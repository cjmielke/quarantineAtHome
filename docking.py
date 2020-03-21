import glob
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
# ideas : https://stackoverflow.com/questions/18344932/python-subprocess-call-stdout-to-file-stderr-to-file-display-stderr-on-scree

def runAutogrid(cwd=None):
	mglPath = os.path.join(os.getcwd(), 'mgltools_x86_64Linux2_1.5.6')
	scriptPath = os.path.join(mglPath, 'MGLToolsPckgs/AutoDockTools/Utilities24/prepare_gpf4.py')
	if not os.path.exists(scriptPath):
		raise ValueError('prepare_gpf4 script is missing : '+scriptPath)
	prepCmd = [
		#'./mgltools_x86_64Linux2_1.5.6/MGLToolsPckgs/AutoDockTools/Utilities24/prepare_gpf.py',
		scriptPath,
		'-i', 'template.gpf',		# primarily needed to save the gridbox information .... unique for each receptor
		'-l', 'ligand.pdbqt',
		'-r', 'receptor.pdbqt',
		'-o', 'autogrid.gpf'
	]
	check_call(prepCmd, cwd=cwd, env={'PATH': '/mgltools_x86_64Linux2_1.5.6/bin'})
	# ENV PATH="/mgltools_x86_64Linux2_1.5.6/bin:${PATH}"
	autogridCmd = [ 'autogrid4', '-p', 'autogrid.gpf', '-l', 'autogrid.log' ]

	fo = open("stdout.txt", "w")
	fe = open("stderr.txt", "w")
	ret = check_call(autogridCmd, cwd=cwd, stdout=fo, stderr=fe)

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
	check_call(prepCmd, cwd=cwd, env={'PATH': '/mgltools_x86_64Linux2_1.5.6/bin'})


	logFile = os.path.join(cwd, 'dock.dlg')
	if os.path.exists(logFile): os.remove(logFile)


	# later we will probably implement an API where the server indicates a preference for which docking algorithm to run
	# for now, just checking if the compiled GPU version of autodock is available is sufficient
	gpuBins = glob.glob('/AutoDock-GPU/bin/autodock_gpu_*')
	if len(gpuBins) and os.path.exists(gpuBins[0]):
		# /AutoDock-GPU/bin/autodock_gpu_32wi -ffile chainE.maps.fld -lfile DCABRM.xaa_ligand_200.pdbqt -nrun 100
		cmd = [ gpuBins[0], '-ffile', 'receptor.maps.fld', '-lfile', 'ligand.pdbqt', '-nrun', '100' ]
		algo = 'AD-gpu'
	else:
		#cmd = [ 'autodock4', '-p', 'autodock.dpf', '-l', 'dock.dlg' ]
		cmd = [ 'autodock4', '-p', 'autodock.dpf']
		algo = 'AD4'

	ret = check_call(cmd, cwd=cwd, stdout=open(logFile, 'w'))

	results = parseLogfile(logFile)
	results['algo']=algo
	return results


# FIXME - parse the inhibiion constant (in millimolar, micromolar, nanomolar, etc) and standardize
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


if __name__ == '__main__':
	dir = os.path.join(os.getcwd(), 'receptors/mpro-1/')
	print dir
	#runAutogrid(cwd=dir)
	runAutodock(cwd=dir)
	#parseLogfile('docking.dlg')
	#parseLogfile('dock2.dlg')


