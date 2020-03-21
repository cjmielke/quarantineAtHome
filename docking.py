import os
import re
from subprocess import check_call

import numpy as np

# check_call uses Popen args
'''
def __init__(self, args, bufsize=0, executable=None,
			 stdin=None, stdout=None, stderr=None,
			 preexec_fn=None, close_fds=False, shell=False,
			 cwd=None, env=None, universal_newlines=False,
			 startupinfo=None, creationflags=0):
'''

# FIXME - we need to figure out clever ways of capturing stdout of autodock and autogrid
# FIXME - could null-route it, but would be better to condense status so the user knows something is happening

def runAutogrid(cwd=None):
	mglPath = os.path.join(os.getcwd(), 'mgltools_x86_64Linux2_1.5.6')
	prepCmd = [
		#'./mgltools_x86_64Linux2_1.5.6/MGLToolsPckgs/AutoDockTools/Utilities24/prepare_gpf.py',
		os.path.join(mglPath, 'MGLToolsPckgs/AutoDockTools/Utilities24/prepare_gpf4.py'),
		'-i', 'template.gpf',		# primarily needed to save the gridbox information .... unique for each receptor
		'-l', 'ligand.pdbqt',
		'-r', 'receptor.pdbqt',
		'-o', 'autogrid.gpf'
	]
	check_call(prepCmd, cwd=cwd)

	autogridCmd = [ 'autogrid4', '-p', 'autogrid.gpf', '-l', 'autogrid.log' ]
	ret = check_call(autogridCmd, cwd=cwd)

def runAutodock(cwd=None):
	if not cwd: cwd=os.getcwd()

	mglPath = os.path.join(os.getcwd(), 'mgltools_x86_64Linux2_1.5.6')
	prepCmd = [
		#'./mgltools_x86_64Linux2_1.5.6/MGLToolsPckgs/AutoDockTools/Utilities24/prepare_gpf.py',
		os.path.join(mglPath, 'MGLToolsPckgs/AutoDockTools/Utilities24/prepare_dpf4.py'),
		#'-i', 'template.dpf',		# might re-enable this to set certain desired algorithm parameters for each system ....
		'-l', 'ligand.pdbqt',
		'-r', 'receptor.pdbqt',
		'-o', 'autodock.dpf'
	]
	check_call(prepCmd, cwd=cwd)

	cmd = [ 'autodock4', '-p', 'autodock.dpf', '-l', 'dock.dlg' ]
	ret = check_call(cmd, cwd=cwd)

	lf = os.path.join(cwd, 'dock.dlg')
	results = parseLogfile(lf)
	return results


# FIXME - parse the inhibiion constant (in millimolar, micromolar, nanomolar, etc) and standardize
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
			meanDG = bindingEnergies.mean(),
			bestDG = bindingEnergies.min(),
			zincID = zincID
		)

		return results


if __name__ == '__main__':
	dir = os.path.join(os.getcwd(), 'receptors/mpro-1/')
	print dir
	#runAutogrid(cwd=dir)
	runAutodock(cwd=dir)
	#parseLogfile('docking.dlg')
	#parseLogfile('dock2.dlg')


