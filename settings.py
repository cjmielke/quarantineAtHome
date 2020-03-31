import os

from util import getwd

SERVER = 'http://127.0.0.1:1313'
SERVER = 'http://172.19.0.2:1313'				# running inside docker now for development
API_V = 'v1'


PRODUCTION_SERVER = 'https://quarantine.infino.me'


RECEPTORS_DIR = 'docking/receptors'
RECEPTORS_DIR = os.path.join(getwd(), 'receptors')



TRANCHE_DOWNLOAD_LOCATION = os.path.join(getwd(), 'downloads')

MGL_PATH = os.path.join(os.getcwd(), 'mgltools_x86_64Linux2_1.5.6')

LOCAL_RESULTS_DIR = os.path.join( getwd(), 'results' )