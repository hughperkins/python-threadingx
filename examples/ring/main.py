import sys
import os

from threadingxlib import *

N = 3
M = 3

class Main(object):
   def __init__(self):
      self.isfinished = False

   def finished( self, sender ):
      self.isfinished = True

threadx = threadingx.ThreadingX()

previousworker = None
firstworker = None
for n in xrange(0, N - 1):
   worker = threadx.spawn('worker')
   if previousworker != None:
      previousworker.setnextnode( worker )
   else:
      firstworker = worker
   previousworker = worker
manager = threadx.spawn('manager')
manager.setmain( threadx.getme() )
previousworker.setnextnode( manager )
manager.setnextnode( firstworker )

main = Main()
threadx.register_instance(main)
firstworker.relay( M )
while not main.isfinished:
   threadx.receive()

threadx.shutdown()

