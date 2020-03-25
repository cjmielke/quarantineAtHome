import argparse
import logging
import multiprocessing	# maybe should be using Ray, maybe Celery
import os
import Queue
import sys
import tempfile
import time
from random import shuffle
import glob

from docking.autodock import runAutodock, prepDPFshell
from docking.autogrid import runAutogrid
from getjob import API, TrancheReader

parser = argparse.ArgumentParser()
parser.parse_args()

from raven import Client

client = Client('https://95200bce44ef41ae828324e243dc3240:4d2b75ff840d434490a507511340c7f7@bugs.infino.me/6')
sentry_errors_log = logging.getLogger("sentry.errors")
sentry_errors_log.addHandler(logging.StreamHandler())




#!/usr/bin/env python
import signal
import sys

def signal_handler(sig, frame):
	print('You pressed Ctrl+C!')
	sys.exit(13)
signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C')
#signal.pause()

def isGPU():
	gpuBins = glob.glob('/AutoDock-GPU/bin/autodock_gpu_*')
	if len(gpuBins) and os.path.exists(gpuBins[0]):
		return True
	else:
		return False

'''
try:
	1 / 0
except ZeroDivisionError:
	client.captureException()
'''


'''
The primary loop for the client ....

To minimize bandwidth requirements on the UCSF Zinc database, clients will download single tranche files,
and generally stick with them for lengthy periods of time. Thus, the outer loop is a request to the server of 
which tranche file should be processed.
'''


devmode = os.getenv('DEBUG')		# if set, enters developer mode (contacts local server
USERNAME = os.getenv('ME')		# if set, enters developer mode (contacts local server

jobs_to_cache = 5
cpu_count = multiprocessing.cpu_count() / 2 # assume hyperthreading so ignore half the logical cores
gpu_count = 1 # assuming one GPU job at a time, use nvidia-smi to see if you have <100% utilization
POISON_PILL = "STOP"

def fetchLoop(work_new):
	print("Fetch worker started")
	client = API(USERNAME, dev=devmode)

	while True:

		while work_new.qsize > jobs_to_cache:		# Puts the breaks on execution
			time.sleep(1)

		trancheID, tranche = client.nextTranche()		# contact server for a tranche assignment
		TR = TrancheReader(trancheID, tranche, mirror=client.mirror)			# then download and open this tranche for reading

		# inner loop - which ligand models from this tranche file should we execute?
		while True:
			# get model number from server
			ligandNum, receptors = client.nextLigand(trancheID)					# ask server which ligand model number to execute
			print 'Server told us to work on model ', ligandNum

			try: zincID, model = TR.getModel(ligandNum)					# parse out of Tranche file
			except StopIteration:
				client.trancheEOF(trancheID)
				break

			for receptor in receptors:
				print 'queueing docking algorithm on ', receptor

				# Creating a temporary directory per job
				dir = tempfile.TemporaryDirectory()
				work_new.put(dir)
				#dir = os.path.join(os.getcwd(), 'receptors', receptor)

				if not os.path.exists(dir):			# if a new receptor has been deployed, but we don't have it, stop the client and run git-pull
					raise ValueError("Don't have this receptor definition yet")
					#sys.exit(1)

				TR.saveModel(model, outfile=os.path.join(dir, 'ligand.pdbqt'))
				sys.stdout.flush()
	return

# Run one of these per physical core
def cpuLoop(work_new, work_gpu):
	print("CPU worker started")
	while True:

		while work_new.empty() or work_gpu.qsize() > jobs_to_cache:
			time.sleep(1)

		dir = work_new.get()
		start = time.time()
		# Tasks that run on the CPU
		runAutogrid(cwd=dir)
		prepDPFshell(cwd=dir)

		# Tasks that may run on the GPU
		if not isGPU():
			print 'running docking algorithm on CPU in ', dir
			results, logFile = runAutodock(cwd=dir)
			end = time.time()
			results['time'] = end - start
			results['receptor'] = receptor
			results['tranche'] = trancheID
			results['ligand'] = ligandNum

			# FIXME - different autodock versions have different logfile formats - some don't export ligand name

			client.reportResults(results, logFile)
		else:
			work_gpu.put(dir)	# hand work over to GPU
		sys.stdout.flush()
	return

# Only run if GPU version and probably only use one
def gpuLoop(work_gpu):
	print("GPU worker started")
	while True:
		while work_gpu.empty():
			time.sleep(0.2)

		dir = work_gpu.get()

		start = time.time()
		print 'running docking algorithm on GPU in ', dir
		results, logFile = runAutodock(cwd=dir)
		end = time.time()
		results['time'] = end - start
		results['receptor'] = receptor
		results['tranche'] = trancheID
		results['ligand'] = ligandNum

		# FIXME - different autodock versions have different logfile formats - some don't export ligand name

		client.reportResults(results, logFile)
		sys.stdout.flush()
	return

def dispatchCenter():
	# create a manager - it lets us share native Python object types like
	# lists and dictionaries without worrying about synchronization -
	# the manager will take care of it
	manager = multiprocessing.Manager()

	# now using the manager, create our shared data structures
	work_new = manager.Queue()
	work_gpu = manager.Queue()

	if not isGPU():
		worker_count = 1 + cpu_count
	else: # is GPU
		worker_count = 2 # no need for overkill, one fetch and one cpu for unpack
	print "CPU workers count = " + str(cpu_count)
	pool_cpu = multiprocessing.Pool(processes=worker_count)

	# Loops getting stuck, trying this approach https://stackoverflow.com/questions/29571671/basic-multiprocessing-with-while-loop
	if isGPU():
		print("Starting GPU workers")
		pool_gpu = multiprocessing.Pool(processes=1)
		gpu_res = pool_gpu.apply_async(func=gpuLoop, args=(work_gpu))
		print("Starting CPU workers")
		pool_cpu = multiprocessing.Pool(processes=1)
		cpu_res = pool_cpu.apply_async(func=cpuLoop, args=(work_new, work_gpu))
	else:
		print("Starting CPU workers")
		pool_cpu = multiprocessing.Pool(processes=cpu_count)
		cpu_res = pool_cpu.apply_async(func=cpuLoop, args=(work_new, work_gpu))

	print("Starting fetching process")
	fetchLoop(work_new)
	pool_gpu.close()
	pool_cpu.close()
	pool_gpu.join()
	pool_cpu.close()

	return

if __name__ == '__main__':
	dispatchCenter()



