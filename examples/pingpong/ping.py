import sys
import os
import subprocess
import socket
import pickle

from threadingxlib import *

class Ping():
   def oninit( self, threadx ):
      self.threadx = threadx
      registry = registrylib.Registry(self.threadx)
      registry.register( 'ping', self.threadx.getme() )
      self.pong = registry.lookup( 'pong')

   def ping( self, requester, count ):
      print 'ping ' + str( count )
      if count > 0:
         self.pong.pong( count - 1 )
      else:
         print "Finished"
         self.threadx.getparent().finished()

threadingx.ThreadingX( instance = Ping() )

