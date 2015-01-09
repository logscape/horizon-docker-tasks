# Horizon 

An Enterprise-Level Container Orchestration Platform that gives you  

	1 Resource Allocation by tags (properties) - AKA as the resourceSelection 
	2 Querying executing/tasks resources by tags 
	3 Control of your Service/Task life cycle - start,stop services and tasks 
er


# MVP Requirements 



## 1. Docker/Script Wrapper 

 A Docker Script Wrapper - to interact with Docker and execute a docker task and provide process visbility 

	process visibility  (possibly spool stats to disk) 
	- PID 
	- Resource Utizlisation 


## 2. Service Descriptor [Bundle] 
 The user uploads a service descriptor as XML/JSON which describes the Service and Task( Docker Task)  to be executed 
	- tags 


## 3. VScape Manangement Console (VsM) 
 The VsM console will provide service/tasks visbility and control the service/task life cycle.

 1. Task(script) -  list, stop, suspend etc 
 2. Services - list,start ,stop etc 
 3.  


## Monitoring 

 This will provide health of a Logscape Docker Task. 



