#!/bin/bash -x
echo $wos
python $WORKSPACE/es_load_single.py  --secret_key $AWS_SECRET_KEY --access_key $AWS_ACCESS_KEY --threads $threads --shards $shards --replicas $replicas --index $index --host $host --wos $wos
