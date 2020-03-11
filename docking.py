import gzip
import os
from subprocess import check_call

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


def parseLogfile():
	with open('log.dlg') as fh:
		for line in fh:
			print line


if __name__ == '__main__':
	runAutogrid()
	runAutodock()


