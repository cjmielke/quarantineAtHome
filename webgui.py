import SimpleHTTPServer
import SocketServer
import json
import multiprocessing
import os
import thread
import time
import webbrowser

import simplejson as simplejson

from settings import LOCAL_RESULTS_DIR
from util import downloadFile, getwd

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

DEV = True
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
        ('/client/index.html', ''),
        ('/static/js/client.min.js', ''),
        ('/static/js/clientcoffee.js', ''),
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

class ServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def hook(self):     # something to be added after the fact
        raise NotImplementedError

    def translate_path(self, path):
        # if '/static/' in path: path = path.replace('/static/', '/')
        path = path.replace('/static/js/', '/')
        path = path.replace('/static/', '/')
        path = SimpleHTTPServer.SimpleHTTPRequestHandler.translate_path(self, path)
        return path

    def log_message(self, format, *args):
        #BaseHTTPRequestHandler.log_message(self, format, *args)
        return

    def do_POST(self):
        self.hook()
        # self._set_headers()
        print "in post method", self.testattrib
        self.data_string = self.rfile.read(int(self.headers['Content-Length']))

        self.send_response(200)
        self.end_headers()

        data = simplejson.loads(self.data_string)
        with open("config.json", "w") as outfile:
            simplejson.dump(data, outfile)
        print "{}".format(data)
        # f = open("for_presen.py")
        # self.wfile.write(f.read())
        return


class GUIServer():
    testattrib = None

    def __init__(self):

        self.port = None
        self.httpd = None
        self.updateObj = UpdateObj()
        self.settings = SettingsObj()

    def update(self):
        '''
        For now im lazy so I just write a file
        In the future, this can just be served from memory ....
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



    # FIXME - this will eventually be where we handle post/config updates
    def outerHook(self):
        print 'you have successfully replaced it!'

    def startServer(self):

        for n in range(40):
            tryport = DEFAULT_PORT+n
            try:
                self.httpd = SocketServer.TCPServer(("", tryport), ServerHandler)
                self.httpd.RequestHandlerClass.hook = self.outerHook

                def start_server():
                    while True:
                        try:
                            self.httpd.serve_forever()
                        except:
                            pass
                # start the server in a background thread
                thread.start_new_thread(start_server, ())

                '''

                server_process = multiprocessing.Process(target=self.httpd.serve_forever)
                server_process.daemon = True
                server_process.start()
                '''

                self.port = tryport
                print 'Successfully started GUI server on port ', self.port
                break       # leave the loop!
            except Exception as e:
                #print 'This port is used, trying next'
                if 'Address already in use' in e.message:
                    print 'This port is used, trying next'
                else: raise

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
        #print 'still executing'
        #print httpd
        time.sleep(4)

    #print "serving at port", DEFAULT_PORT
    #httpd.serve_forever()




