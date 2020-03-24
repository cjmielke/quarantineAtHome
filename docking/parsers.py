import re

import numpy as np
import gzip
import shutil


def compressFile(fileName):
	with open(fileName, 'rb') as f_in:
		gz_ = fileName + '.gz'
		with gzip.open(gz_, 'wb') as f_out:
			shutil.copyfileobj(f_in, f_out)

	return gz_


def parseLogfile(fileName):
	energyRE = re.compile(r'= {2,3}([-+\d.]*) kcal\/mol')
	zincRE = re.compile(r'.*(ZINC[\d]*).*')

	with open(fileName) as fh:
		firstLine = fh.readline()

		bindingEnergies = []

		for line in fh:
			if 'REMARK' in line and 'ZINC' in line:
				#zincID = line.split(' ')[-1].strip()
				zincID = zincRE.findall(line)[0]
				#print line, zincID
			if 'Estimated Free Energy of Binding' in line:
				# for m in energyRE.findall(line):
				#	print m
				bindingEnergy = float(energyRE.findall(line)[0])
				bindingEnergies.append(bindingEnergy)
		'''
		if 'AutoDock-GPU' in firstLine:		# GPU version makes slightly different logfiles
				pass
		else:
			for line in fh:
				pass
		'''

		bindingEnergies = np.asarray(bindingEnergies)
		print zincID
		print 'binding energy mean : ', bindingEnergies.mean()
		print 'binding energy min : ', bindingEnergies.min()

		results = dict(
			meanDG = bindingEnergies.mean(),
			bestDG = bindingEnergies.min(),
			zincID = zincID
		)

		return results