import os

SERVER = 'http://127.0.0.1:1313'
SERVER = 'http://172.19.0.2:1313'				# running inside docker now for development
API_V = 'v1'


PRODUCTION_SERVER = 'https://quarantine.infino.me'


RECEPTORS_DIR = 'docking/receptors'
RECEPTORS_DIR = os.path.join(os.getcwd(), 'receptors')



TRANCHE_DOWNLOAD_LOCATION = os.path.join(os.getcwd(), 'downloads')

