import sys
import os
import subprocess
import socket
import pickle

from threadingxlib import *

class Ping():
   def __init__(self, threadx, pong):
      self.threadx = threadx
      self.pong = pong

   def ping( self, requester, count ):
      print 'ping ' + str( count )
      if count > 0:
         self.pong.pong( count - 1 )
      else:
         print "Finished"
         self.threadx.getparent().finished()

def go():
   threadx = threadingx.ThreadingX()
   registry = registrylib.Registry(threadx)

   registry.register( 'ping', threadx.getme())
   pong = registry.lookup( 'pong')

   threadx.register_instance( Ping(threadx, pong) )
   while threadx.receive():
      pass
   threadx.close()

if __name__ == '__main__':
   go()

