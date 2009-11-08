import sys
import os
import subprocess
import socket
import pickle

from threadingxlib import *

#registryport = 1313 # should be well-known to all users of registry

class RegistryServer():
   def __init__(self, threadx):
      self.names = {}
      self.threadx = threadx

   def register( self, requester, name, port ):
      #print "register " + name + ' ' + str(port)
      self.names[name] = port

   # returns port
   def lookup( self, requester, name ):
      reply = None
      if self.names.has_key(name):
         reply = self.names[name]
         #print "lookup " + name + ' ' + str(reply)
         requester.registryresponse( name, reply )
      else:
         return False  # keep the message in the queue for processing later

   def unregister(self, requester, name):
      self.names.remove(name)

def go():
   threadx = threadingx.ThreadingX()
   threadx.register_instance( RegistryServer(threadx) )
   alive = True
   while alive:
      #try:
      alive = threadx.receive()
      #except:
      #   print sys.exc_info()
   threadx.close()

if __name__ == '__main__':
   go()

