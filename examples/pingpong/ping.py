import sys
import os
import subprocess
import socket
import pickle

from threadingx import threadingx, registrylib

class Ping():
   def __init__(self,pong):
      self.pong = pong

   def ping( self, count ):
      print 'ping ' + str( count )
      if count > 0:
         threadingx.getproxy( self.pong ).pong( count - 1 )
      else:
         print "Finished"
         threadingx.getproxy( threadingx.getparent() ).finished() 

def go():
   threadingx.init()

   registrylib.register('ping', threadingx.getme())
   pong = registrylib.lookup('pong')

   threadingx.register_instance(Ping(pong))
   while threadingx.receive():
      pass
   threadingx.shutdown()

if __name__ == '__main__':
   go()

