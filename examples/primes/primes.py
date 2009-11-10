import os
import sys
import math

def getprimes( num ):
   sqrtnum = int(math.sqrt(num))
   potentialprimes = [ True for i in range(0,num + 1) ]
   for i in range(2, sqrtnum):
      if potentialprimes[i]:
         j = i * 2
         while j <= num:
            potentialprimes[j] = False
            j = j + i

   i = 0
   primes = []
   for boolean in potentialprimes:
      if boolean:
         primes.append( i )
      i = i + 1

   return primes

def go():
   num = 1000000
   print len(getprimes(num))

if __name__ == '__main__':
   go()

