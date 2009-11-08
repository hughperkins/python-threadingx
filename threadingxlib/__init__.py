"""
threadingx

Summary
-------

threadingx is designed to emulate some of the threading functionality 
in Erlang.

It makes it easy to spawn new processes, and communicate with them.

Details
-------

Each process is a full-blown Python process, so can run independently on
multi-core hardware.

This contrasts with micro-threading ('green thread') approaches where 
the python global interpreter lock (GIL) means that the green threads
 all run in essentially a single operating system thread, and cannot 
take advantage of multi-core systems.

Communications use sockets, for portability.  Marshalling is done using 
pickle.

Example
-------

For an example usage, please see the ping-pong example.

Usage
-----

Initialization:
---------------

threadingx.init()

Shutdown:
---------

threadingx.shutdown()

This will clean up sockets and child processes

Starting and calling other processes:
-------------------------------------

Spawn a module as a new process:
child = threadingx.spawn('modulename')

Call a function in the child:
threadingx.somefunction( child, arg1, arg2, ...)

Making methods available to other processes:
--------------------------------------------

Register object, with methods that other processes can call:
threadingx.register_instance(someobject)

Receive an incoming message:
----------------------------

threadingx.receive()

If this returns False, the child has received a shutdown
from its parent, and appropriate behavior is to call 
threadingx.shutdown(), then exit.

Registry
--------

Add a process to the registry:
registrylib.register('somename', someprocess)

Lookup a process in the registry (note: synchronous):
child = registrylib.lookup('somename')

"""

__all__ = ['registrylib','threadingx']

