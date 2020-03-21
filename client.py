import argparse
import os
import sys
import time
from random import shuffle

from docking import runAutodock, runAutogrid
from getjob import API, TrancheReader

parser = argparse.ArgumentParser()
parser.parse_args()



'''
The primary loop for the client ....

To minimize bandwidth requirements on the UCSF Zinc database, clients will download single tranche files,
and generally stick with them for lengthy periods of time. Thus, the outer loop is a request to the server of 
which tranche file should be processed.
'''


def jobLoop():
	client = API()

	while True:

		tranche = client.nextTranche()		# contact server for a tranche assignment
		TR = TrancheReader(tranche)			# then download and open this tranche for reading

		# inner loop - which ligand models from this tranche file should we execute?
		while True:
			# get model number from server
			modelNum, receptors = client.nextLigand(tranche)					# ask server which ligand model number to execute
			print 'Server told us to work on model ', modelNum

			try: zincID, model = TR.getModel(modelNum)					# parse out of Tranche file
			except:
				break													# will ask for the next tranche

			for receptor in receptors:
				print 'running docking algorithm on ', receptor
				dir = os.path.join(os.getcwd(), 'receptors', receptor)

				if not os.path.exists(dir):			# if a new receptor has been deployed, but we don't have it, stop the client and run git-pull
					raise ValueError("Don't have this receptor definition yet")
					#sys.exit(1)

				TR.saveModel(model, outfile=os.path.join(dir, 'ligand.pdbqt'))

				start = time.time()
				runAutogrid(cwd=dir)
				results = runAutodock(cwd=dir)
				end = time.time()
				results['time'] = end-start
				results['receptor'] = receptor

				# FIXME - different autodock versions have different logfile formats - some don't export ligand name
				#if

				client.reportResults(results)



if __name__ == '__main__':
	jobLoop()



