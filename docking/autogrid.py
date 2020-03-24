import os
from subprocess import check_call

from docking.prepareGPF import prepGPF


def prepGPFshell(cwd):

	mglPath = os.path.join(os.getcwd(), 'mgltools_x86_64Linux2_1.5.6')
	scriptPath = os.path.join(mglPath, 'MGLToolsPckgs/AutoDockTools/Utilities24/prepare_gpf4.py')
	if not os.path.exists(scriptPath):
		raise ValueError('prepare_gpf4 script is missing : '+scriptPath)
	interpreter = os.path.join(mglPath, 'bin', 'python2.5')

	prepCmd = [
		#'./mgltools_x86_64Linux2_1.5.6/MGLToolsPckgs/AutoDockTools/Utilities24/prepare_gpf.py',
		interpreter,
		scriptPath,
		'-i', 'template.gpf',		# primarily needed to save the gridbox information .... unique for each receptor
		'-l', 'ligand.pdbqt',
		'-r', 'receptor.pdbqt',
		'-o', 'autogrid.gpf'
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

	return


def runAutogrid(cwd=None):

	#prepGPF(cwd)
	prepGPFshell(cwd)

	# ENV PATH="/mgltools_x86_64Linux2_1.5.6/bin:${PATH}"
	autogridCmd = [ 'autogrid4', '-p', 'autogrid.gpf', '-l', 'autogrid.log' ]

	fo = open("stdout.txt", "w")
	fe = open("stderr.txt", "w")
	ret = check_call(autogridCmd, cwd=cwd, stdout=fo, stderr=fe)