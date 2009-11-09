import sys
import os

from threadingxlib import *

class Main(object):
   def __init__(self):
      self.isfinished = False

   def finished( self, sender ):
      self.isfinished = True

if len(sys.argv) == 1:
   M = 100
   N = 10
elif len(sys.argv) < 3:
   print "Usage: " + sys.argv[0] + " [M] [N]"
   print "where: M is number of loop iterations"
   print "       N is number of nodes in loop"
   sys.exit(0)
else:
   M = int( sys.argv[1] )
   N = int( sys.argv[2] )

print "Using M=" + str(M) + " N=" + str(N)

threadx = threadingx.ThreadingX()

try:
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
finally:
   threadx.shutdown()

