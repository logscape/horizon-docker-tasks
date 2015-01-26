from time import sleep
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
"""
	executor = DockerTaskExecutor()
	
	executor.runTask("ubuntu:10.04","hello.sh") 
		Task

"""

class TestExecutor(unittest.TestCase):
    pass


class TestPidStats(unittest.TestCase):
    def setUp(self):
        global executor
        self.executor = executor
    def tearDown(self):
        pass

class TestServiceDiscovery(unittest.TestCase):
    pass

class TestDockerExecutor(unittest.TestCase):
    def setUp(self):
        self.executor =  DockerTaskExecutor()
        self.container = "ubuntu:10.04"
        self.cmd = "sleep 10s"

    def TestRegisterWithEtcd(self):
        executor= self.executor
        executor.register("etcd://127.0.0.1")
        self.assertTrue(False)
    def TestRegisterWithVscape(self):
        executor= self.executor
        executor.register("vscape://127.0.0.1")
        self.assertTrue(False)

    def TestRegisterWithNothing(self):
        executor= self.executor
        executor.register(None)
        self.assertTrue(False)


    def TestGetLastTaskId_ShouldPass(self):
        executor = self.executor
        executor.runTask("sleep 5m")
        taskId = executor.getLastTaskId()
        self.assertTrue ( taskId > -1 )

    def TestGetLastTaskId_ShouldFail_With_MinusOne(self):
        executor = self.executor
        taskId = executor.getLastTaskId()
        self.assertTrue ( taskId == -1 )

    def TestRunTask(self):
        executor = self.executor
        executor.runTask("sleep 5m")
        taskId = executor.getLastTaskId()
        executor.stop(taskId)
        containerNames = [c["Names"][0][1:]  for c in task._client.containers() ]
        self.assertTrue( taskId not in containerNames , " container names : %s " % str(containerNames)  )

    def TestStopAll(self):
        executor = self.executor
        executor.runTask("sleep 5m")
        executor.runTask("sleep 5m")
        executor.stopAll()
        containerNames = [c["Names"][0][1:]  for c in task._client.containers() ]
        self.assertEquals( len(containerNames)  , 0 , " container names : %s " % str(containerNames)  )


    def TestStop(self):
        pass

class TestDockerTask(unittest.TestCase):

    def register(self):
        pass
    def setUp(self):
        self.client =  Client(base_url='unix://var/run/docker.sock')
        self.cmd='sleep 5m'
        self.task=DockerTask("ubuntu:10.04",cmd=self.cmd)
    # task id is the container id

    def tearDown(self):
        client=self.client
        for cInfo in client.containers(self):
            cID=cInfo['Id']
            print "[tearDown] Stopping %s " %cID
            client.stop(cID)


    def testTaskId(self):
        task=self.task
        name = task.taskId()
        self.assertTrue(name.find("name") > -1," %s is incorrect" % name )

    def testRunTask(self):
        task = self.task
        task.run()
        taskId = task.taskId()
        self.assertTrue(task.client().top(taskId) != None)

    def testStopTask(self):
        task = self.task
        task.run()
        taskId = task.taskId()
        task.stop()
        containerNames = [c["Names"][0][1:]  for c in task._client.containers() ]
        self.assertTrue( taskId not in containerNames , " container names : %s " % str(containerNames)  )


    def testGetStats(self):
        task = self.task
        task.run()
        stats=task.getStats()
        task.stop()
        print stats
        self.assertTrue ( stats != None )



client =  Client(base_url='unix://var/run/docker.sock')
cmd='sleep 5m'
task=DockerTask("ubuntu:10.04",cmd)
def setUp():
    global task
    task.run()

def tearDown():
    global task
    task.stop()


def test():
    pass

executor = Executor("serviceId&id=0",["service=executor","host=127.0.0.1"])
executor.runTask("ubuntu:10.04","sleep 5m")
executor.runTask("ubuntu:10.04","sleep 5m")
executor.runTask("ubuntu:10.04","sleep 5m")
executor.waitForExit()


import sys;sys.exit()
if __name__ == '__main__':

    setUp()
    unittest.main()
    tearDown()