import sys
import os
import subprocess
import socket
import pickle
import time

from threadingxlib import *

class LauncherClass():
   def __init__(self):
      self.isfinished = False

   def finished( self, requester ):
      self.isfinished = True

def go():
   threadx = threadingx.ThreadingX()
   launcher = LauncherClass()
   threadx.register_instance( launcher )

   ping = threadx.spawn('ping')
   pong = threadx.spawn('pong')
   ping.ping( 20)

   while not launcher.isfinished:
      threadx.receive()   

   threadx.close()

if __name__ == '__main__':
   go()

