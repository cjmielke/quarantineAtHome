import gzip
import os

import requests
import json

SERVER = 'http://127.0.0.1:5001'





class API():						# API client for talking to server

	def _get(self, path):
		url = SERVER+path
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



