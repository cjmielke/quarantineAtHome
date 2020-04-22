import os

import requests

from settings import RECEPTORS_DIR, getwd

'''
# FIXME - write receptor download code
#dir = os.path.join(os.getcwd(), 'receptors', receptor)
dir = os.path.join(getwd(), 'receptors', receptor)
if not os.path.exists(dir):			# if a new receptor has been deployed, but we don't have it, stop the client and run git-pull
	raise ValueError("Don't have this receptor definition yet   ", dir)
	#sys.exit(1)

'''

# TODO - build in backoff logic and retries
# TODO - figure out how often we want to initiate this update
def downloadFile(src, dest, replace=True):
	if dest is None or dest == '':
		#dest = os.path.join(getwd(), src.split('/')[-1])
		dest = src.split('/')[-1]               # src is just a web path - get filename

	dest = os.path.join(getwd(), dest)

	if not replace and os.path.exists(dest):
		print 'already have ', dest

	R = requests.get(src)
	with open(dest, 'wb') as fh:
		fh.write(R.content)


# handles downloading of receptor systems if we don't yet have them
class Receptor():
	def __init__(self, name):
		self.name = name

		self.dir = os.path.join (RECEPTORS_DIR, self.name)

		exists = os.path.exists(self.dir)
		if not exists:                        # FIXME - should check existence of each required file ....
			self.download()

	def download(self):
		mirror = 'https://cjmielke.github.io/quarantine-files/'

		if not os.path.exists(self.dir): os.makedirs(self.dir)

		# to run jobs we need the receptor structure file and the grid parameter template file
		for fn in ['receptor.pdbqt', 'template.gpf']:
			src = '%s/receptors/%s/%s' % (mirror, self.name, fn)
			dest = os.path.join(RECEPTORS_DIR, self.name, fn)
			downloadFile(src, dest)



