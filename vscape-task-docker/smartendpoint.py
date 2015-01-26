from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import SimpleHTTPServer
import SocketServer
import sys 
import unittest 
import simplejson as json
#handler=SimpleHTTPServer.SimpleHTTPRequestHandler


"""
	curl -X GET http://127.0.0.1:9999/api/v1/
	
	tasks -  ["name1","name2","name3" ... ]  
	stats - [ {"pid": ... ,
	]
	
"""
class RouteManager(object):
	def __init__(self):
		self._routes = {} 
	def addRoute(self,path,action):
		self._routes[path]=action 

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
	
class  RouteActionHandler(BaseHTTPRequestHandler):
	def __init__(self,request,client_address,server):
		super(BaseHTTPRequestHandler).__init__(request,client_address,server)
		self._data = None 
		print "moo moo!" 

	def setData(self,data):
		data["path"]=self.path 
		self._data = json.dumps(data) 
		pass
	def do_GET(self):
		self.send_response(200) 
		self.send_header("Content-Type","application/json")	
		self.end_headers()
		self.wfile.write(self._data)

class SmartEndPoint(HTTPServer):
	allow_reuse_address = True 
	def finish_request(self,request,client_address):
		super(HTTPServer).finish_request(request,client_address) 
	def shutdown(self):
		self.socket.close() 
	
ip="127.0.0.1"
port=int(sys.argv[1]) 

httpd = SmartEndPoint((ip,port),RouteActionHandler) 
httpd.serve_forever() 


#httpd=SocketServer.TCPServer((ip,port),JsonHandler)
#httpd.serve_forever() 

#if __name__ == '__main__':
#	unittest.main()
