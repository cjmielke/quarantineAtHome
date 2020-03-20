import argparse
import os
import sys
import time
from random import shuffle

from docking import runAutodock
from getjob import API, updateReceptors, TrancheReader

parser = argparse.ArgumentParser()
parser.parse_args()



def jobLoop():
	client = API()

	while True:
		updateReceptors()					# make sure we have all the receptors we need

		tranche = client.nextTranche()		# contact server for a tranche assignment
		TR = TrancheReader(tranche)			# then download and open this tranche for reading

		# contact server for a model assignment (lets hardcode for now)
		receptors = ['mpro-1']
		shuffle(receptors)

		# inner loop - which ligand models from this tranche file should we execute?
		while True:
			# get model number from server
			modelNum = client.nextLigand(tranche)					# ask server which ligand model number to execute
			print 'Server told us to work on model ', modelNum
			zincID, model = TR.getModel(modelNum)					# parse out of Tranche file

			for receptor in receptors:
				print 'running docking algorithm on ', receptor
				dir = os.path.join(os.getcwd(), 'receptors', receptor)

				if not os.path.exists(dir):
					# if a new receptor model has been deployed, this client's code may be out of date
					# exit, and let the bash script run a git pull, and rerun the python script
					sys.exit(1)

				TR.saveModel(model, outfile=os.path.join(dir, 'ligand.pdbqt'))
				results = runAutodock(cwd=dir)
				#parseLogfile(os.path.join(dir, 'log.dlg'))

			#print 'running docking algorithm'
			#time.sleep(4)


if __name__ == '__main__':
	jobLoop()


	while True:
		print 'running job'
		time.sleep(5)
		sys.exit()



