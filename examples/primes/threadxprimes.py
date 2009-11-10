import sys
import os

from threadingxlib import *

import primes

num = 200000

class MainService:
   def __init__(self):
      self.isfinished = False

   def finished( self, sender ):
      self.isfinished = True

def go():
   threadx = threadingx.ThreadingX()
   for i in range(4):
      child = threadx.spawn('threadxprimechild')
      child.go( num )
   mainservice = MainService()
   threadx.register_instance(mainservice)
   while not mainservice.isfinished and threadx.receive():
      pass
   threadx.shutdown()

if __name__ == '__main__':
   go()

