import sys
import os

from threadingxlib import *

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

class Main(object):
   def oninit(self, threadx ):
      self.threadx = threadx
      previousworker = None
      firstworker = None
      for n in xrange(0, N - 1):
         worker = self.threadx.spawn('worker')
         if previousworker != None:
            previousworker.setnextnode( worker )
         else:
            firstworker = worker
         previousworker = worker
      manager = self.threadx.spawn('manager')
      manager.setmain( self.threadx.getme() )
      previousworker.setnextnode( manager )
      manager.setnextnode( firstworker )

      firstworker.relay( M )

   def finished( self, sender ):
      self.threadx.shutdownnow()

threadingx.ThreadingX( instance = Main() )

