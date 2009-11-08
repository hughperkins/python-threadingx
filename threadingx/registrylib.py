import sys
import os
import subprocess
import socket
import pickle
import time

import threadingx

# registryport = 1313

class Registry():
   def __init__(self):
      self.port = None

   def registryresponse(self, name, lport):
      #print str(threadingx.getme()) + ' got port ' + str(lport) + ' for ' + name
      self.port = lport

# synchronous
def lookup(name):
   registry = Registry()
   oldinstance = threadingx.register_instance( registry )
   threadingx.getproxy(threadingx.getregistry()).lookup(threadingx.getme(),name)
   while registry.port == None:
      threadingx.receive()
   threadingx.register_instance(oldinstance)  # put the old instance back, if anything
   return registry.port

# asynchonous
def register(name, target):
   threadingx.getproxy(threadingx.getregistry()).register(name,target)

