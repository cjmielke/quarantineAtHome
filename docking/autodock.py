import glob
import os
from subprocess import check_call

from docking.parsers import parseLogfile
from docking.prepareDPF import prepDPF

#prepDPF(cwd)
from settings import MGL_PATH


def prepDPFshell(cwd):
	prepCmd = [
		#'./mgltools_x86_64Linux2_1.5.6/MGLToolsPckgs/AutoDockTools/Utilities24/prepare_gpf.py',
		os.path.join(MGL_PATH, 'MGLToolsPckgs/AutoDockTools/Utilities24/prepare_dpf4.py'),
		#'-i', 'template.dpf',		# might re-enable this to set certain desired algorithm parameters for each system ....
		'-l', 'ligand.pdbqt',
		'-r', 'receptor.pdbqt',
		'-o', 'autodock.dpf'
	]
	paths = ':'.join([
		os.path.join(os.getcwd(), 'mgltools_x86_64Linux2_1.5.6/MGLToolsPckgs/'),
		os.path.join(os.getcwd(), 'mgltools_x86_64Linux2_1.5.6/lib/python2.5/site-packages/')
	])
	env = {
		#'PATH': '/mgltools_x86_64Linux2_1.5.6/bin',				# docker
		'PATH': os.path.join(os.getcwd(), 'mgltools_x86_64Linux2_1.5.6/bin'),
		#'PYTHON' : 'mgltools_x86_64Linux2_1.5.6/bin/python',
		#'PYTHONHOME': os.path.join(os.getcwd(), 'mgltools_x86_64Linux2_1.5.6/lib/'),
		'PYTHONPATH': paths
	}
	check_call(prepCmd, cwd=cwd, env=env)


def runAutodock(cwd=None):
	if not cwd: cwd=os.getcwd()

	#prepDPF(cwd)
	prepDPFshell(cwd)


	logFile = os.path.join(cwd, 'docking.dlg')				# note - autodock-gpu always uses this filename, so we adopt it
	if os.path.exists(logFile): os.remove(logFile)


	# later we will probably implement an API where the server indicates a preference for which docking algorithm to run
	# for now, just checking if the compiled GPU version of autodock is available is sufficient
	gpuBins = glob.glob('/AutoDock-GPU/bin/autodock_gpu_*')
	if len(gpuBins) and os.path.exists(gpuBins[0]):
		# /AutoDock-GPU/bin/autodock_gpu_32wi -ffile chainE.maps.fld -lfile DCABRM.xaa_ligand_200.pdbqt -nrun 100
		cmd = [ gpuBins[0], '-ffile', 'receptor.maps.fld', '-lfile', 'ligand.pdbqt', '-nrun', '100' ]
		algo = 'AD-gpu'
	else:
		cmd = [ 'autodock4', '-p', 'autodock.dpf', '-l', 'docking.dlg' ]
		#cmd = [ 'autodock4', '-p', 'autodock.dpf']
		algo = 'AD4'

	#log = open(logFile, 'w')
	ret = check_call(cmd, cwd=cwd)
	#log.close()

	results = parseLogfile(logFile)
	results['algo']=algo

	return results, logFile



