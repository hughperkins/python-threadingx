import sys
import os

from threadingxlib import *

class Worker(object):
   def __init__(self):
      self.next = None

   def setnextnode( self, sender, nextnode ):
      self.nextnode = nextnode

   def relay( self, sender, n ):
      print "worker: " + str(n)
      self.nextnode.relay( n )

threadx = threadingx.ThreadingX()
threadx.register_instance(Worker())
while threadx.receive():
   pass
threadx.shutdown()

