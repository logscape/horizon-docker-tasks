


# Concepts 
 The  docker task executor runs a command inside a container. You can think of your container as the execution context for your task. The container provides the runtime environment for your task to execute successfully.

 ![Overview](/docs/images/components.png)

When your docker task starts it registers itself with the Horizon namespace within the service registry backend. The current service registry used is etcd; there are plans to support others. Each executor maps a running task onto a service and task. Service and task info, task metrics are stored in etcd and persist for the duration of the task's execution. 


## Smart End Points

A smart end-point is registered wih a task. You can access task metrics and status information through it's rest api. The host and port numbers are both stored in etcd for each task. Forexample, to get the task info use the following curl command. 

	curl -X GET http://127.0.0.1:31961/info

This will respond with the host, port and the service owning the tasks. 

	{"info": {"host": "127.0.0.1", "name": "service-7024-645", "port": 31961}}


# Getting Started 
## 0. Prequisites 

The docker task executer has the following python dependencies. Make sure that the following libraries are installed on your system. 

	pip install docker-py
	pip install python-etcd 
	pip install psutils 

This is a quick getting started guide using a mysql container.

## 1. Start Etcd Cluster 

The quickest way to get an etcd cluster up and running is to install it via the container. 

	export PUBLIC_IP=192.168.0.10
	docker run -d -p 8001:8001 -p 5001:5001 quay.io/coreos/etcd:v0.4.6 -peer-addr ${PUBLIC_IP}:8001 -addr ${PUBLIC_IP}:5001 -name etcd-node1
	docker run -d -p 8002:8002 -p 5002:5002 quay.io/coreos/etcd:v0.4.6 -peer-addr ${PUBLIC_IP}:8002 -addr ${PUBLIC_IP}:5002 -name etcd-node2 -peers ${PUBLIC_IP}:8001,${PUBLIC_IP}:8002,${PUBLIC_IP}:8003
	docker run -d -p 8003:8003 -p 5003:5003 quay.io/coreos/etcd:v0.4.6 -peer-addr ${PUBLIC_IP}:8003 -addr ${PUBLIC_IP}:5003 -name etcd-node3 -peers ${PUBLIC_IP}:8001,${PUBLIC_IP}:8002,${PUBLIC_IP}:8003

 Make sure the etcd cluster is running by requesting the leader summary. 

	curl -L $PUBLIC_IP:5001/v2/stats/leader 

 See the [running etcd in containers ](https://coreos.com/blog/Running-etcd-in-Containers/) page for more. 

## 2. Download docker-task-executor 

Download the docker task executor. 

	https://github.com/logscape/horizon-docker-tasks.git

The docker task executor includes main.py and the service-tool for querying the service registry. 

##3. Start Your Docker Task

To execute a docker task you will need to specify a container and the command to run in the container. Here's a trivial example exeucting a the sleep command. 

	sudo python main.py ubuntu:10.04 "sleep 5m" 

To start a longer running task like a database you would need to pass the command specified in the DockerFile. The example below uses (tutum's mysql image)https://github.com/tutumcloud/tutum-docker-mysql. This container uses a run script which starts all the mysql daemons. 

	sudo python main.py tutum/mysql:5.6 "./run.sh"


##4. Access Task Metrics and Status using the Rest API 

Using the mysql example, we see the smart end-point is started on port 33015. You can curl the task metrics in the following manner.

	curl -X GET http://$PUBLIC_IP:$33015/metrics

You will get the following response.


	{"task-1533-1066": [{"process.pid": 9429, "process.cpu.percent": 0.0, "process.context_switches.involuntary": 6, "process.rss.mb": 0, "process.context_switches.voluntary": 904, "process.cmdline": "/bin/sh/usr/bin/mysqld_safe", "process.memory.percent": 0.0, "process.name": "mysqld_safe"}, {"process.pid": 10490, "process.cpu.percent": 0.0, "process.context_switches.involuntary": 1, "process.rss.mb": 0, "process.context_switches.voluntary": 17, "process.cmdline": "tail-F/var/log/mysql/error.log", "process.memory.percent": 0.0, "process.name": "tail"}, {"process.pid": 11457, "process.cpu.percent": 0.0, "process.context_switches.involuntary": 3, "process.rss.mb": 449, "process.context_switches.voluntary": 34, "process.cmdline": "/usr/sbin/mysqld--basedir=/usr--datadir=/var/lib/mysql--plugin-dir=/usr/lib/mysql/plugin--user=mysql--log-error=/var/log/mysql/error.log--pid-file=/var/run/mysqld/mysqld.pid--socket=/var/run/mysqld/mysqld.sock--port=3306", "process.memory.percent": 0.0, "process.name": "mysqld"}]}

Requesting task metrics will report on each process running within a docker container. Normally With complex applications like databases multiple processes will be running within your container. 

## Getting the Address of the Smart End-Point

Use the service-tool to get the host and port of the smart end-point. List the services.

 ./service-tool list-services 

then run service-info on your service. 

 ./service-tool service-info 

which will return the host,port and service name. 


##5. Access Task Metrics and Status through etcd 

Each task will publish the following information to etcd. The *status* file contains a message indiciating the health of the contaienr. 
	/service-XXXX-XXXX
	    /task-123-345
	        |-status 
                |-metrics 
                |-info

The *metrics* file has a list of all cpu,mem, disk utilization of the processes running in the docker task and the *info* file containes general service/task info. These files are updated every 20 seconds. An audit of the tasks run and their health metrics can be quickly scripted using curl and shell scripts. 


##6. Service Tool.

The service-tool reports which services and tasks have been registered with Horizon. Here are few usage examples.

### Service Info

	./service-tool service-info 

### List Services 

	./service-tool list-services

Example output 

	service-7024-645
	service-3072-1179

## List Tasks for a services		
	
	./service-tool list-tasks

Replies with the following task-ids 

	{'tasks': [u'task-3675-9288'], 'name': 'service-3072-1179'}





