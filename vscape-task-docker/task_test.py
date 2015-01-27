import unittest
from docker import Client
from container import DockerTask


class TestDockerTask(unittest.TestCase):
    def register(self):
        pass

    def setUp(self):
        self.client = Client(base_url='unix://var/run/docker.sock')
        self.cmd = 'sleep 5m'
        self.task = DockerTask("ubuntu:10.04", cmd=self.cmd)

    # task id is the container id

    def tearDown(self):
        client = self.client
        for cInfo in client.containers(self):
            cID = cInfo['Id']
            # print "[tearDown] Stopping %s " %cID
            client.stop(cID)

    def testTaskId(self):
        task = self.task
        name = task.taskId()
        self.assertTrue(name.find("service") > -1, " %s is incorrect" % name)

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
        containerNames = [c["Names"][0][1:] for c in task._client.containers()]
        self.assertTrue(taskId not in containerNames, " container names : %s " % str(containerNames))

    def testGetStats(self):
        task = self.task
        task.run()
        stats = task.getStats()
        task.stop()
        print stats
        self.assertTrue(stats != None)


def suite():
    """
        Gather all the tests from this module in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestDockerTask))
    return test_suite