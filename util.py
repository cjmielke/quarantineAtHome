import os
import sys

import requests


def getwd():
    if os.name == 'nt':
        if hasattr(sys, 'frozen'):
                #print 'this is a pyinstaller-compiled binary'
                #print sys.frozen
                #print sys._MEIPASS                      # location of directory program is running in
                return sys._MEIPASS
        else:
            return os.getcwd()  # how I originally did this ....

    else:
        return os.getcwd()              # how I originally did this ....




def downloadFile(src, dest, replace=True):
    if dest is None or dest == '': dest = os.path.join(getwd(), src.split('/')[-1])

    if not replace and os.path.exists(dest):
        print 'already have ', dest

    R = requests.get(src)
    with open(dest, 'wb') as fh:
        fh.write(R.content)