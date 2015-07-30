##VisonDataLoader VDL
#Description:
This is a rest API Service that can be utilized to initalize bulk dataloads into an elasticsearch cluster from s3.
This is intended to be used with jenkins. You restrict your security group on the api server in aws to allow traffic 
only on the api port from the jenkins ip. Then you use your jenkins job with parameters to make the api call to start
the loading process. I intend to improve upon this idea. This is just an inital working concept.
Eventually I will add basic authentication, and a config file for the transient settings for ElasticSearch to support faster bulk loading. Currently these are hard coded.

The process also has the ability to revert the elastic-search settings once its completed loading.
However, currently it is commented out on line 115 of the api_execute_data_load.py script.
If you wish to enable it please uncomment it.

##How to USE!
#Here are the examples of how to use it.

	#All Variables are required and required in the order below, and here they are:
	
	##Start Load
		#Example URL
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
		
		#Variable Explinations	
			#The first var is load, although this is for future development for now it is just required.
			#Host: this can be either the ip address or dns name to your es cluser
			#Thread: The number of worker threads to spawn
			#MappingLocation: This is the s3 location of your ES mapping file for index load.
			#DataLocation: This is the location of your data. Need top be bucket/data_bucket
			#Port: The port elasticsearch is on.
			#Index: The elasticsearch index to create, or index to.
			#Protocol: Just make it http. That is the only supported protocol currently.
			#Type: Yourdatatype
			#Access: Your AWS Access Key
			#Secret: Your AWS Secret Key

	##Delete Index:
			#Example URL
					http://127.0.0.1:8001/delete/
					wos4&
					host=ip or DNS&
					port=9200
	
			#Variable Explinations	
				#The first var is the name of the index you wish to delete.
				#Host: this can be either the ip address or dns name to your es cluser
				#Port: The number of worker threads to spawn

							
##All values are seperated by & sign. They are need to be key=value, with key being the variable name. This will be used later.
			If you need to use a \ in a variable please use | instead. I.e. in your mapping and datalocation variables you will need this.