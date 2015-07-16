#!/bin/bash -x

curl -XPUT http://$host:$port/_cluster/settings -d '{
    "transient" : {
	    "index.warmer.enabled": false,
	    "indices.memory.index_buffer_size": "40%",
	    "indices.store.throttle.max_bytes_per_sec": "10mb",
	    "index.number_of_replicas": 0,
	    "indices.store.throttle.type": "Merge",
	    "index.compound_on_flush": false,
	    "index.compound_format": false,
	    "http.max_content_length": "1000mb",
	    "threadpool.bulk.type":"fixed",
	    "threadpool.builk.size": 120, 
	    "threadpool.bulk.queue_size": 10000
    }
}'

python $WORKSPACE/load-es.py --data "$wos" --host $host --index $index --port $port --type $type --mapping "$mapping" --threads $threads

curl -XPUT http://$host:$port/_cluster/settings -d '{
"transient" : {
               "index.warmer.enabled": true,
               "indices.memory.index_buffer_size": "40%",
               "indices.store.throttle.max_bytes_per_sec": "100mb",
               "index.number_of_replicas": 0,
               "indices.store.throttle.type": "Merge",
               "index.compound_on_flush": true,
               "index.compound_format": true,
               "http.max_content_length": "1000mb",
                }
}'

