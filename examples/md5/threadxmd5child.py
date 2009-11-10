import sys
import os
import md5
import random
import string
import md5

from threadingxlib import *

class Md5Child(object):
   def go(self, sender ):
      randomstring = ''
      for i in range(100000):
         randomstring = randomstring + string.letters[random.randint(0,25)]
      sender.finished( md5.md5(randomstring).hexdigest() )

threadingx.ThreadingX( Md5Child() )


