import sys
import os

from threadingxlib import *

class MainService:
   def oninit(self, threadx):
      self.threadx = threadx
      self.children = []
      for i in range(4):
         child = self.threadx.spawn('threadxmd5child')
         child.go()
         self.children.append(child)

   def finished( self, sender, md5hash ):
      print md5hash
      self.children.remove( sender )
      if len( self.children ) == 0:
         self.threadx.shutdownnow()

threadingx.ThreadingX( MainService() )

