import sys
import os
import subprocess
import socket
import pickle

import threadingx # just use threadingx?

#registryport = 1313 # should be well-known to all users of registry

class RegistryServer():
   def __init__(self):
      self.names = {}

   def register( self, name, port ):
      #print "register " + name + ' ' + str(port)
      self.names[name] = port

   # returns port
   def lookup( self, requester, name ):
      reply = None
      if self.names.has_key(name):
         reply = self.names[name]
         #print "lookup " + name + ' ' + str(reply)
         threadingx.getproxy(requester).registryresponse( name, reply )
      else:
         return False  # keep the message in the queue for processing later

   def unregister(self, name):
      self.names.remove(name)

def go():
   threadingx.init()
   threadingx.register_instance( RegistryServer() )
   alive = True
   while alive:
      try:
         alive = threadingx.receive()
      except:
         print sys.exc_info()
   threadingx.shutdown()

if __name__ == '__main__':
   go()

