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
from optparse import OptionParser

max_pending_connections = 1000
max_data_size = 10000

scriptdir = os.path.dirname( os.path.realpath( __file__ ) )

class ThreadingX(object):
   def __init__(self, port = 0, name = '' ):
      # our listening socket
      self.mysocket = None

      self.parentport = None

      self.childpopens = []
      self.childports = []

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
      self.register_function(self._shutdown)

      # if we are a child, we should see parents port on commandline
      # so we connect to the parent and tell parent our own listeninger port number
      parser = OptionParser()
      parser.add_option('--parentport', dest='parentport')
      parser.add_option('--parenttempport', dest='parenttempport')
      parser.add_option('--registryport', dest='registryport')      
      (options, args ) = parser.parse_args()
      if options.parentport != None:
         # print 'args: ' + str(sys.argv)
         self.parentport = int(options.parentport)
         parenttemp = int(options.parenttempport)
         if options.registryport != 'None':
            self.registry = self.getproxy( int(options.registryport) )
         #print "parent: " + str(parent)
         connecttoparentsocket = socket.socket()
         connecttoparentsocket.connect(('127.0.0.1', parenttemp ))
         connecttoparentsocket.send(str(self.mysocket.getsockname()[1]))
         connecttoparentsocket.close()
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
      tempreceivesocket = socket.socket()
      tempreceivesocket.bind(('localhost',0))
      tempreceivesocket.listen(1)
      registrystring = str(None)
      if self.registry != None:
         registrystring = str(self.registry.getchildport())
      popen = subprocess.Popen( [ sys.executable, modulename + ".py", '--parentport=' + str( self.mysocket.getsockname()[1]), '--parenttempport=' + str(tempreceivesocket.getsockname()[1]), '--registryport=' + registrystring ] )
      self.childpopens.append(popen)
      (childconnection,temppeerinfo) = tempreceivesocket.accept()
      childport = int(childconnection.recv(100))
      self.childports.append( childport )
      childconnection.close()
      tempreceivesocket.close()
      return self.getproxy( childport )

   # returns (clientsocket, data )
   # blocks until someone connects and sends us something,
   # which we then add to the queue
   def enqueuenextmessage(self):
      (clientsocket,info) = self.mysocket.accept()
      data = clientsocket.recv(max_data_size)
      clientsocket.close()
      dataobject = data
      dataobject = pickle.loads( data )
      self.queue.append( dataobject )
      #print str(self.getme()) + ' queued ' + str(dataobject )

   # creates a new port and a new connection to target, sends the data, then closes the port
   def sendbis( self, target, data ):
      #print str(self.getme()) + " sending " + str(data) + ' to ' + str(target)
      pickleddata = data
      pickleddata = pickle.dumps( ( self.mysocket.getsockname()[1], data ) )
      outgoingsocket = socket.socket()
      outgoingsocket.connect(('localhost', target ))
      outgoingsocket.send( pickleddata )
      outgoingsocket.close()

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
         return 'Proxy to ' + str( self.target )

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

      #print str(self.getme()) + " running function " + functionname + " " + str( args ) + " >>>"
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
         #print str(self.getme()) + " ... call to function " + functionname + " left in queue"
         return False
      return True

   # returns False if we should shutdown now (eg for a child process)
   # otherwise returns True, whether or not it processed anything
   def receive(self):
      while True:
         if self.shutdownnow:         
            return False

         # go through the queue looking for matches
         for (queueitem) in self.queue:
            if self.trycalling( queueitem ):
               self.queue.remove( queueitem )
               return True

         # if didn't find one, wait for new message, and try again
         self.enqueuenextmessage()

   # register new instance, returns old one, or None
   def register_instance( self, instance ):
      oldinstance = self.instance
      self.instance = instance
      return oldinstance

   def register_function(self, function ):
      self.functions[function.__name__] = function

   def _shutdown(self, requester ):
      #print str(getme()) + " setting shutdownnow"
      self.shutdownnow = True

   # kill all children, and close our port
   def shutdown(self):
      #print str(getme()) + " ... shutting down ..."
      for i in range(len(self.childports)):
         self.getproxy( self.childports[i] )._shutdown()
         self.childpopens[i].wait()
      
      self.mysocket.close()

   def close(self):
      self.shutdown()



