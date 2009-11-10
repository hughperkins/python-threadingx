import sys
import os

from threadingxlib import *

import primes

class PrimeChild(object):
   def go(self,sender,num):
      print len( primes.getprimes(num) )
      sender.finished()

def go():
   threadx = threadingx.ThreadingX()
   threadx.register_instance(PrimeChild())
   while threadx.receive():
      pass
   threadx.shutdown()

if __name__ == '__main__':
   go()

