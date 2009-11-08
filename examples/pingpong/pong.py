import sys
import os
import subprocess
import socket
import pickle

from threadingxlib import *

class Pong():
   def __init__(self, threadx, ping):
      self.threadx = threadx
      self.ping = ping

   def pong( self, requester, count ):
      print 'pong ' + str( count )
      if count > 0:
         self.ping.ping( count - 1 )
      else:
         print "Finished"
         self.threadx.getparent().finished()

def go():
   threadx = threadingx.ThreadingX()
   registry = registrylib.Registry(threadx)

   registry.register( 'pong', threadx.getme())
   ping = registry.lookup( 'ping')

   threadx.register_instance( Pong(threadx, ping) )
   while threadx.receive():
      pass
   threadx.close()

if __name__ == '__main__':
   go()

