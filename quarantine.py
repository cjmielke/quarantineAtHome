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
import shutil

from docking.autodock import runAutodock, prepDPFshell
from docking.autogrid import runAutogrid
from getjob import API, TrancheReader

parser = argparse.ArgumentParser()
parser.parse_args()

from raven import Client

client = Client('https://95200bce44ef41ae828324e243dc3240:4d2b75ff840d434490a507511340c7f7@bugs.infino.me/6')
sentry_errors_log = logging.getLogger("sentry.errors")
sentry_errors_log.addHandler(logging.StreamHandler())

# Currently designed to be CPU or GPU centric processing, so you can launch one container of each type.
# TODO maybe change autodock.py to allow using all CPUs + GPUs
# Issue with multiprocessing and check_call worked around using this approach
# https://gist.github.com/ownport/63167dbb162f998964f309a5046bef58

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

cpu_count = multiprocessing.cpu_count() / 2 # assume hyperthreading so ignore half the logical cores
gpu_count = 1 # assuming one GPU job at a time, use nvidia-smi to see if you have <100% utilization
jobs_to_cache = cpu_count # have one job per core available, or 3-5 jobs if GPU running
POISON_PILL = "STOP"

def fetchLoop(work_new):
	print("Fetch worker started")
	client = API(USERNAME, dev=devmode)

	while True:

		trancheID, tranche = client.nextTranche()		# contact server for a tranche assignment
		TR = TrancheReader(trancheID, tranche, mirror=client.mirror)			# then download and open this tranche for reading

		# inner loop - which ligand models from this tranche file should we execute?
		while True:
			while work_new.qsize() > jobs_to_cache:  # Puts the breaks on execution
				time.sleep(1)
			# get model number from server
			ligandNum, receptors = client.nextLigand(trancheID)					# ask server which ligand model number to execute
			print('Server told us to work on model '+str(ligandNum))

			try: zincID, model = TR.getModel(ligandNum)					# parse out of Tranche file
			except StopIteration:
				client.trancheEOF(trancheID)
				break

			for receptor in receptors:
				print('queueing docking algorithm on '+str(receptor))

				# Creating a temporary directory per job
				dir = tempfile.mkdtemp() # .TemporaryDirectory()
				work_new.put([dir, receptor, trancheID, ligandNum, client])
				#dir = os.path.join(os.getcwd(), 'receptors', receptor)

				if not os.path.exists(dir):			# if a new receptor has been deployed, but we don't have it, stop the client and run git-pull
					raise ValueError("Creating temporary file failed")
					#sys.exit(1)

				# Need to copy receptor file
				receptor_dir = os.path.join(os.getcwd(), 'receptors', receptor)
				if not os.path.exists(receptor_dir):  # if a new receptor has been deployed, but we don't have it, stop the client and run git-pull
					raise ValueError("Don't have this receptor definition yet")
					# sys.exit(1)
				print("Copying "+receptor_dir+" to "+dir)
				try:
					#shutil.copytree(receptor_dir, dir)
					shutil.copy(receptor_dir+'/template.gpf', dir)
					shutil.copy(receptor_dir+'/receptor.pdbqt', dir)
				except OSError:
					pass
				#check_call([ls, dir])

				TR.saveModel(model, outfile=os.path.join(dir, 'ligand.pdbqt'))
				sys.stdout.flush()	# make sure child processes print
			time.sleep(0.5) # slow down to help syncing, server
	return

class CpuConsumer(multiprocessing.Process):
	def __init__(self, work_new, work_gpu):
		multiprocessing.Process.__init__(self)
		self.work_new = work_new
		self.work_gpu = work_gpu

	# Run one of these per physical core
	def run(self):
		proc_name = self.name
		print("CPU worker started")
		while True:
			while self.work_new.empty() or self.work_gpu.qsize() > jobs_to_cache:
				time.sleep(1)
			dir, receptor, trancheID, ligandNum, client = self.work_new.get()
			if dir is POISON_PILL: # poison pill to exit
				print('CPU {}: CPU exiting'.format(proc_name))
				self.work_new.task_done()
				break
			print('CPU {}: {}'.format(proc_name, dir))
			start = time.time()
			# Tasks that run on the CPU
			runAutogrid(cwd=dir)
			prepDPFshell(cwd=dir)

			# Tasks that may run on the GPU
			if not isGPU():
				print('running docking algorithm on CPU in '+str(dir))
				results, logFile = runAutodock(cwd=dir)
				end = time.time()
				results['time'] = end - start
				results['receptor'] = receptor
				results['tranche'] = trancheID
				results['ligand'] = ligandNum

				# FIXME - different autodock versions have different logfile formats - some don't export ligand name

				client.reportResults(results, logFile)
				shutil.rmtree(dir) # hack to remove temporaryDirectory w/o context (https://stackoverflow.com/questions/6884991/how-to-delete-a-directory-created-with-tempfile-mkdtemp)
			else:
				self.work_gpu.put(dir)	# hand work over to GPU
			self.work_new.task_done()
			sys.stdout.flush()
			print('CPU work_new='+str(self.work_new.qsize())+' GPU work_gpu='+str(self.work_gpu.qsize()))
		return

# Only run if GPU version and probably only use one
class GpuConsumer(multiprocessing.Process):
	def __init__(self, work_gpu):
		multiprocessing.Process.__init__(self)
		self.work_gpu = work_gpu

	# Run one of these per physical core
	def run(self):
		proc_name = self.name
		print("GPU worker started")
		while True:
			while self.work_gpu.empty():
				time.sleep(0.2)
			dir, receptor, trancheID, ligandNum, client = work_gpu.get()
			if dir is POISON_PILL: # poison pill to exit
				print('GPU {}: GPU exiting'.format(proc_name))
				self.work_gpu.task_done()
				break
			print('GPU {}: {}'.format(proc_name, dir))
			start = time.time()
			print('running docking algorithm on GPU in '+str(dir))
			results, logFile = runAutodock(cwd=dir)
			end = time.time()
			results['time'] = end - start
			results['receptor'] = receptor
			results['tranche'] = trancheID
			results['ligand'] = ligandNum

			# FIXME - different autodock versions have different logfile formats - some don't export ligand name

			client.reportResults(results, logFile)
			shutil.rmtree(dir)

			self.work_gpu.task_done()
			sys.stdout.flush()
		return

def dispatchCenter():
	work_new = multiprocessing.JoinableQueue()
	work_gpu = multiprocessing.JoinableQueue()

	if not isGPU():
		worker_count = cpu_count
	else: # is GPU
		worker_count = 1 # no need for overkill, one cpu for unpack
		jobs_to_cache = 3 # probably enough buffering to keep GPU fed, else up to 5
	print("CPU workers count = "+str(cpu_count))

	# Loops getting stuck, trying this approach https://stackoverflow.com/questions/29571671/basic-multiprocessing-with-while-loop
	if isGPU():
		cpu_consumers = [
			CpuConsumer(work_new, work_gpu)
			for i in range(worker_count)
		]
		for cw in cpu_consumers:
			cw.start()
		gpu_consumers = [
			GpuConsumer(work_gpu)
			for i in range(gpu_count)
		]
		for gw in gpu_consumers:
			gw.start()
	else:
		cpu_consumers = [
			CpuConsumer(work_new, work_gpu)
			for i in range(worker_count)
		]
		for cw in cpu_consumers:
			cw.start()

	print("Starting fetching process")
	fetchLoop(work_new)
	for i in range(worker_count):
		work_new.put(POISON_PILL)
	work_new.join()
	if isGPU():
		for i in range(gpu_count):
			work_gpu.put(POISON_PILL)
		work_gpu.join()

	return

if __name__ == '__main__':
	dispatchCenter()



