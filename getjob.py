import gzip
import os
import time
from random import shuffle
from subprocess import check_call

import requests
import json

from docking import runAutodock, parseLogfile
from settings import SERVER, RECEPTORS_DIR

'''
On tranches stored in Zinc :

First two letters are logP and molecular weight

The third letter is reactivity : A=anodyne. B=Bother (e.g. chromophores) C=clean (but pains ok), E=mild reactivity ok, G=reactive ok, I = hot chemistry ok
The fourth letter is purchasability: A and B = in stock, C = in stock via agent, D = make on demand, E = boutique (expensive), F=annotated (not for sale)
The fifth letter is pH range: R = ref (7.4), M = mid (near 7.4), L = low (around 6.4), H=high (around 8.4).
The sixth and last dimension is net molecular charge. Here we follow the convention of InChIkeys. Thus. N = neutral, M = minus 1, L = minus 2 (or greater). O = plus 1, P = plus 2 (or greater).

We probably want ?? [AB] [AB] [RM] [*]

'''


'''
JSON posting notes
url = "http://localhost:8080"  
data = {'sender': 'Alice', 'receiver': 'Bob', 'message':'We did it!'}
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
r = requests.post(url, data=json.dumps(data), headers=headers)

'''



class API():						# API client for talking to server
	def __init__(self):
		self.server = SERVER


	def _get(self, path):
		url = self.server+path
		req = requests.get(url, timeout=5)
		j = json.loads(req.text)
		return j

	def nextTranche(self):
		j = self._get('/tranche/get')
		Tn = j['tranche']
		return Tn

	def nextLigand(self, trancheName):
		j = self._get('/tranches/%s/nextligand' % trancheName)
		return j['ligand']

	def reportResults(self, data):
		url = self.server + '/submitresults'
		headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
		resp = requests.post(url, data=json.dumps(data), headers=headers)
		print resp



class TrancheReader():					# for fetchng/parsing tranche file
	def __init__(self, trancheName):
		self.name = trancheName
		self.download()
		self.fh = gzip.open(self.name)
		self.currentModel = 0

	def download(self):
		Tn = self.name
		trancheUrl = 'http://files.docking.org/3D/%s/%s/%s' % (Tn[0:2], Tn[2:6], Tn)
		print trancheUrl
		# TRANCHE_FILE = 'tranche.pdbqt.gz'
		trancheFilename = Tn
		if not os.path.exists(trancheFilename):
			Tfile = requests.get(trancheUrl)
			with open(trancheFilename, 'wb') as fh:
				fh.write(Tfile.content)
		else:
			print 'already have tranche file'

		return

	def getModel(self, modelNum):

		zincID = None
		lines = []
		for line in self.fh:
			if line.startswith('MODEL'):
				self.currentModel = int(line.replace('MODEL', '').strip().rstrip())
				if self.currentModel > modelNum: break
			if line.startswith('REMARK'):
				if 'Name' in line:
					zincID = line.replace('REMARK', '').replace('Name', '').replace('=', '').strip()
			if self.currentModel == modelNum: lines.append(line.rstrip('\n'))
		if len(lines) == 0:
			raise ValueError('Tranche is out of Models')


		with open('ligand.pdbqt', 'w') as lf:
			lf.write('\n'.join(lines))

		return zincID, '\n'.join(lines)

	def saveModel(self, model, outfile='ligand.pdbqt'):
		with open(outfile, 'w') as lf:
			lf.write(model)


# construct expected URL for this tranche



# now the tranche file is downloaded to this local worker
# open it as a compressed stream

'''
for line in fh:
	line = line.rstrip()
	print line, fh.offset
'''

client = API()
tranche = client.nextTranche()

TR = TrancheReader(tranche)






def updateReceptors():
	cmd = [
		'git', 'clone', 'https://github.com/cjmielke/quarantine-receptors', RECEPTORS_DIR
	]
	cmd = [
		'git', 'pull'
	]

	ret=check_call(cmd)
	cmd = [
		'pwd'
	]

	ret=check_call(cmd)




'''
The primary loop for the client ....

To minimize bandwidth requirements on the UCSF Zinc database, clients will download single tranche files,
and generally stick with them for lengthy periods of time. Thus, the outer loop is a request to the server of 
which tranche file should be processed.



'''
cmd = [
	'git', 'pull'
]

ret = check_call(cmd)


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
				TR.saveModel(model, outfile=os.path.join(dir, 'ligand.pdbqt'))
				results = runAutodock(cwd=dir)
				#parseLogfile(os.path.join(dir, 'log.dlg'))

			#print 'running docking algorithm'
			#time.sleep(4)


def test():
	for n in range(0, 4):
		modelNum = client.nextLigand(tranche)
		print 'Server told us to work on model ', modelNum
		zincID, model = TR.getModel(modelNum)


def testSubmit():
	client = API()
	results = dict(
		username='cosmo',
		bestDG=-10.0,
		bestKi=10e-6,
		receptor='spike'
	)
	client.reportResults(results)


if __name__ == '__main__':
	#test()

	#testSubmit()
	#updateReceptors()
	jobLoop()



