import sys
import os
import subprocess
import socket
import pickle
import time

from threadingxlib import *

class LauncherClass():
   def oninit(self, threadx ):
      self.threadx = threadx
      ping = self.threadx.spawn('ping')
      pong = self.threadx.spawn('pong')
      ping.ping( 20)

   def finished( self, requester ):
      self.threadx.shutdownnow()

threadingx.ThreadingX( instance = LauncherClass() )

