import SimpleHTTPServer
import SocketServer
import json
import multiprocessing
import os
import thread
import time
import webbrowser
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

import simplejson as simplejson

from settings import LOCAL_RESULTS_DIR, getwd
from util import downloadFile

DEFAULT_PORT = 7777



'''
Notes on how to build a very simple client-side interface ....

Client process starts a simple webserver thread that serves up all files in program directory
Javascript on page merely polls a file to discover last completed jobID. Whenever this ID changes,
it triggers an interface update that
    - loads the next active ligand
    - loads the receptor and pose information from the results directory



'''

# for testing
# curl -d '{"name":"anonymous"}' -H "Content-Type: application/json" http://172.19.0.2:7778/

#DEV = True
DEV = os.getenv('DEBUG')		# if set, enters developer mode (contacts local server


def prepServer():
    '''
    The client GUI is just a minimal webpage (html and javascript) that
    the client hosts with a very basic webserver. The html/js assets are
    maintained on the main server, because this simplifies
    - development, via coffeescript and pug templates
    - instant updates, since the client can just fetch new versions
    '''

    lis = [
        ('/client/index-v1.html', 'index.html'),            # always save to index.html locally, but server-side can have multiple routes+templates
        #('/static/js/client.min.js', ''),                  # dont need to distinguish between these anymore
        ('/static/js/client.v1.js', ''),                    # on server just change filename in assets.py, and commit old ones to git repo
    ]

    if DEV: host = 'http://172.19.0.2:1313'
    else:
        host='https://cjmielke.github.io/quarantineAtHome/clientstatic/'      # FIXME
        host = 'https://quarantine.infino.me/'  # FIXME

    for src, dest in lis:
        downloadFile(host + src, dest)


    # set up results area
    if not os.path.exists(LOCAL_RESULTS_DIR): os.makedirs(LOCAL_RESULTS_DIR)


prepServer()











# ======== Config objects - serialized to disk with JSON

class JsonFile():
    def save(self, fileName):
        with open(fileName, 'w') as lf:
            results = self.__dict__
            json.dump(results, lf)

class UpdateObj(JsonFile):
    def __init__(self):
        self.lastJob = None
        self.ligand = None
        self.receptor = None
        self.lastResults = {}

class SettingsObj(JsonFile):
    def __init__(self):
        self.username = 'anonymous'


# ===============


class ServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def hook(self, data):     # something to be added after the fact
        raise NotImplementedError

    def translate_path(self, path):             # for rewriting paths
        # if '/static/' in path: path = path.replace('/static/', '/')
        path = path.replace('/static/js/', '/')
        path = path.replace('/static/', '/')
        path = SimpleHTTPServer.SimpleHTTPRequestHandler.translate_path(self, path)
        return path

    def end_headers(self):                      # disable browser cache
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        SimpleHTTPServer.SimpleHTTPRequestHandler.end_headers(self)         # dont forget this!

    def log_message(self, format, *args):       # suppress some logs
        if 'GET /update.json' in args[0]: return
        BaseHTTPRequestHandler.log_message(self, format, *args)
        return


    def do_POST(self):                          # eventually needed to allow user to set username
        self.data_string = self.rfile.read(int(self.headers['Content-Length']))
        self.send_response(200)
        self.end_headers()

        print self.raw_requestline                      # POST /config HTTP/1.1    .....   can use this for routing with multiple endpoints

        data = simplejson.loads(self.data_string)
        self.hook(data)

        with open("settings.json", "w") as outfile:
            simplejson.dump(data, outfile)
        print "{}".format(data)
        # f = open("for_presen.py")
        # self.wfile.write(f.read())
        return

class ThreadedHTTPServer(SocketServer.ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

#DD = {}

class GUIServer():

    def __init__(self):

        self.port = None
        self.httpd = None
        self.updateObj = UpdateObj()
        self.settings = SettingsObj()

        #global DD
        #self.postData = DD
        self.postData = {}

        '''
        self.jobListFile = os.path.join(getwd(), 'jobs.txt')
        self.jobList = []
        if os.path.exists(self.jobListFile):
            with open(self.jobListFile, 'r') as jl:
                for row in jl:
                    rDict = json.loads(row)
                    self.jobList.append(rDict)
        '''

    def update(self):
        '''
        For now im lazy so I just write a file that client JS polls ....
        In the future, serve from memory .... or use websocket
        '''
        self.updateObj.save(os.path.join(getwd(), 'update.json' ))

    def nextJob(self, zincID, receptor):
        print 'running docking algorithm on ', receptor         # serves commandline interface
        self.updateObj.ligand = zincID
        self.updateObj.receptor = receptor
        self.update()

    def jobFinished(self, jobID, results):
        self.updateObj.lastJob = jobID
        self.updateObj.lastResults = results.copy()
        self.update()

    def appendToLog(self):
        '''add status messages to a buffer - lets the user know what's going on'''


    def tailLog(self):
        '''Follow a log for important status updates and append to buffer'''


    # FIXME - this will eventually be where we handle post/config updates
    def outerHook(self, data):
        print 'you have successfully replaced it!', data
        self.postData = data


    def startServer(self):

        # silly way of finding an ephemeral port .... there are better ways : https://stackoverflow.com/questions/1365265/on-localhost-how-do-i-pick-a-free-port-number
        for n in range(40):
            tryport = DEFAULT_PORT+n
            try:
                #self.httpd = SocketServer.TCPServer(("", tryport), ServerHandler)
                host = 'localhost'
                if DEV : host = ''
                self.httpd = ThreadedHTTPServer((host, tryport), ServerHandler)
                self.httpd.RequestHandlerClass.hook = self.outerHook
                self.port = tryport

                print 'Successfully started GUI server on port ', self.port
                break  # leave the loop!
            except Exception as e:
                # print 'This port is used, trying next'
                if 'Address already in use' in e.message:
                    print 'This port is used, trying next'
                else:
                    raise

        # threading mode
        def startThread():
            while True:
                try: self.httpd.serve_forever()
                except: time.sleep(2)
        # start the server in a background thread
        thread.start_new_thread(startThread, ())

        # FIXME - would love to run webserver as a separate process, but then I lose shared variables
        '''
        # multiprocessing mode
        server_process = multiprocessing.Process(target=self.httpd.serve_forever)
        server_process.daemon = True
        server_process.start()
        '''

        if not self.httpd:
            raise ValueError('Could not start local webserver')         # FIXME - fallback to commandline client?

        return self

    def openBrowser(self):
        url = 'http://127.0.0.1:'+str(self.port)

        def delayedStart():                     # wait a few seconds to start, but return immediately
            time.sleep(4)
            webbrowser.open(url, new=1)
        thread.start_new_thread(delayedStart, ())

        return self




    def loadConfig(self):
        pass

    def updateConfig(self):
        pass






if __name__=='__main__':
    #runInBackground()


    wg = GUIServer().startServer()#.openBrowser()

    while True:
        print 'still executing', wg.postData, wg.port
        #print httpd
        time.sleep(1)

    #print "serving at port", DEFAULT_PORT
    #httpd.serve_forever()




