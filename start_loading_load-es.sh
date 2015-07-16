#!/bin/bash -x
python $WORKSPACE/load-es.py --data "$wos" --host $host --index $index --port $port --type $type --mapping "$mapping" --threads $threads



