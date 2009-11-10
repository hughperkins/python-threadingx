Performance benchmark using prime numbers
=========================================

What is this?
-------------

We calculate prime numbers using a basic sieve of Arystophenes.  We do this several times, in multiple processes.

We have one implementation using classic Python threads, and one using threadingx.

Results for eeepc 901 running Ubuntu Jaunty:

> time python primesclassicthreads.py

real	0m7.110s
user	0m5.828s
sys	0m2.040s

> time python threadxprimes.py 

real	0m3.626s
user	0m6.288s
sys	0m0.288s

You can see that the user time is similar in both cases, but the elapsed time is less in threadx, nearly half, which one can suppose is because it is making use of both cores, whereas the classically-threaded example is being blocked by the global interpreter lock.

To run using normal python threads:
-----------------------------------

   python primesclassicthreads.py

On linux, you can do:

   time python primesclassicthreads.py

... to measure execution time


To run using threadx:
---------------------

   python threadxprimes.py

On linux you can do:

   time python threadxprimes.py

... to measure execution time

