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


client = Client(ip,port)

class VScapeStatus(object):
    def __init__(self,client):
            self._client = client
    def get_services(self):
        return "\n".join( [ str(l.key.split("/")[-1]) for l in client.read("/vscape/services").leaves ])

    def get_service_config(self,service_name):
        file = "config"
        path="/vscape/services/%s/%s"  %(service_name,file)
        value = client.read(path).value

        return json.loads(value.replace("'","\""))

    def get_tasks(self,service_name):
        path="/vscape/services/" + service_name
        tasks = {}
        for l in client.read(path).leaves:
            if l.key.find("task") > -1:
                k = l.key.split("/")[-1]
                v=json.loads(l.value.replace("'","\""))
                tasks[k]=v

        return {"name":service_name,"tasks":tasks}

    def delete_service(self,service_name):
        path="/vscape/services/" + service_name
        self._client.delete(path,dir=True,recursive=True)

    def purge_service_directory(self,service_name):
        path="/vscape/services/" + service_name
        self._client.delete(path,dir=True,recursive=True)
        pass


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

def help():
    pass
vs = VScapeStatus(client)

command_router = {
    "list-services":list_services
    ,"list-tasks":list_tasks
    ,"delete-service":delete_service
    ,"service-info":service_info
    ,"help":help
}

action = command_router.get(cmd)
action(params)


