"""\
Copyright Hugh Perkins 2009

License: Mozilla Public License v1.1
http://www.mozilla.org/MPL/MPL-1.1.html

The Registry class can be used to communicate with the registry process.

It can be used to register processes using names, which other processes
can then look up
"""

import sys
import os
import subprocess
import socket
import pickle
import time

import threadingx

# registryport = 1313

class Registry(object):
   class _RegistryResponse():
      def __init__(self):
         self.process = None

      def registryresponse(self, requester, name, process):
         self.process = process

   def __init__(self, threadx ):
      self.threadx = threadx

   # synchronous
   def lookup(self, name):
      """\
      Looks up name in the registry process, returning a child proxy
      object
     
      Synchronous, and in addition, the registryy blocks until the name 
      has been registered,
      """
      registry = self._RegistryResponse()
      oldinstance = self.threadx.register_instance( registry )
      self.threadx._getregistry().lookup( name )
      while registry.process == None:
         self.threadx.receive()
      self.threadx.register_instance(oldinstance)  # put the old instance back, if anything
      return registry.process

   def register(self, name, target):
      """\
      Register target process as name with the registry process

      Asynchonous, ie returns immediately
      """
      self.threadx._getregistry().register( name, target )
   
