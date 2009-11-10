import sys
import os

from threadingxlib import *

class Manager(object):
   def __init__(self):
      self.next = None

   def setmain( self, sender, main ):
      self.main = main

   def setnextnode( self, sender, nextnode ):
      self.nextnode = nextnode

   def relay( self, sender, n ):
      n = n - 1
      print "Manager: " + str(n)
      if n == 0:
         print "Manager: finished"
         self.main.finished()
      else:
         self.nextnode.relay( n )

threadingx.ThreadingX( instance = Manager() )

