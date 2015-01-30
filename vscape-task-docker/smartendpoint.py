from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import SimpleHTTPServer
import SocketServer
import sys 
import unittest 
import simplejson as json


"""
	SmartEndPoint exposes a task and service status through a rest api 
"""
class RouteManager(object):
	def __init__(self):
		self._routes = {}
	@staticmethod
	def action_undefined(self,data=None):
		return {"response":"action undefined"}
	def addRoute(self,path,action):
		self._routes[path]=action
	def getAction(self,path):
		if self._routes.has_key(path) is False:
				return RouteManager.action_undefined
		return self._routes[path]

class TestRouterManager(unittest.TestCase):
	def setUp(self):
		pass

	def testRegister(self):	
		def action():
			pass
		rm = RouteManager() 
		r="/tasks"
		rm.addRoute(r,action) 
		self.assertTrue( rm._routes.has_key(r))

	def testRegisterFail(self):
		rm = RouteManager
		method = rm.addRoute
		r = "/tasks"
		m = None
		self.assertRaises(Exception,method,r,m)

	def testRouteUndefined(self):
		rm = RouteManager()
		method = rm.getAction("/")
		self.assertEquals(RouteManager.action_undefined,method)

	
class  RouteActionHandler(BaseHTTPRequestHandler):
	def __init__(self,request,client_address,server,route_manager=None):
		BaseHTTPRequestHandler.__init__(self,request,client_address,server)
		self._route_manager = route_manager


	def execute_action(self):
		action = self.server._route_manager.getAction(self.path)
		result=action(None)
		return result

	def do_GET(self):
		self.send_response(200) 
		self.send_header("Content-Type","application/json")	
		self.end_headers()
		data=self.execute_action()
		data_as_json=json.dumps(data)
		self.wfile.write(data_as_json)

class SmartEndPoint(HTTPServer):
	allow_reuse_address = True

	def __init__(self, server_address, RequestHandlerClass,route_manager):
		self._route_manager = route_manager
		HTTPServer.__init__(self, server_address, RequestHandlerClass)

	def finish_request(self,request,client_address):
		self.RequestHandlerClass(request, client_address, self,self._route_manager)

	#def shutdown(self):
	#	self.socket.close()

#def action_default(data):
#	return {"version":"v1.0","application":"SmartEndPoint"}


#ip="127.0.0.1"
#port=int(sys.argv[1])

#port=33333
#routeManager=RouteManager()
#routeManager.addRoute("/",action_default)
#httpd = SmartEndPoint((ip,port),RouteActionHandler,routeManager)
#httpd.serve_forever()


#httpd=SocketServer.TCPServer((ip,port),JsonHandler)
#httpd.serve_forever() 

if __name__ == '__main__':
	unittest.main()
