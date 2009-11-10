import sys
import os
import md5
import string
import random

import threading

class Md5Thread(threading.Thread):
   def run(self):
      randomstring = ''
      for i in range(100000):
         randomstring = randomstring + string.letters[random.randint(0,25)]
      self.result = md5.md5(randomstring).hexdigest()

def go():
   threads = []
   for i in range(4):
      newthread = Md5Thread()
      newthread.start()
      threads.append(newthread)
   for thread in threads:
      thread.join()
      print thread.result

if __name__ == '__main__':
   go()

