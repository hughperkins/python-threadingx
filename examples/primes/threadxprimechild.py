import sys
import os

from threadingxlib import *

import primes

class PrimeChild(object):
   def go(self,sender,num):
      sender.finished( len(primes.getprimes(num) ) )

threadingx.ThreadingX( PrimeChild() )


