import sys
import os
import subprocess
import socket
import pickle

from threadingxlib import *

class Pong():
   def oninit( self, threadx ):
      self.threadx = threadx
      registry = registrylib.Registry(self.threadx)
      registry.register( 'pong', self.threadx.getme() )
      self.ping = registry.lookup( 'ping')

   def pong( self, requester, count ):
      print 'pong ' + str( count )
      if count > 0:
         self.ping.ping( count - 1 )
      else:
         print "Finished"
         self.threadx.getparent().finished()

threadingx.ThreadingX( instance = Pong() )

