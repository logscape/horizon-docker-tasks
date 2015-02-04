__author__ = 'gomoz'


import unittest
import etcd
from registry import Registry
import simplejson as json




class TestEtcdRegistry(unittest.TestCase):

    def setUp(self):
        self._registry = Registry("10.28.1.159",5001)
        self._client = self._registry._client
        self.directory = "/test/"
        self.service_directory="/horizon/services/"
        self.file  = "/test/file1"
        self.map = {"name":"service-0"}


    def tearDown(self):
        try:
            self._client.delete(self.directory,dir=True,recursive=True)
        except KeyError:
            print "Keys not found [%s]" % self.directory

        try:
            self._client.delete(self.service_directory,dir=True,recursive=True)
        except KeyError:
            print "Keys not found [%s]" % self.service_directory

    def test_add_service(self):
        print "[test/start] test_add_service"
        registry = self._registry
        service_name = "service-000"
        registry.add_service(service_name,{})
        services = None
        r = self._client.read("/horizon/services/")
        services = [ l.key.split("/")[-1] for l in r.leaves]
        print "[test/end] test_add_service"
        self.assertTrue(service_name in services)

    def  test_del_service(self):
        print "[test/start] test_del_service"
        registry = self._registry
        service_name_1 = "service-000"
        service_name_2 = "service-001"
        registry.add_service(service_name_1,{})
        registry.add_service(service_name_2,{})
        registry.del_service(service_name_1)
        services = None
        r = self._client.read("/horizon/services/")
        services = [ l.key.split("/")[-1] for l in r.leaves]
        print "[test/end] test_add_service"
        self.assertTrue(service_name_1 not in services)


    def test_del_task(self):
        registry = self._registry
        service_name = "service-000"
        task_name_1 = "task-000"
        task_name_2 = "task-001"
        registry.add_service(service_name,{})
        registry.add_task(service_name,task_name_1,{})
        registry.add_task(service_name,task_name_2,{})
        registry.del_task(service_name,task_name_1)
        tasks = [l.key.split("/")[-1]  for l in self._client.read("/horizon/services/%s" % (service_name)).leaves ]

        self.assertTrue( task_name_1 not in tasks  )

    def test_add_two_services(self):

        registry = self._registry
        service_name1 = "service-000"
        service_name2 = "service-001"
        registry.add_service(service_name1,{})
        registry.add_service(service_name2,{})
        services = None
        r = self._client.read("/horizon/services/")
        services = [ l.key.split("/")[-1] for l in r.leaves]
        print "[test/end] test_add_service"
        self.assertTrue([service_name1,service_name2] ==  services,"%s != %s" % ([service_name1,service_name2],services))


    def test_add_task(self):
        registry = self._registry
        service_name = "service-000"
        task_name = "task-000"
        registry.add_service(service_name,{})
        registry.add_task(service_name,task_name,{})
        result = self._client.read("/horizon/services/%s/%s/info" % (service_name,task_name))
        self.assertTrue( result.value != None )

    def test_get_taskinfo(self):
        registry = self._registry
        service_name = "service-000"
        task_name = "task-000"
        task_info = {"name":task_name, "rest_endpoint":8000 }
        registry.add_service(service_name,{})
        registry.add_task(service_name,task_name,task_info)


        result = self._client.read("/horizon/services/%s/%s/info" % (service_name,task_name))
        actual = json.loads(result.value.replace("'","\""))
        expected = registry.get_task_info(service_name,task_name)
        self.assertEquals(expected,actual)

    def test_get_taskinfo_endpoint(self):
        registry = self._registry
        service_name = "service-000"
        task_name = "task-000"
        task_info = {"name":task_name, "rest_endpoint":8000 }
        registry.add_task(service_name,task_name,task_info)
        result = self._client.read("/horizon/services/%s/%s/info" % (service_name,task_name))
        actual = json.loads(result.value.replace("'","\""))
        expected = registry.get_task_info(service_name,task_name)
        self.assertEquals(task_info["rest_endpoint"],actual["rest_endpoint"])


    def test_write(self):
        registry = self._registry
        file = self.file
        registry.write(file,0)
        self.assertTrue(registry.key_exists(file))

    def test_read(self):
        registry = self._registry
        file = self.file
        self._client.write(file,0)
        expected = self._client.read(file).value
        actual = registry.read(file)
        self.assertEquals(actual,expected)

    def test_key_exists(self):
        registry = self._registry
        file = self.file
        self._client.write(file,0)
        self.assertTrue(registry.key_exists(file))

def suite():
    """
        Gather all the tests from this module in a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestEtcdRegistry))
    test_suite.addTest(unittest.makeSuite(TestRegistry))
    return test_suite

if __name__ == '__main__':
    unittest.main()