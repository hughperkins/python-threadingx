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
import time

import threadingx

# registryport = 1313

class Registry(object):
   class RegistryResponse():
      def __init__(self):
         self.port = None

      def registryresponse(self, requester, name, lport):
         #print str(threadingx.getme()) + ' got port ' + str(lport) + ' for ' + name
         self.port = lport

   def __init__(self, threadx ):
      self.threadx = threadx

   # synchronous
   def lookup(self, name):
      registry = self.RegistryResponse()
      oldinstance = self.threadx.register_instance( registry )
      self.threadx.getregistry().lookup( name )
      while registry.port == None:
         self.threadx.receive()
      self.threadx.register_instance(oldinstance)  # put the old instance back, if anything
      return self.threadx.getproxy( registry.port )

   # asynchonous
   def register(self, name, target):
      self.threadx.getregistry().register( name,target.getchildport() )
   
