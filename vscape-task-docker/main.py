from time import sleep 
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


class DockerUniqueNamer(object):
	name = "" 
	@staticmethod
	def get(tags=None):
		if tags==None:
			tags=["name"]
		tagStr="-".join(tags) 
		DockerUniqueNamer.name="%s-%s-%s" %  (tagStr,str(randint(0,10000)),str(randint(0,10000)))
		return "%s" % DockerUniqueNamer.name 

class UniqueEndpoint(object):
	""" Smart Endpoints will sit within the port range 
		30000 - 40000
		Providing a capacity of 10000 simoultaneousports 
		A random port is chosen. If there's a bind collision it will be released and another chosen .
	"""
	pass

class SmartEndpoint(object):
	pass 

class Executor(object):
	STATUS_CHECK_SECS=20
	def __init__(self,serviceId,tags=None):
		"""
			serviceId - Logscape's Service Id. Contains bundle and service name
			tags - a list of tags describing the Executor / task being run. 
		"""
		self._client =  Client(base_url='unix://var/run/docker.sock')
		self._tags = tags 
		self._serviceId = serviceId 		
		self._running = [] 
		self._stopped = [] 
		self.STATUS_CHECK_MS=5
		pass
	def register(self,registry):
		pass 
	def runTask(self,container,cmd):
		task=DockerTask(container="ubuntu:10.04",cmd=cmd)
		task.run() 
		self._running.append(task.taskId()) 

	def clean_dead_tasks(self):
		containers=[ c["Names"][0][1:]  for c in self._client.containers() if len(c["Names"]) > 0 ] 
		reap = [] 
		print containers 
		print self._running 	
		for taskId in self._running:
			if taskId not in containers:
				print "schedule [%s] to reap"
				reap.append(taskId) 
		for taskId in reap:
			print "reaping [%s]" % taskId 
			self._running.remove(taskId)

		
			

	def waitForExit(self):
		while len(self._running) > 0:
			sleep(1.0*self.STATUS_CHECK_SECS) 
			self.clean_dead_tasks() 
		print "Exiting ... "

	def createSmartEndpoint(self,port):
		pass 
	


# Task Executor Registers with etcd, kv store , logscape etc 
class Task(object):
	def __init__(self,client=None):
		if client is None:
			self.client =  Client(base_url='unix://var/run/docker.sock')
		else:
			self.client = client 

"""
	/stats
	/tags
	/pids
"""
class SmartEndPoint(object):
	pass

class DockerTask(Task):
	def __init__(self,container,cmd):
		"""
			container -  The container which executes the argument 
		"""
		self._tags = ["service","task"] 
		print "Creating Client" 
		self._client =  Client(base_url='unix://var/run/docker.sock')
		self._task_id = DockerUniqueNamer.get(self._tags) 
		self._cmd=cmd
		self._container=container

	# TODO: Only run one task at a time per Executor 
	def run(self):
		"""
			cmd  - The command to execute
			     - If the command is NULL, then the containers default command will be executed 

			throws - API error 
		"""
		print "Executing Starting %s with %s "	 % (self._task_id,cmd)
		
		#self._client.create_container("ubuntu:10.04",self._cmd,name=self._task_id)
		c_info = self._client.create_container(self._container,self._cmd,name=self._task_id)
		self._containerId = c_info["Id"] 
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
