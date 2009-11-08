import sys
import os
import subprocess
import socket
import pickle

from threadingx import threadingx, registrylib

class Pong():
   def __init__(self, ping):
      self.ping = ping

   def pong( self, count ):
      print 'pong ' + str( count )
      if count > 0:
         threadingx.getproxy( self.ping ).ping( count - 1 )
      else:
         print "Finished"
         threadingx.getproxy( threadingx.getparent() ).finished() 

def go():
   threadingx.init()

   registrylib.register('pong', threadingx.getme())
   ping = registrylib.lookup('ping')

   threadingx.register_instance(Pong(ping))
   while threadingx.receive():
      pass

   threadingx.shutdown()

if __name__ == '__main__':
   go()

