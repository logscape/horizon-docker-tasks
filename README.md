
Getting started with horizon's docker-task-executor. 


# Concepts 
 A docker task executor  is a command that is executed inside a container. You can think of your container as the execution context for your task. The container provides the runtime environment for your task to execute successfully.

 ![Overview](/docs/images/overview.png)

When your docker task starts it registers with the horizon namespace in etcd. Each executor maps a running task onto a service and task. Service and task info, task metrics are stored in etcd and persist for the duration of the tasks execution. 


## Smart End Points

A smart end point is registered wih a task. You can access task metrics and status information through it's rest api. The host and port numbers are both stored in etcd for each task. 

# 0. Prequisites 

The docker task executer has the following dependencies. Make sure that the following libraries are installed on your system. 

	pip install docker-py
	pip install python-etcd 
	pip install psutils 

This ia quick getting started guide using a mysql container.

# 1. Start Etcd Cluster 

The quickest way to get a etcd cluster up and running is to install it via the container. 

	export PUBLIC_IP=192.168.0.10
	docker run -d -p 8001:8001 -p 5001:5001 quay.io/coreos/etcd:v0.4.6 -peer-addr ${PUBLIC_IP}:8001 -addr ${PUBLIC_IP}:5001 -name etcd-node1
	docker run -d -p 8002:8002 -p 5002:5002 quay.io/coreos/etcd:v0.4.6 -peer-addr ${PUBLIC_IP}:8002 -addr ${PUBLIC_IP}:5002 -name etcd-node2 -peers ${PUBLIC_IP}:8001,${PUBLIC_IP}:8002,${PUBLIC_IP}:8003
	docker run -d -p 8003:8003 -p 5003:5003 quay.io/coreos/etcd:v0.4.6 -peer-addr ${PUBLIC_IP}:8003 -addr ${PUBLIC_IP}:5003 -name etcd-node3 -peers ${PUBLIC_IP}:8001,${PUBLIC_IP}:8002,${PUBLIC_IP}:8003

 Make sure the etcd cluster is running by requesting the leader summary. 

	curl -L $PUBLIC_IP:5001/v2/stats/leader 

 See the [running etcd in containers ](https://coreos.com/blog/Running-etcd-in-Containers/) page. 

# 2. Download docker-task-executor 

Download the docker task executor. 

 git clone logscape.com/docker-task-excuter.git


#3. Start Your Docker Task

To execute a docker task you will need to specify a container and the command to run in the container. Here's a trivial example exeucting a the sleep command. 

	sudo python main.py ubuntu:10.04 "sleep 5m" 

To start a longer running task like a database you would need to pass the command specified in the DockerFile. The example below uses (tutum's mysql image)https://github.com/tutumcloud/tutum-docker-mysql. This container uses a run script which starts all the mysql daemons. 

	sudo python main.py tutum/mysql:5.6 "./run.sh"


#4. Access Task Metrics and Status using the Rest API 

Using the mysql example the smart end point is started on port 33015. You can get curl the task metrics in the following manner.

	curl -X GET http://$PUBLIC_IP:$33015/metrics

You will get the following response.




#5. Access Task Metrics and Status through etcd 

Each task will publish the following information to etcd

	/service-XXXX-XXXX
	    /task-123-345
	        -running 
		-status 
		-metrics 
		-info




			






