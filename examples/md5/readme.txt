md5 benchmark
-------------

Generates a random string of 100,000 characters, then returns the md5 hexdigest.

Does this  4 times, in different threads.

Compare classic python threads with threadx.

Results on eeepc 901 running Ubuntu Jaunty:

> time python md5classicthreads.py 

real	0m8.357s
user	0m7.832s
sys	0m1.268s

> time python threadxmd5.py 

real	0m5.154s
user	0m8.989s
sys	0m0.212s

Eeepc has two cores, so this sounds about right.  Note that there is a slight overhead for threadx for process spawning, compared to classic threads, but then the thread runs a lot faster, since it is not blocked by the global interpreter lock.

Note that whilst the user time is slightly more for threadingx - because of the process setup overhead - the real  time is nearly half.

