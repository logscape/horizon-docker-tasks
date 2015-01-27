from time import sleep
from random import randint
from docker import Client
from smartendpoint import RouteActionHandler,RouteManager,SmartEndPoint
import unittest
import psutil
from threading import Thread


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
        self._server_thread = None
        self.STATUS_CHECK_MS=5
        self.start_rest_api(33333)
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

    def action_default(self,data=None):
        data = {"tags":self._tags, "serviceId":self._serviceId,"running":self._running}
        return data

    def action_running(self,data=None):
        return self._running

    def action_stats(self,data=None):
        stats={}
        """for task_id in self._running:
            for process_info in self._client.top(task_id)["Processes"][0]:
                pid=process_info[1]
                p = psutil.Process(pid)

            metrics = {}
            metrics
            stats[task_id] = {}

            stats.append()"""
        return self._client.top(task_id)["Processes"]

    def start_rest_api(self,port):
        route_manager=RouteManager()
        route_manager.addRoute("/",self.action_default)
        route_manager.addRoute("/running",self.action_running)
        route_manager.addRoute("/stats",self.action_stats)

        ip="127.0.0.1"
        port=33333
        httpd = SmartEndPoint((ip,port),RouteActionHandler,route_manager)
        print "[SmartEndPoint] Starting ... %s" % port
        self._server_thread=Thread(target=httpd.serve_forever,args=[])
        #httpd.serve_forever()
        self._server_thread.start()
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


class DockerTask(Task):
    def __init__(self,container,cmd):
        """
            container -  The container which executes the argument
        """
        self._tags = ["service","task"]
        #print "Creating Client"
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
        #print "Executing Starting %s with %s "	 % (self._task_id,self._cmd)

        #self._client.create_container("ubuntu:10.04",self._cmd,name=self._task_id)
        c_info = self._client.create_container(self._container,self._cmd,name=self._task_id)
        self._containerId = c_info["Id"]
        self._client.start(self._task_id)

    def stop(self):
        #print "[stop] Stopping %s " % self._task_id
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