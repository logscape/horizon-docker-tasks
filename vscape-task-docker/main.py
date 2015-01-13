
from random import randint 
from docker import Client
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


	
class TestDockerTaskExecutor(unittest.TestCase):

	def register(self):
		pass 
	def setUp(self):
		self.client =  Client(base_url='unix://var/run/docker.sock')
		self.cmd='sleep 5m' 
		self.executor=DockerTaskExecutor("ubuntu:10.04")
		# task id is the container id 
	
	def tearDown(self):
		client=self.client
		for cInfo in client.containers(self):
			cID=cInfo['Id'] 
			print "[tearDown] Stopping %s " %cID
			client.stop(cID) 


	def testTaskId(self):
		executor=self.executor
		name = executor.taskId() 
		self.assertTrue(name.find("name") > -1," %s is incorrect" % name ) 
		
	def testRunTask(self):
		executor = self.executor 
		executor.runTask(self.cmd) 
		taskId = executor.taskId() 
		self.assertTrue(executor.client().top(taskId) != None) 	

	def testStopTask(self):
		executor = self.executor 
		executor.runTask(self.cmd) 
		taskId = executor.taskId() 
		executor.stop() 
		containerNames = [c["Names"][0][1:]  for c in executor._client.containers() ]
		self.assertTrue( taskId not in containerNames , " container names : %s " % str(containerNames)  ) 
		

	def testGetStats(self):
		executor = self.executor
		executor.runTask(self.cmd) 
		stats=executor.getStats()
		executor.stop() 
		print stats 
		self.assertTrue ( stats != None ) 


# Task Executor Registers with etcd, kv store , logscape etc 
class TaskExecutor(object):
	def __init__(self):
		self.client =  Client(base_url='unix://var/run/docker.sock')
class DockerUniqueNamer(object):
	name = "" 
	@staticmethod
	def get():
		DockerUniqueNamer.name="name-%s-%s" %  (str(randint(0,10000)),str(randint(0,10000)))
		return "%s" % DockerUniqueNamer.name 

class DockerTaskExecutor(TaskExecutor):
	def __init__(self,container):
		"""
			container -  The container which executes the argument 
		"""
		print "Creating Client" 
		self._client =  Client(base_url='unix://var/run/docker.sock')
		self._task_id = DockerUniqueNamer.get() 

	# TODO: Only run one task at a time per Executor 
	def runTask(self,cmd):
		"""
			cmd  - The command to execute
			     - If the command is NULL, then the containers default command will be executed 

			throws - API error 
		"""
		print "Executing Starting %s with %s "	 % (self._task_id,cmd)
		
		self._client.create_container("ubuntu:10.04",cmd,name=self._task_id)
		self._client.start(self._task_id)  
	def stop(self):
		print "[stop] Stopping %s " % self._task_id 
		self._client.stop(self._task_id) 
	
	def getStats(self):
		print self._client.top(self._task_id) 
		# This is dependent on the version of PS 
		pids=[ int(p[1]) for p in self._client.top(self._task_id)['Processes'] ]
		print pids 
		stats=[]
		for pid in pids:
			p=psutil.Process(pid) 
			s={} 
			s["status"]=p.status
			s["cpu"]=p.get_cpu_percent(interval=1.0) 
			s["mem"]=p.get_memory_percent()
			s["rss"] = p.get_memory_info().rss
			s["read_bytes"]=p.get_io_counters().read_bytes
			s["write_bytes"]=p.get_io_counters().write_bytes
			s["cwd"]=p.getcwd() 
			stats.append(s) 

		return stats 
	
	def client(self):
		return self._client
	def taskId(self):
		return self._task_id

#
client =  Client(base_url='unix://var/run/docker.sock')
cmd='sleep 5m' 
executor=DockerTaskExecutor("ubuntu:10.04")
def setUp():
	global executor 
	executor.runTask("sleep 3m") 

def tearDown():
	global executor
	executor.stop() 


if __name__ == '__main__':
	setUp()
	unittest.main() 
	tearDown() 
