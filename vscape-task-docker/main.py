from random import randint
from docker import Client
from container import DockerTask,Executor
import sys
import unittest
import psutil
c = Client(base_url='unix://var/run/docker.sock')


if len(sys.argv) < 1:
    print "Usage: executor container 'command'"
    import sys;sys.exit(0)

client =  Client(base_url='unix://var/r'
                          'un/docker.sock')

container = sys.argv[1]
cmd= sys.argv[2]


if len(sys.argv) > 2:
	container = sys.argv[1] 

	
print sys.argv

task=DockerTask("ubuntu:10.04",cmd)
executor = Executor("serviceId&id=0",["service=executor","host=127.0.0.1"])
try:
    executor.register("etcd://10.28.1.159:5001")
    executor.runTask(container,cmd)
    executor.waitForExit()
    executor.shutdown()
except Exception,e:
    print "Something bad happened : %s " % str(e)
    executor.shutdown()
