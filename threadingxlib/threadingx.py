# Copyright Hugh Perkins 2009
#
# License: Mozilla Public License v1.1
# http://www.mozilla.org/MPL/MPL-1.1.html
#

import sys
import os
import subprocess
import socket
import pickle
import threading
import thread
import time
from optparse import OptionParser

max_pending_connections = 1000
max_data_size = 10000

scriptdir = os.path.dirname( os.path.realpath( __file__ ) )

# used by spawn to receive the child's proxy
class ChildRegistrationResponse(object):
   def __init__(self ):
      self.child = None

   def setchild( self, sender, child ):  # sender and child will of course be the same, but anyway..
      self.child = child

queuelock = threading.Lock()
incomingmessageevent = threading.Event() # the main thread will unset this when it wants
                                             # to wait on a new message
                                             # the socket threads will set this whenever
                                             # they've enqueued a new message
                                         # waiting on an event blocks until the event is set

class IncomingConnection(threading.Thread):
   def __init__(self, threadx, socket ):
      threading.Thread.__init__(self)
      self.threadx = threadx
      self.socket = socket
      self.clientport = None

   # receives until it has len data
   # checks for self.threadx.shutdownnoww every second or so
   # returns targetlength worth of received data
   def getdata(self, targetlength ):
      data = ''
      while len(data) < targetlength and not self.threadx.shutdownnow:
         try:
            newdata = self.socket.recv( targetlength - len(data) )
            if newdata == '':
               return None
            data = data + newdata
         except:
            # self.debug( "Exception: " + str( sys.exc_type ) )
            pass # ignore timeout exceptions etc
      return data

   def debug( self, message):
      if self.clientport != None:
         self.threadx.debug( 'connection from ' + str( self.clientport ) + ': ' + message )
      else:
         self.threadx.debug( 'connection: ' + message )

   def run(self):
      self.socket.settimeout(1.0)
      while not self.threadx.shutdownnow:
         lendata = self.getdata(10)
         if self.threadx.shutdownnow:
            continue
         if lendata == None:
            return
         length = int( lendata )
         data = self.getdata( length )
         if self.threadx.shutdownnow:
            continue
         if data == None:
            return
         dataobject = pickle.loads( data )
         (self.clientport, otherstuff ) = dataobject
         #self.threadx.debug( "received " + str( dataobject ) )
         queuelock.acquire()
         self.threadx.queue.append( dataobject )
         queuelock.release()
         incomingmessageevent.set()
         #self.debug( "added to queue: " + str( dataobject ) )
      #self.debug(' shut down')
      self.socket.close()

class IncomingListener(threading.Thread):
   def __init__(self, threadx, socket ):
      threading.Thread.__init__(self)
      self.threadx = threadx
      self.socket = socket

   def run(self):
      self.socket.settimeout(1.0)
      while not self.threadx.shutdownnow:
         try:
            ( clientsocket, info ) = self.socket.accept()
            #self.threadx.debug( "incominglistener got new connection" )
            connectionthread = IncomingConnection( self.threadx, clientsocket )
            self.threadx.threadslock.acquire()
            self.threadx.threads.append( connectionthread )
            self.threadx.threadslock.release()
            connectionthread.start()
         except:
            pass # ignore exceptions gennerated by accept
      #self.threadx.debug('incominglistener thread shut down')
      self.socket.close()

class ThreadingX(object):
   def __init__(self, port = 0, name = '' ):
      # our listening socket
      self.mysocket = None

      self.parentport = None

      self.childpopens = []
      self.childports = []

      self.outgoingsockets = {} # socket by port number
      # self.incomingsockets = [] # just a bunch of accepted sockets

      self.threadslock = threading.Lock() # protect self.threads
      self.threads = []  # mostly for diagnostics

      self.queue = []

      self.registry = None

      self.instance = None
      self.functions = {}
      self.functionname = None

      self.shutdownnow = False

      # open a listening socket for us
      self.mysocket = socket.socket()
      self.mysocket.bind(('localhost',port))
      self.mysocket.listen(max_pending_connections)
      self.myportnumber = self.mysocket.getsockname()[1]
      self.incominglistener = IncomingListener( self, self.mysocket )
      self.threadslock.acquire()
      self.threads.append( self.incominglistener )
      self.threadslock.release()
      self.incominglistener.start() #spawn thread for listening to incoming connections
                                    # and pumping into queue

      self.register_function(self._shutdown)

      # if we are a child, we should see parents port on commandline
      # so we connect to the parent and tell parent our own listeninger port number
      parser = OptionParser()
      parser.add_option('--parentport', dest='parentport')
      parser.add_option('--registryport', dest='registryport')      
      (options, args ) = parser.parse_args()
      if options.parentport != None:
         if options.registryport != 'None':
            self.registry = self.getproxy( int(options.registryport) )

         self.parentport = int(options.parentport)
         self.getproxy( self.parentport ).setchild( self.getme() )
      else:
         # we are main basically, so create the registry
         self.registry = self.spawn(scriptdir + '/registryserver')

   def getparent(self):
      return self.getproxy( self.parentport )

   def getme(self):
      return self.getproxy( self.mysocket.getsockname()[1] )

   def getregistry(self):
      return self.registry

   # run modulename using python, passing in our socket port number as a commandline parameter
   # wait for it to connect back to us telling us its port number
   # add it to childpopens and childports
   def spawn( self, modulename ):
      childregistrationresponse = ChildRegistrationResponse()
      oldinstance = self.register_instance( childregistrationresponse )

      registrystring = str(None)
      if self.registry != None:
         registrystring = str(self.registry.getchildport())
      popen = subprocess.Popen( [ sys.executable, modulename + ".py", '--parentport=' + str( self.mysocket.getsockname()[1]), '--registryport=' + registrystring ] )
      self.childpopens.append(popen)

      while childregistrationresponse.child == None and not self.shutdownnow:
         self.receive()

      self.register_instance( oldinstance )
      return childregistrationresponse.child


   # creates a new port and a new connection to target, sends the data, then closes the port
   def sendbis( self, target, data ):
      # print str(self.getme()) + " sending " + str(data) + ' to ' + str(target)
      pickleddata = data
      pickleddata = pickle.dumps( ( self.mysocket.getsockname()[1], data ) )
      if not self.outgoingsockets.has_key( target ):
         newsocket = socket.socket()
         newsocket.connect(('localhost', target))
         self.outgoingsockets[ target ] = newsocket
      outgoingsocket = self.outgoingsockets[ target ]
      # self.debug('send len ' + str( len(pickleddata)))
      outgoingsocket.send( str( len( pickleddata ) ).rjust(10) )  # send length first;  probably
                                                                  # a more efficient way of sending this ;-)
      outgoingsocket.send( pickleddata )

   def sendfunctioncall( self, target, functionname, args ):
      argstosend = []
      for arg in args:
         if arg.__class__ == self.Proxy:
            argstosend.append(('threadx.thread',arg.getchildport()))
         else:
            argstosend.append(arg)
      self.sendbis( target, ( functionname, argstosend ) )

   class Proxy(object):
      def __init__(self, threadx, target ):
         self.threadx = threadx
         self.target = target
         self.functionname = None

      def __getattr__(self, name ):
         self.functionname = name  # not very thread-safe I know ;-)
         return self.genericfunctionproxy

      def getchildport(self):
         return self.target

      def genericfunctionproxy( self, *args ):
         self.threadx.sendfunctioncall( self.target, self.functionname, args )

      def __str__(self):
         return 'process on port ' + str( self.target )

   def getproxy(self, target ):
      return self.Proxy( self, target )

   # return true if call considered 'successful', and we can remove from queue
   # functions we are caling can return 'False' to instruct us to keep it on the queue
   def trycalling( self, queueitem ):
      (clientport,data) = queueitem
      (functionname,args) = data
      functiontocall = None

      if functionname in dir(self.instance):
         functiontocall = getattr(self.instance,functionname)

      if functiontocall == None:
         if self.functions.has_key(functionname ):
            functiontocall = self.functions[functionname]

      if functiontocall == None:
         return False # couldnt find a candidate function to run

      # print str(self.getme()) + " running function " + functionname + " " + str( args ) + " >>>"
      argstouse = []
      for arg in args:
         try:
            (thistype,port) = arg
            if thistype == 'threadx.thread':
               argstouse.append( self.getproxy( port ) )
            else:
               argstouse.append( arg )
         except:
            argstouse.append(arg)
      result = functiontocall( self.getproxy(clientport), *argstouse)
      if result == False:
         # print str(self.getme()) + " ... call to function " + functionname + " left in queue"
         return False
      return True

   # go through the queue looking for matches
   # if we find a match, call it and return True
   # otherwise return False
   def checkqueue(self):
      # self.debug('queue:')
      queuecopy = []
      queuelock.acquire()
      for (queueitem) in self.queue:
         queuecopy.append( queueitem )
      queuelock.release()
      for (queueitem) in queuecopy:
         # self.debug('queueitem: ' + str(queueitem ) )
         if self.trycalling( queueitem ):
            queuelock.acquire()
            self.queue.remove( queueitem )
            queuelock.release()
            return True
      return False

   def debug( self, message ):
      try:
         print str(self.myportnumber) + " " + message
      except:
         print " " + message

   # returns False if we should shutdown now (eg for a child process)
   # otherwise returns True, whether or not it processed anything
   def receive(self):
      while True:
         if self.shutdownnow:         
            # self.debug( "receive got shutdownnow, exiting" )
            return False

         # in relation to the incomingmessageevent event:
         # - it won't cause a block here if we exit when there's still something in the queue to
         #   to process
         # - we must never block if there is already something in the queue to process, otherwise
         #   we may block forever
         # - so we should only unset the event *before* checking the queue
         # - I think we should make sure we process one, and exactly one, function before exiting
         #   so we either find one and process it, or wait for a message until we've found one
         incomingmessageevent.clear()
         if self.checkqueue(): # if returns True, we processed seomthing
            return True
         incomingmessageevent.wait()  # if it's already been set, this won't block here, will
                                     # just go straight through

   # register new instance, returns old one, or None
   def register_instance( self, instance ):
      oldinstance = self.instance
      self.instance = instance
      return oldinstance

   def register_function(self, function ):
      self.functions[function.__name__] = function

   def _shutdown(self, requester ):
      self.shutdownnow = True

   # kill all children, and close our port
   def shutdown(self):
      self.shutdownnow = True
      for i in range(len(self.childports)):
         self.getproxy( self.childports[i] )._shutdown()
      
      # we should shut down all the outgoing connections too:
      for target in self.outgoingsockets.keys():
         self.outgoingsockets[target].close()
      self.outgoingsockets = {}

      for i in range(len(self.childports)):
         self.childpopens[i].wait()

      self.mysocket.close()
      incomingmessageevent.set()

   # diagnostic function: print state of all threads
   def dumpthreads(self):
      self.debug("thread dump:")
      self.threadslock.acquire()
      for thread in self.threads:
         self.debug( "   thread: " + str( thread ) )
      self.threadslock.release()

   def close(self):
      self.shutdown()



