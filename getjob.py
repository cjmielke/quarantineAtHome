import gzip
import os

import requests
import json

SERVER = 'http://127.0.0.1:5001'


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
		req = requests.get(url)
		j = json.loads(req.text)
		return j

	def nextTranche(self):
		j = self._get('/tranche/get')
		Tn = j['tranche']
		return Tn

	def nextModel(self, trancheName):
		j = self._get('/tranches/%s/nextmodel' % trancheName)
		return j['model']

	def reportResults(self, userName, modelName, zincID, bestDeltaG, bestKi):
		url = self.server + '/submitresults'
		headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
		data = dict(user=userName)
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

		return zincID, lines



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





for n in range(0, 4):
	modelNum = client.nextModel(tranche)
	print 'Server told us to work on model ', modelNum
	zincID, model = TR.getModel(modelNum)


	# run the docking


def jobLoop():

	# contact server for a tranche assignment

	# contact server for a model assignment

	# inner loop - which ligand models from this tranche file should we execute?
	while True:
		# get model number from server
		modelNum = client.nextModel(tranche)					# ask server which ligand model number to execute
		print 'Server told us to work on model ', modelNum
		zincID, model = TR.getModel(modelNum)					# parse out of Tranche file





