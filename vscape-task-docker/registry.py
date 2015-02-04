__author__ = 'gomoz'


from etcd import Client,EtcdException
import simplejson as json
import logging
module_logger = logging.getLogger('service-registry')

class Registry(object):
    SERVICE_DIRECTORY = "/horizon/services"
    def __init__(self,ip,port):
        self._client = Client(ip,port)

    def create_directory(self,k,v):
        try:
            self._client.write(k,v,dir=True)
        except EtcdException,e:
            errorMessage = str(e) + "\n"
            errorMessage = "%s  [Registry] write %s = %s " % (errorMessage,k,v)
            module_logger.fatal("[registry] write %s=%s" % (errorMessage,k,v))
            raise EtcdException(errorMessage)

    def read(self,k):
        return self._client.read(k).value

    def write(self,k,v):
        try:
            self._client.write(k,v)
        except EtcdException,e:
            errorMessage = str(e) + "\n"
            errorMessage = "%s %s" % (errorMessage,"[Registry] write %s = %s" % (k,v))
            raise EtcdException(errorMessage)

    def add_task(self,service_name,task_name,info):
        path ="%s/%s/%s/info" % (Registry.SERVICE_DIRECTORY,service_name,task_name)
        self.write(path,info)
    def del_task(self,service_name,task_name):
        path ="%s/%s/%s" % (Registry.SERVICE_DIRECTORY,service_name,task_name)
        self._client.delete(path,dir=True,recursive=True)

    def get_task_info(self,service_name,task_name):
        task_file ="%s/%s/%s/info" % (Registry.SERVICE_DIRECTORY,service_name,task_name)
        result=self.read(task_file)
        result=result.replace("\'","\"")
        return json.loads(result)

    def add_service(self,name,value):
        service_directory ="%s/%s/" % (Registry.SERVICE_DIRECTORY,name)
        self.create_directory(service_directory,value)

    def del_service(self,name):
        service_directory ="%s/%s/" % (Registry.SERVICE_DIRECTORY,name)
        self._client.delete(service_directory,dir=True,recursive=True)


    def key_exists(self,k):
        client = self._client
        try:
            client.read(k)
        except KeyError:
            return False
        return True
