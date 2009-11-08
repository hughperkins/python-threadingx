import sys
import os
import subprocess
import socket
import pickle
import time

from threadingx import threadingx, registrylib

class LauncherClass():
   def __init__(self):
      self.isfinished = False

   def sayHello( self, message, age ):
      print 'sayhello called with message ' + message + ' and age ' + str( age )

   def registryresponse(self, name, response ):
      print name + ' ' + str(response)

   def finished( self ):
      self.isfinished = True

def go():
   threadingx.init()
   launcher = LauncherClass()
   threadingx.register_instance( launcher )

   ping = threadingx.spawn('ping')
   pong = threadingx.spawn('pong')
   threadingx.getproxy(ping).ping(20)

   while not launcher.isfinished:
      threadingx.receive()   

   threadingx.shutdown()

if __name__ == '__main__':
   go()

