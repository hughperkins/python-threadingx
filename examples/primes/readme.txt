Performance benchmark using prime numbers
=========================================

What is this?
-------------

We calculate prime numbers using a basic sieve of Arystophenes.

We do this several times, in multiple processes.

We have one example where each process is a standard python thread.

We have another where each process is a threadingx process.

Then, we can compare the execution time.

On a multi-core system, using threadingx results in a faster overall execution time.

To run using normal python threads:
-----------------------------------

   python threadedprimes.py

On linux, you can do:

   time python threadedprimes.py

... to measure execution time


To run using threadx:
---------------------

   python threadxprimes.py

On linux you can do:

   time python threadxprimes.py

... to measure execution time

