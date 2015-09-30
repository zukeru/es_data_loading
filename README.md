This is a parallel elasticsearch bulk and non bulk data loading rest service. This service takes json files in gzip format for bulk inserting. This is a multiprocessing parallel data loading service that is called via rest api. It is designed to be utilized with Jenkins and a multi configuration role, and s3 bucket. More documentation to follow.


#User-Axis Var Examples:
	http://172.31.28.189:8001/load_data/load?folder|bucket|path1
	http://172.31.28.189:8001/load_data/load?folder|bucket|path2


#Jenkins Parameters:

##Threads: 
	The number of threads for that loading host you want to spawn to accomplish the bulk loading.
##Index:
	The index the data is going to be loaded to
##Host:
	The elasticsearch host the data is going to be loaded to. This is designed to be used with a load balancer so it can direct traffic between the 3 client nodes. Currently please remove the: .us-west-2.elb.amazonaws.com portion of the dns name to resemble the following: internal-1pelasticsearch-deb-ILB-2051321412 which would normally be internal-1pelasticsearch-deb-ILB-2051321412.us-west-2.elb.amazonaws.com.
##Port:
	The elastic search port
##Type:
	The type of the data set. i.e. wos, or whatever dataset you are loading.
##Mapping:
	This is the location of the mapping file separated by | to replace / for delimitation reasons. Note the number of shards per dataset is set based on the number of shards defined in the wos.mapping if the index doesn't already exist.
##Replicas:
	This is the number of replicas to set while the loading process is occurring.
##Access_key:
	This is the aws api access key set as a masked password that gets passed to the api. This password will not be logged anywhere. It is simply contained in the url. When this is passed from Jenkins it is masked for security reasons.
##Secret_key:
	Same as access key, but the secret key to your access key. This must be the account where the data is located.


#Jenkins Shell Command Execution
	This is the command Jenkins executes with the parameters you set. Currently you need one job per dataset because currently there is no way to parameterize the user axis variables, which can only be set in the jobs configuration. This is a Jenkins limitation. However, you can make multiple jobs per dataset.

```	
##!/bin/bash
	
##this is what splits the values apart from the user axis which is labeled wos hence it references the $wos var.
IFS='?' read -ra myarray <<< "$wos"
	
curl -XGET "${myarray[0]}&host=$host&thread=$threads&mappniglocation=$mapping&datalocation=${myarray[1]}&port=$port&index=$index&protocol=http&type=$type&access=$access_key&secret=$secret_key"
```

#Here are the examples of how to use it.
All Variables are required and required in the order below, and here they are:
	
#Start Load

	This is an explanation of the restful structure for initiating a data load.

##Example URL
	http://127.0.0.1:8001/load_data/
	load&
	host=ip or DNS&
	thread=5&
	mappinglocation=bucket|mappings_bucket|version_1_2|wos.mapping&
	datalocation=bucket|json-data|data-name&
	port=9200&
	index=wos4&
	protocol=http&
	type=wos&
	access=access_key&
	secret=secret_key
		
##Variable Explinations	
	The first var is load, although this is for future development for now it is just required.
##Host: 
	this can be either the ip address or dns name to your es cluser
##Thread: 
	The number of worker threads to spawn
##MappingLocation: 
	This is the s3 location of your ES mapping file for index load.
##DataLocation: 
	This is the location of your data. Need top be bucket/data_bucket
##Port: 
	The port elasticsearch is on.
##Index: 
	The elasticsearch index to create, or index to.
##Protocol: 
	Just make it http. That is the only supported protocol currently.
##Type: 
	Yourdatatype
##Access: 
	Your AWS Access Key
##Secret: 
	Your AWS Secret Key

#Delete Index:

	This is an explication for initiating a deletion

##Example URL
	http://127.0.0.1:8001/delete/
	wos4&
	host=ip or DNS&
	port=9200
	
##Variable Explanations	
	The first var is the name of the index you wish to delete.
##Host: 
	this can be either the ip address or dns name to your es cluster
##Port: 
	The number of worker threads to spawn
							
							
All values are separated by & sign. They are need to be key=value, with key being the variable name. This will be used later.

If you need to use a / in a variable please use | instead. I.e. in your mapping and data location variables you will need this.

#How to install:
	Run install.sh with sudo bash -x install.sh this will install the service and start both apis. they will be installed currently as 
	sudo service vdl start or sudo service vdl_status start or stop



