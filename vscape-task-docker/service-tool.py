from etcd import Client
import simplejson as json
import sys

if len(sys.argv) < 3:
    print "Usage: service-tool.py ip port command args"
    sys.exit(0)
ip = sys.argv[1]
port = int(sys.argv[2])
cmd = sys.argv[3]
try:
    params = sys.argv[4:]
except:
    params = None




class HorizonStatus(object):
    def __init__(self,client):
            self._client = client
    def get_services(self):
        return "\n".join( [ str(l.key.split("/")[-1]) for l in client.read("/horizon/services").leaves ])

    def get_service_config(self,service_name):
        file = "config"
        path="/horizon/services/%s/%s"  %(service_name,file)
        value = client.read(path).value

        return json.loads(value.replace("'","\""))

    def get_tasks(self,service_name):
        path="/horizon/services/" + service_name
        tasks = []
        for l in client.read(path).leaves:
            if l.key.find("task") > -1:
                k = l.key.split("/")[-1]
                #v=json.loads(l.value.replace("'","\""))
                #tasks[k]=v
                tasks.append(k)

        return {"name":service_name,"tasks":tasks}

    def get_file(self,service_name,task_name,file):
        path="/horizon/services/%s/%s/%s" % (service_name,task_name,file)
        resp = self._client.read(path)

    def delete_service(self,service_name):
        path="/horizon/services/" + service_name
        self._client.delete(path,dir=True,recursive=True)

    def purge_service_directory(self,service_name):
        path="/horizon/services/" + service_name
        self._client.delete(path,dir=True,recursive=True)
        pass


def get_file(params):
    global vs
    service_name = params[0]
    task_name = params[1]
    file = params[1]
    print vs.get_file(service_name,task_name,file)

def service_info(params):
    global vs
    service_name = params[0]
    config = vs.get_service_config(service_name)
    print config

def delete_service(params):
    global vs
    service_name = params[0]
    vs.delete_service(service_name)
def list_services(params):
    global vs
    services = vs.get_services()
    print services

def list_tasks(params):
    global vs
    service_name=params[0]
    tasks = vs.get_tasks(service_name)
    print tasks

def help(params):
    global command_router
    print command_router.keys()

command_router = {
    "list-services":list_services
    ,"list-tasks":list_tasks
    ,"delete-service":delete_service
    ,"service-info":service_info
    ,"get-file":get_file
    ,"help":help
}
client = Client(ip,port)
vs = HorizonStatus(client)
action = command_router.get(cmd)
action(params)


