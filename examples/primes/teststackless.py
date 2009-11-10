import sys
import os

import stackless

import primes

def primethread():
   

def go():
   thread1 = stackless.tasklet(primethread)
   primes.go( 1000000 )

if __name__ == '__main__':
   go()

