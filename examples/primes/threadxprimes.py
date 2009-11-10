import sys
import os

from threadingxlib import *

num = 200000

class MainService:
   def oninit(self, threadx):
      self.threadx = threadx
      self.children = []
      for i in range(4):
         child = self.threadx.spawn('threadxprimechild')
         child.go( num )
         self.children.append(child)

   def finished( self, sender, numprimes ):
      print numprimes
      self.children.remove( sender )
      if len( self.children ) == 0:
         self.threadx.shutdownnow()

threadingx.ThreadingX( MainService() )

