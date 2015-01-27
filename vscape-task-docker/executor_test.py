from time import sleep
from random import randint
from docker import Client
from container import DockerTask, Executor
import unittest
import psutil


class TestDockerExecutor(unittest.TestCase):
    def setUp(self):
        self.executor = DockerTaskExecutor()
        self.container = "ubuntu:10.04"
        self.cmd = "sleep 10s"

    def TestRegisterWithEtcd(self):
        executor = self.executor
        executor.register("etcd://127.0.0.1")
        self.assertTrue(False)

    def TestRegisterWithVscape(self):
        executor = self.executor
        executor.register("vscape://127.0.0.1")
        self.assertTrue(False)

    def TestRegisterWithNothing(self):
        executor = self.executor
        executor.register(None)
        self.assertTrue(False)


    def TestGetLastTaskId_ShouldPass(self):
        executor = self.executor
        executor.runTask("sleep 5m")
        taskId = executor.getLastTaskId()
        self.assertTrue(taskId > -1)

    def TestGetLastTaskId_ShouldFail_With_MinusOne(self):
        executor = self.executor
        taskId = executor.getLastTaskId()
        self.assertTrue(taskId == -1)

    def TestRunTask(self):
        executor = self.executor
        executor.runTask("sleep 5m")
        taskId = executor.getLastTaskId()
        executor.stop(taskId)
        containerNames = [c["Names"][0][1:] for c in task._client.containers()]
        self.assertTrue(taskId not in containerNames, " container names : %s " % str(containerNames))

    def TestStopAll(self):
        executor = self.executor
        executor.runTask("sleep 5m")
        executor.runTask("sleep 5m")
        executor.stopAll()
        containerNames = [c["Names"][0][1:] for c in task._client.containers()]
        self.assertEquals(len(containerNames), 0, " container names : %s " % str(containerNames))


    def TestStop(self):
        pass


def suite():
    """
        Gather all the tests from this module in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestDockerExecutor))
    return test_suite