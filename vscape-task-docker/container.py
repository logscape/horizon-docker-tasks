from time import sleep
from random import randint
from docker import Client
from smartendpoint import RouteActionHandler,RouteManager,SmartEndPoint

import unittest
import psutil
import etcd
from registry import  Registry


from threading import Thread,Timer


class DockerUniqueNamer(object):
    name = ""
    @staticmethod
    def get(tags=None):
        if tags==None:
            tags=["name"]
        tagStr="-".join(tags)
        DockerUniqueNamer.name="%s-%s-%s" %  (tagStr,str(randint(0,10000)),str(randint(0,10000)))
        return "%s" % DockerUniqueNamer.name


class ServiceUniqueNamer(object):
    name = ""
    @staticmethod
    def get(tags=None):
        if tags==None:
            tags=["service"]
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
        self._service_name  = ServiceUniqueNamer.get()
        self._restapi_port = randint(30000,40000)
        self._service_info = {"host":"127.0.0.1","name":self._service_name, "port":self._restapi_port}
        self._registry = None
        self._tags = tags
        self._serviceId = serviceId
        self._running = {}
        self._stopped = []
        self._server_thread = None
        self.STATUS_CHECK_MS=5
        self._last_task_id = -1
        self.httpd = None
        self.start_rest_api(self._restapi_port)
        self.start_publish_thread()
        pass

    def start_publish_thread(self):
        t = Timer(5,self.publish)
        t.daemon = True
        t.start()

    def publish_task_data(self,file_name,task_id,data):
        """route_manager.addRoute("/",self.action_default)
        route_manager.addRoute("/running",self.action_running)
        route_manager.addRoute("/stats",self.action_stats)
        route_manager.addRoute("/metrics",self.action_metrics)
        route_manager.addRoute("/status",self.action_status)
        route_manager.addRoute("/tasks",self.action_tasks)
        route_manager.addRoute("/info",self.action_info)"""
        task_path = "%s/%s/%s/%s" % (self._registry.SERVICE_DIRECTORY,self._service_name,task_id,file_name)
        self._registry._client.write(task_path,data)

    def publish(self):

        for task_id in self._running:
            data = self.action_running(None)
            self.publish_task_data("running",task_id,data)
            data = self.action_stats(None)
            self.publish_task_data("stats",task_id,data)
            data = self.action_metrics(None)
            self.publish_task_data("metrics",task_id,data)
            data = self.action_status(None)
            self.publish_task_data("status",task_id,data)
            data = self.action_tasks(None)
            self.publish_task_data("tasks",task_id,data)
            data = self.action_info(None)
            self.publish_task_data("info",task_id,data)

    def register(self,full_address):
        address = full_address.split("//")[1]
        (ip,port) = address.split(":")
        self._registry = Registry(ip,int(port))
        self._registry.add_service(self._service_name,{})
        full_service_path = self._registry.SERVICE_DIRECTORY + "/" + self._service_name
        self._registry.write(full_service_path + "/config" ,self._service_info)
        print "[Executor::register] %s%s " % (self._service_name,"/config")

    def runTask(self,container,cmd):
        print "[RUNTASK](%s,%s) " % (container,cmd)
        task=DockerTask(container=container,cmd=cmd)
        task.run()
        task_info = {"name":task._task_id , "cmd":cmd , "container":container}
        self._registry.add_task(self._service_name,task._task_id,task_info)
        self._running[task.taskId()] = task
        print "Adding %s" % task.taskId()
        self.last_task_id=task.taskId()

    def stopAll(self):
        """
            Stops all running containers
        :return:
        """
        print "[stopAll] Stopping All %s" % self._running.keys()
        for task_id in self._running.keys():
            self.stop(task_id)

    @property
    def last_task_id(self):
        return self._last_task_id

    @last_task_id.setter
    def last_task_id(self,t_id):
        if t_id in self._running.keys():
            self._last_task_id = t_id
        else:
            return -1


    def clean_dead_tasks(self):
        containers=[ c["Names"][0][1:]  for c in self._client.containers() if len(c["Names"]) > 0 ]
        reap = []
        #print containers
        #print self._running
        for taskId in self._running.keys():
            if taskId not in containers:
                print "schedule [%s] to reap"
                reap.append(taskId)
        for task_id in reap:
            print "reaping [%s]" % task_id
            #self._running.remove(taskId)
            self._running.pop(task_id)
            self._registry.del_task(self._service_name,task_id)


    def stop(self,task_id):
        if task_id in self._running.keys():
            self._client.stop(task_id)
            self._registry.del_task(self._service_name,task_id)
        else:
            raise RuntimeError("Task '%s' is not running in %s " % (task_id,self._running.keys()))


    def waitForExit(self):
        while len(self._running.keys()) > 0:
            print "[waitForExit] Sleeping %s, (%s)" % (self.STATUS_CHECK_SECS, str(self._running.keys()))
            sleep(1.0*self.STATUS_CHECK_SECS)
            self.clean_dead_tasks()
        print "Exiting ... "

    def action_shutdown(self,data=None):
        data = {"message":"shutting down"}
        self.stopAll()
        return data

    def action_default(self,data=None):
        data = {"tags":self._tags, "serviceId":self._serviceId,"running":self._running.keys()}
        return data

    def action_running(self,data=None):
        return {"running":self._running.keys()}

    def action_metrics(self,data=None):
        task_metrics = []
        for task_id in self._running:
            metrics = self._client.top(task_id)["Processes"]
            task_metrics.append({"task_name":task_id,"metrics":metrics})
        return {"service_name":self._service_name , "tasks":task_metrics  }

    def action_stats(self,data=None):
        stats={}
        for task_id in self._running:
            stats[task_id] = []
            for process_info in self._client.top(task_id)["Processes"]:
                metrics = {}
                pid=int(process_info[1])

                try:
                    p = psutil.Process(pid)
                    metrics["process.name"] = p.name()
                    metrics["process.pid"] = p.pid
                    metrics["process.cmdline"] = "".join(p.cmdline())
                    metrics["process.cpu.percent"] = p.cpu_percent(interval=1.0)
                    metrics["process.memory.percent"] = p.cpu_percent()
                    metrics["process.rss.mb"] = p.get_memory_info().rss / (1024 * 1024 )
                    metrics["process.context_switches.voluntary"] = p.num_ctx_switches().voluntary
                    metrics["process.context_switches.involuntary"] = p.num_ctx_switches().involuntary
                    stats[task_id].append(metrics)
                except psutil.NoSuchProcess,messge:
                    print "[stats] Process no longer exists (%s)" % pid


        return stats


    def action_tasks(self,data=None):
        return {"tasks":self._running}

    def action_status(self,data=None):
        return {"status":"good"}

    def action_info(self,data=None):
        return {"info":self._service_info}

    def start_rest_api(self,port):
        route_manager=RouteManager()
        route_manager.addRoute("/",self.action_default)
        route_manager.addRoute("/running",self.action_running)
        route_manager.addRoute("/stats",self.action_stats)
        route_manager.addRoute("/metrics",self.action_metrics)
        route_manager.addRoute("/status",self.action_status)
        route_manager.addRoute("/tasks",self.action_tasks)
        route_manager.addRoute("/info",self.action_info)
        route_manager.addRoute("/shutdown",self.action_shutdown)


        ip="127.0.0.1"

        self.httpd = SmartEndPoint((ip,port),RouteActionHandler,route_manager)
        print "[SmartEndPoint] Starting ... %s" % port
        self._server_thread=Thread(target=self.httpd.serve_forever,args=[])
        #httpd.serve_forever()
        self._server_thread.start()
        pass

    def shutdown(self):
        try:
            self._registry.del_service(self._service_name)
        except KeyError:
            print "[%s] service already deleted " % (self._service_name)

        self.httpd.shutdown()
        #self._server_thread,stop()




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
        self._tags = ["task"]
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
            try:
                s["read_bytes"]=p.get_io_counters().read_bytes
                s["write_bytes"]=p.get_io_counters().write_bytes
                s["cwd"]=p.getcwd()
            except Exception:
                s["read_bytes"]=-1
                s["write_bytes"]=-1
                s["cwd"]="ACCESS DENIED"


            stats.append(s)

        return stats

    def client(self):
        return self._client
    def taskId(self):
        return self._task_id

        #
