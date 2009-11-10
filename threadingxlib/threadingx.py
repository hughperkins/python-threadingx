"""\
Copyright Hugh Perkins 2009

License: Mozilla Public License v1.1
http://www.mozilla.org/MPL/MPL-1.1.html

Please see http://manageddreams.com/python-threadingx for documentation and tutorial
"""

import sys
import os
import subprocess
import socket
import pickle
from optparse import OptionParser

max_pending_connections = 1000
max_data_size = 10000

scriptdir = os.path.dirname( os.path.realpath( __file__ ) )

# used by spawn to receive the child's proxy
class _ChildRegistrationResponse(object):
   def __init__(self ):
      self.child = None

   def setchild( self, sender, child ):  # sender and child will of course be the same, but anyway..
      self.child = child

class ThreadingX(object):
   def __init__(self, instance = None, port = 0, name = '' ):
      """\
      parameters:

      - port: the port to listen to other processes on,
        or zero to pick any available port

      - instance: if you pass in an object instance, 
        this will run for you:

          threadx.register_instance( instance )
          while threadx.receive():
             pass
          threadx._shutdown()
      """
      # our listening socket
      self.mysocket = None

      self.parentport = None

      self.childpopens = []
      self.childports = []

      self.proxies = {} # dict of proxy by port number, so each proxy is unique per port number

      self.queue = []

      self.registry = None

      self.instance = None
      self.functions = {}
      self.functionname = None

      self._shutdownnowflag = False

      # open a listening socket for us
      self.mysocket = socket.socket()
      self.mysocket.bind(('localhost',port))
      self.myportnumber = self.mysocket.getsockname()[1]
      self.mysocket.listen(max_pending_connections)
      self.register_function(self._shutdownnow)

      # if we are a child, we should see parents port on commandline
      # so we connect to the parent and tell parent our own listeninger port number
      parser = OptionParser()
      parser.add_option('--parentport', dest='parentport')
      parser.add_option('--registryport', dest='registryport')      
      (options, args ) = parser.parse_args()
      if options.parentport != None:
         if options.registryport != 'None':
            self.registry = self._getproxy( int(options.registryport) )

         self.parentport = int(options.parentport)
         self._getproxy( self.parentport ).setchild( self.getme() )
      else:
         # we are main basically, so create the registry
         self.registry = self.spawn(scriptdir + '/registryserver')

      if instance != None:
         try:
            if 'oninit' in dir( instance ):
               instance.oninit( self )
            self.register_instance( instance )
            while self.receive():
               pass
         finally:
            self._shutdown()

   def getparent(self):
      """\
      For children, returns a proxy representing the parent process, 
      otherwise None
      """
      if self.parentport != None:
         return self._getproxy( self.parentport )
      return None

   def getme(self):
      """\
      Returns a proxy representing the current process.
      Can be sent through method calls to other processes.
      """
      return self._getproxy( self.mysocket.getsockname()[1] )

   def _getregistry(self):
      """\
      Returns a proxy to the registry process.

      Best to use an instance of Registry instead though, which
      is a higher level abstraction.
      """
      return self.registry

   def spawn( self, modulename ):
      """\
      Run modulename using python as a child process

      Returns a proxy object representing the child object, on which
      methods can be called.
      """
      # wait for it to connect back to us telling us its port number
      # add it to childpopens and childports
      childregistrationresponse = _ChildRegistrationResponse()
      oldinstance = self.register_instance( childregistrationresponse )

      registrystring = str(None)
      if self.registry != None:
         registrystring = str(self.registry.getchildport())
      popen = subprocess.Popen( [ sys.executable, modulename + ".py", '--parentport=' + str( self.mysocket.getsockname()[1]), '--registryport=' + registrystring ] )
      self.childpopens.append(popen)

      while childregistrationresponse.child == None and not self._shutdownnowflag:
         self.receive()

      self.register_instance( oldinstance )
      self.childports.append( childregistrationresponse.child.getchildport() )
      return childregistrationresponse.child


   # returns (clientsocket, data )
   # blocks until someone connects and sends us something,
   # which we then add to the queue
   def _enqueuenextmessage(self):
      (clientsocket,info) = self.mysocket.accept()
      data = clientsocket.recv(max_data_size)
      clientsocket.close()
      dataobject = data
      dataobject = pickle.loads( data )
      self.queue.append( dataobject )
      #print str(self.getme()) + ' queued ' + str(dataobject )

   # creates a new port and a new connection to target, sends the data, then closes the port
   def _sendbis( self, target, data ):
      #print str(self.getme()) + " sending " + str(data) + ' to ' + str(target)
      pickleddata = data
      pickleddata = pickle.dumps( ( self.mysocket.getsockname()[1], data ) )
      outgoingsocket = socket.socket()
      outgoingsocket.connect(('localhost', target ))
      outgoingsocket.send( pickleddata )
      outgoingsocket.close()

   def _sendfunctioncall( self, target, functionname, args ):
      argstosend = []
      for arg in args:
         if arg.__class__ == self._Proxy:
            argstosend.append(('threadx.thread',arg.getchildport()))
         else:
            argstosend.append(arg)
      self._sendbis( target, ( functionname, argstosend ) )

   class _Proxy(object):
      def __init__(self, threadx, target ):
         self.threadx = threadx
         self.target = target
         self.functionname = None

      def __getattr__(self, name ):
         self.functionname = name  # not very thread-safe I know ;-)
         return self._genericfunctionproxy

      def getchildport(self):
         return self.target

      def _genericfunctionproxy( self, *args ):
         self.threadx._sendfunctioncall( self.target, self.functionname, args )

      def __str__(self):
         return '_Proxy to ' + str( self.target )

   def _getproxy(self, target ):
      """\
      returns a proxy object for the target 'target' (currently, a port 
      number)
      """
      if not self.proxies.has_key( target ):
         self.proxies[ target ] = self._Proxy( self, target )
      return self.proxies[ target ]

   # return true if call considered 'successful', and we can remove from queue
   # functions we are caling can return 'False' to instruct us to keep it on the queue
   def _trycalling( self, queueitem ):
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
               argstouse.append( self._getproxy( port ) )
            else:
               argstouse.append( arg )
         except:
            argstouse.append(arg)
      result = functiontocall( self._getproxy(clientport), *argstouse)
      if result == False:
         #print str(self.getme()) + " ... call to function " + functionname + " left in queue"
         return False
      return True

   def receive(self):
      """\
      Runs one, and only one, function call in the queue, then returns.

      If there are no function calls in the queue that match the 
      current registered instance or functions, then blocks until a
      new function call arrives.

      A called function that requested to be left in the queue does not
      count as a function call that has been run.

      Returns False if we should shutdown now (eg for a child process)
      otherwise returns True
      """
      while True:
         if self._shutdownnowflag:         
            return False

         # go through the queue looking for matches
         for (queueitem) in self.queue:
            if self._trycalling( queueitem ):
               self.queue.remove( queueitem )
               return True

         # if didn't find one, wait for new message, and try again
         self._enqueuenextmessage()

   def register_instance( self, instance ):
      """\
      Registers new instance, returning old registered instance or None
 
      All methods on the instance become callable by other processes
      """
      oldinstance = self.instance
      self.instance = instance
      return oldinstance

   def register_function(self, function ):
      """\
      Registers a function that can be called by other processes
      """
      self.functions[function.__name__] = function

   def _shutdownnow(self, requester ):
      # self._debug( "setting _shutdownnowflag" )
      self._shutdownnowflag = True

   def shutdownnow(self):
      """\
      Requests threadingx to shut down cleanly, cleaning up any child
      processes and sockets.

      This is only useful when you passed in an instance to the __init__
      method initially, otherwise you should call 'close' directly 
      instead.
      """
      self._shutdownnowflag = True

   def _debug( self, message ):
      print str( self.myportnumber) + ": " + message

   # kill all children, and close our port
   def _shutdown(self):
      #self._debug( " ... shutting down ..." )
      for i in range(len(self.childports)):
         #self._debug( " ... telling child to shutdown ..." )
         self._getproxy( self.childports[i] )._shutdownnow()
         #self._debug( " ... waiting for child ..." )
         self.childpopens[i].wait()
      
      self.mysocket.close()
      #self._debug( " ... shutdown finished" )

   def close(self):
      """\
      Immediately shutdown threadingx, including child processes and 
      sockets
      """
      self._shutdown()



