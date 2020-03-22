import gzip
import json
import os
from subprocess import check_call

import requests
from urllib3 import Retry

from settings import SERVER, API_V, PRODUCTION_SERVER, TRANCHE_DOWNLOAD_LOCATION

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

import logging
import requests

from requests.adapters import HTTPAdapter
#from requests.packages.urllib3.util.retry import Retry

logging.basicConfig(level=logging.DEBUG)


class API():						# API client for talking to server
	def __init__(self, username, dev=None):
		self.username = username

		if dev is not None:
			self.server = SERVER
		else:
			self.server = PRODUCTION_SERVER

		self.apiPath = self.server + '/api/'+API_V

		# implementation found from : https://stackoverflow.com/questions/23267409/how-to-implement-retry-mechanism-into-python-requests-library
		self.session = requests.Session()
		# nginx will conveniently return a 502 if the flask server goes down

		methods = frozenset(["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"] )
		retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504], method_whitelist=methods)
		self.session.mount('https://', HTTPAdapter(max_retries=retries))

		#self.session.get("http://httpstat.us/503")

	def _get(self, path):
		url = self.apiPath+path
		print 'trying new retry session! ', url
		#req = requests.get(url, timeout=5)
		req = self.session.get(url, timeout=5)
		j = json.loads(req.text)
		return j

	def nextTranche(self):
		j = self._get('/tranche/get')
		return j['id'], j['tranche']

	def nextLigand(self, trancheID):
		j = self._get('/tranches/%s/nextligand' % trancheID)
		return j['ligand'], j['receptors']

	def reportResults(self, data):
		data['user'] = self.username
		url = self.apiPath + '/submitresults'
		print url
		headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
		#resp = requests.post(url, data=json.dumps(data), headers=headers)
		#resp = self.session.post(url, data=json.dumps(data), headers=headers, timeout=5)
		resp = self.session.post(url, json=data, timeout=5)
		print resp


class TrancheReader():					# for fetchng/parsing tranche file
	def __init__(self, trancheID, tranchePath):
		self.trancheID = trancheID
		self.tranchePath = tranchePath				# as in, the url path on files.docker.org
		self.currentModel = 0
		self.trancheFile = None
		self.download()
		self.fh = gzip.open(self.trancheFile)

	# FIXME - really should download tranche files into a local path ....
	def download(self):
		Tn = self.tranchePath
		#trancheUrl = 'http://files.docking.org/3D/%s/%s/%s' % (Tn[0:2], Tn[2:6], Tn)
		trancheUrl = 'http://files.docking.org/' + self.tranchePath
		print trancheUrl
		# TRANCHE_FILE = 'tranche.pdbqt.gz'
		#trancheFilename = Tn
		urlParts = self.tranchePath.split('/')

		localPath = os.path.join(TRANCHE_DOWNLOAD_LOCATION, *urlParts[:-1])
		os.makedirs(localPath)
		trancheFilename = urlParts[-1]
		self.trancheFile = os.path.join(localPath, trancheFilename)

		if not os.path.exists(self.trancheFile):
			Tfile = requests.get(trancheUrl)
			with open(self.trancheFile, 'wb') as fh:
				fh.write(Tfile.content)
		else:
			print 'already have tranche file'

		return

	def getModel(self, modelNum):

		if modelNum < self.currentModel:			# reload tranche modelfile if the server is requesting a ligand we've already passed
			self.fh = gzip.open(self.tranchePath)

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


		#with open('ligand.pdbqt', 'w') as lf:
		#	lf.write('\n'.join(lines))

		return zincID, '\n'.join(lines)


	def saveModel(self, model, outfile='ligand.pdbqt'):
		with open(outfile, 'w') as lf:
			lf.write(model)



def test():
	client = API('testUser', dev=True)
	trancheID, tranche = client.nextTranche()

	TR = TrancheReader(trancheID, tranche)

	for n in range(0, 4):
		ligandNumber, receptors = client.nextLigand(tranche)
		print 'Server told us to work on ligand ', ligandNumber, receptors
		zincID, model = TR.getModel(ligandNumber)


def testSubmit():
	client = API('testUser', dev=True)
	results = dict(
		username='cosmo',
		bestDG=-10.0,
		bestKi=10e-6,
		receptor='spike',
		algo='autodock4',
		zincID='ZINC000130'
	)
	results['test'] = 1					# server will not save in DB
	client.reportResults(results)


if __name__ == '__main__':
	test()
	testSubmit()
	#updateReceptors()



