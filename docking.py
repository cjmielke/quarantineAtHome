import gzip
import os
import re
from subprocess import check_call

import numpy as np
import requests
import json



def runAutogrid():


	autogridCmd = [
		'autogrid4', '-p', 'Mpro.gpf', '-l', 'autogrid.log'
	]
	ret = check_call(autogridCmd, cwd='/docking/')

	# check_call uses Popen args
	'''
	def __init__(self, args, bufsize=0, executable=None,
				 stdin=None, stdout=None, stderr=None,
				 preexec_fn=None, close_fds=False, shell=False,
				 cwd=None, env=None, universal_newlines=False,
				 startupinfo=None, creationflags=0):
	'''


def runAutodock():


	cmd = [
		'autodock4', '-p', 'Mpro.dpf', '-l', 'dock.dlg'
	]
	ret = check_call(cmd, cwd='/docking/')





def parseLogfile(fileName):
	energyRE = re.compile(r'= {2,3}([-+\d.]*) kcal\/mol')
	with open(fileName) as fh:
		firstLine = fh.readline()

		bindingEnergies = []

		for line in fh:
			if 'REMARK' in line and 'ZINC' in line:
				zincID = line.split(' ')[-1].strip()
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
			meanBindingEnergy = bindingEnergies.mean(), minBindingEnergy = bindingEnergies.min(),
			zincID = zincID
		)

		return results

if __name__ == '__main__':
	#runAutogrid()
	runAutodock()
	#parseLogfile('docking.dlg')
	#parseLogfile('dock2.dlg')


