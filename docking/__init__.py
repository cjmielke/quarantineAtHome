import os
import sys

#MGL_LIBS = os.path.join(os.getcwd(), 'mgltools_x86_64Linux2_1.5.6', 'MGLToolsPckgs')
#sys.path.append(MGL_LIBS)
from util import getwd

MGL_LIBS = os.path.join(getwd(), 'docking', 'mglmin')
sys.path.append(MGL_LIBS)
#print MGL_LIBS
#sys.exit(0)


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


# FIXME - parse the inhibiion constant (in millimolar, micromolar, nanomolar, etc) and standardize



