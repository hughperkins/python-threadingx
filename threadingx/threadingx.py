import sys
import os
import subprocess
import socket
import pickle

max_pending_connections = 1000
max_data_size = 10000

# our listening socket
mysocket = None

parentport = None

childpopens = []
childports = []

queue = []

gname = ''

registry = None

scriptdir = os.path.dirname( os.path.realpath( __file__ ) )

def getparent():
   return parentport

def getme():
   return mysocket.getsockname()[1]

def getregistry():
   return registry

# open a listening socket for us
def initbis(port = 0):
   global mysocket, registry
   mysocket = socket.socket()
   mysocket.bind(('localhost',port))
   mysocket.listen(max_pending_connections)
   register_function(_shutdown)

# call initbis to open a listening socket for us,
# if we are a child, we should see parents port on commandline
# so we connect to the parent and tell parent our own listeninger port number
def init( port=0, name = ''):
   global mysocket, parentport, gname, registry
   gname = name
   initbis(port)
   if len(sys.argv) > 1:
      #print 'args: ' + str(sys.argv)
      parentport = int(sys.argv[1])
      parenttemp = int(sys.argv[2])
      if sys.argv[3] != 'None':
         registry = int(sys.argv[3])
      #print "parent: " + str(parent)
      connecttoparentsocket = socket.socket()
      connecttoparentsocket.connect(('127.0.0.1', parenttemp ))
      connecttoparentsocket.send(str(mysocket.getsockname()[1]))
      connecttoparentsocket.close()
   else:
      # we are main basically, so create the registry
      registry = spawn(scriptdir + '/registryserver')
   #print "threadingx.init " + str( mysocket.getsockname()[1] )

# run modulename using python, passing in our socket port number as a commandline parameter
# wait for it to connect back to us telling us its port number
# add it to childpopens and childports
def spawn( modulename ):
   global children, registry
   tempreceivesocket = socket.socket()
   tempreceivesocket.bind(('localhost',0))
   tempreceivesocket.listen(1)
   popen = subprocess.Popen( [ sys.executable, modulename + ".py", str( mysocket.getsockname()[1]), str(tempreceivesocket.getsockname()[1]), str(registry) ] )
   childpopens.append(popen)
   (childconnection,temppeerinfo) = tempreceivesocket.accept()
   childport = int(childconnection.recv(100))
   childports.append( childport )
   childconnection.close()
   tempreceivesocket.close()
   return childport

# returns (clientsocket, data )
# blocks until someone connects and sends us something,
# which we then add to the queue
def enqueuenextmessage():
   (clientsocket,info) = mysocket.accept()
   data = clientsocket.recv(max_data_size)
   clientsocket.close()
   dataobject = data
   dataobject = pickle.loads( data )
   queue.append( dataobject )
   #print str(getme()) + ' queued ' + str(dataobject )
   #return ( dataobject[0], dataobject[1] )

# creates a new port and a new connection to target, sends the data, then closes the port
def sendbis( target, data ):
   #print str(getme()) + " sending " + str(data) + ' to ' + str(target)
   pickleddata = data
   pickleddata = pickle.dumps( ( mysocket.getsockname()[1], data ) )
   outgoingsocket = socket.socket()
   outgoingsocket.connect(('localhost', target ))
   outgoingsocket.send( pickleddata )
   outgoingsocket.close()

instance = None
functions = {}

class Proxy():
   def __init__(self, target):
      self.target = target

   def __getattr__(self, name ):
      self.functionname = name  # not very thread-safe I know ;-)
      return self.genericfunctionproxy

   def genericfunctionproxy(self, *args ):
      #print "genericfunctionproxy"
      #print self.functionname
      #print args
      sendbis( self.target, ( self.functionname, args ) )

def getproxy( target ):
   return Proxy(target)

# return true if call considered 'successful', and we can remove from queue
# functions we are caling can return 'False' to instruct us to keep it on the queue
def trycalling( queueitem ):
   (clientsocket,data) = queueitem
   (functionname,args) = data
   functiontocall = None

   if functionname in dir(instance):
      functiontocall = getattr(instance,functionname)

   if functiontocall == None:
      if functions.has_key(functionname ):
         functiontocall = functions[functionname]

   if functiontocall == None:
      return False # couldnt find a candidate function to run

   #print str(getme()) + " running function " + functionname + " " + str( args )
   result = functiontocall( *args)
   if result == False:
      #print str(getme()) + " ... call to function " + functionname + " left in queue"
      return False
   return True

# returns False if we should shutdown now (eg for a child process)
# otherwise returns True, whether or not it processed anything
def receive():
   while True:
      if shutdownnow:         
         return False

      # go through the queue looking for matches
      for (queueitem) in queue:
         if trycalling( queueitem ):
            queue.remove( queueitem )
            return True

      # if didn't find one, wait for new message, and try again
      enqueuenextmessage()

# register new instance, returns old one, or None
def register_instance( linstance ):
   global instance
   oldinstance = instance
   instance = linstance
   return oldinstance

def register_function( function ):
   functions[function.__name__] = function

shutdownnow = False

def _shutdown():
   #print str(getme()) + " setting shutdownnow"
   global shutdownnow
   shutdownnow = True

# kill all children, and close our port
def shutdown():
   global mysocket
   #print str(getme()) + " ... shutting down ..."
   for i in range(len(childports)):
      getproxy( childports[i] )._shutdown()
      childpopens[i].wait()
   
   mysocket.close()


