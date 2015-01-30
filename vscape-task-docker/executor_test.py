from time import sleep
from random import randint
from docker import Client
from container import DockerTask, Executor
import simplejson as json
import unittest
import psutil

class TestDockerExecutorUsingEtcd(unittest.TestCase):

    def setUp(self):
        self.executor = Executor("serviceId&id=0",["service=executor","host=127.0.0.1"])
        self.registryAddress = "etcd://10.28.1.159:5001"
        self.container = "ubuntu:10.04"
        self.cmd = "sleep 10s"

    def tearDown(self):
        self.executor._registry._client.delete("/vscape/services/",dir=True,recursive=True)
        self.executor.shutdown()

    def testRegisterWithEtcd(self):
        executor = self.executor
        executor.register(self.registryAddress)
        self.assertTrue(executor._registry != None)

    def testRegisteredServiceName(self):
        executor = self.executor
        executor.register(self.registryAddress)
        leaves = [l   for l in executor._registry._client.read("/vscape/services/").leaves]
        self.assertTrue(len(leaves) > 0)

    def testRegisteredServiceInfo(self):
        executor = self.executor
        executor.register(self.registryAddress)
        values = [json.loads(l.value.replace("'","\""))   for l in executor._registry._client.read("/vscape/services/").leaves]
        self.assertTrue(len(values[0].keys()) > 0 )


class TestDockerExecutor(unittest.TestCase):

    def setUp(self):
        self.executor = Executor("serviceId&id=0",["service=executor","host=127.0.0.1"])
        self.container = "ubuntu:10.04"
        self.cmd = "sleep 10s"

    def tearDown(self):
        self.executor.shutdown()


    def testRegisterWithNothing(self):
        executor = self.executor
        executor.register(None)
        self.assertTrue(self._registry == None)


    def testGetLastTaskId_ShouldPass(self):
        executor = self.executor
        executor.runTask(container="ubuntu:10.04",cmd="sleep 5m")
        taskId = executor.last_task_id
        self.assertTrue(taskId > -1)

    def testGetLastTaskId_ShouldFail_With_MinusOne(self):
        executor = self.executor
        taskId = executor.last_task_id
        self.assertTrue(taskId == -1)

    def testRunTask(self):
        executor = self.executor
        executor.runTask(container="ubuntu:10.04",cmd="sleep 5m")
        taskId = executor.last_task_id
        running_tasks = [c["Names"][0][1:] for c in executor._client.containers()]
        self.assertTrue( taskId in running_tasks)

    def testStop(self):
        executor = self.executor
        executor.runTask(container="ubuntu:10.04",cmd="sleep 5m")
        task_id = executor.last_task_id
        executor.stop(task_id)
        running_tasks = [c["Names"][0][1:] for c in executor._client.containers()]
        self.assertTrue( taskId  not in running_tasks)

    #def testStopAll(self):
    #    executor = self.executor
    #    executor.runTask(container="ubuntu:10.04",cmd="sleep 5m")
    #    executor.runTask(container="ubuntu:10.04",cmd="sleep 5m")
    #    executor.stopAll()
    #    containerNames = [c["Names"][0][1:] for c in task._client.containers()]
    #    self.assertEquals(len(containerNames), 0, " container names : %s " % str(containerNames))


    def testStop(self):
        pass


def suite():
    """
        Gather all the tests from this module in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestDockerExecutor))
    test_suite.addTest(unittest.makeSuite(TestDockerExecutorUsingEtcd))
    return test_suite

if __name__ == '__main__':
    unittest.main()