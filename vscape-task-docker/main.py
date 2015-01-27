from random import randint
from docker import Client
from container import DockerTask,Executor
import unittest
import psutil
c = Client(base_url='unix://var/run/docker.sock')

# google style guidelines : https://google-styleguide.googlecode.com/svn/trunk/pyguide.html#Nested/Local/Inner_Classes_and_Functions 
#t=DockerTask(container,cmd)
#t._type="docker"
#Executor.run(t)
#	register t 
#	execute t 
#	deregister t 




client =  Client(base_url='unix://var/run/docker.sock')
cmd='sleep 5m'
task=DockerTask("ubuntu:10.04",cmd)
executor = Executor("serviceId&id=0",["service=executor","host=127.0.0.1"])
# executor.register("etcd://")
executor.runTask("ubuntu:10.04","sleep 5m")
executor.waitForExit()


