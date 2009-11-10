import sys
import os

import threading

import primes

num = 400000

class PrimeThread(threading.Thread):
   def __init__(self, num ):
      threading.Thread.__init__(self)
      self.num = num

   def run(self):
      self.result = len( primes.getprimes(self.num) )

def go():
   threads = []
   for i in range(4):
      newthread = PrimeThread(num)
      newthread.start()
      threads.append(newthread)
   for thread in threads:
      thread.join()
      print thread.result

if __name__ == '__main__':
   go()

