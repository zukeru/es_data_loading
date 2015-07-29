#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Love Sabbath 
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import RequestError
from subprocess import Popen, PIPE
from multiprocessing import Pool
from datetime import datetime
import boto3
import sys
import os
import argparse
import logging
import logging.config
from bottle import route, run


# make python <3 utf-8
reload(sys)
sys.setdefaultencoding('utf8')

logging.config.fileConfig('logging.ini')

# decompress a gzip string
def decompress_gzip(data):
    return Popen(['zcat'], stdout=PIPE, stdin=PIPE).communicate(input=data)[0]

# parse an s3 path into a bucket and key 's3://my-bucket/path/to/data' -> ('my-bucket', 'path/to/data')
def parse_s3_path(str):
    _, _, bucket, key = str.split('/', 3)
    return (bucket, key)

def shell_command_execute(command):
    p = Popen(command, stdout=PIPE, shell=True)
    (output, err) = p.communicate()
    return output

# load an S3 file to elasticsearch
def load_s3_file(s3_bucket, s3_key, es_host, es_port, es_index, es_type):
    logging.info('loading s3://%s/%s', s3_bucket, s3_key)
    s3 = boto3.client('s3')
    file_handle = s3.get_object(Bucket=s3_bucket, Key=s3_key)
    file_contents = file_handle['Body'].read()
    logging.info('%s'%s3_key)
    if file_contents:
        if s3_key.endswith('.gz'):
            file_contents = decompress_gzip(file_contents)
        es = Elasticsearch(host=es_host, port=es_port, timeout=180)
        es.bulk(body=file_contents, index=es_index, doc_type=es_type, timeout=120)
        


def set_es_settings(host, port):
    es_settings = """curl -XPUT http://""" + host + """:"""+port+"""//_cluster/settings -d '{
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
                            }'"""
    shell_command_execute(es_settings) 
    
def start_load(secret, access, protocol, host, ports, index, type, mapping, data,threads):
    print secret, access, protocol, host, ports, index, type, mapping, data, threads
    start = datetime.now()
    es_url = protocol + '://' + host + ':' + str(ports) + '/' + index + '/' + type
    es = Elasticsearch(host=host, port=ports, timeout=180)
    
    # S3 file - https://boto3.readthedocs.org/en/latest/reference/services/s3.html#object
    s3 = boto3.client('s3',  aws_access_key_id=access, aws_secret_access_key=secret)
    s3_bucket, s3_key = parse_s3_path(mapping)
    file_handle = s3.get_object(Bucket=s3_bucket, Key=s3_key)
    mapping = file_handle['Body'].read()
    
    try:
        es.indices.create(index=index, body=mapping)
    except:
        print 'index exist'
    
    set_es_settings(host, ports)

    logging.info('starting to load %s to %s', data, es_url)
    es.indices.put_settings({'index': {'refresh_interval': '-1'}}, index=index)  
    
    pool = Pool(processes=int(threads))
    
    s3 = boto3.resource('s3', aws_access_key_id=access, aws_secret_access_key=secret)
    s3_bucket, s3_key = parse_s3_path(data)
    for file_summary in s3.Bucket(s3_bucket).objects.all():
        if file_summary.key.startswith(s3_key):
            pool.apply_async(load_s3_file, args=(s3_bucket, file_summary.key, host, ports, index, type))
            
    pool.close()
    pool.join()
    
    es.indices.put_settings({'index': {'refresh_interval': '1s'}}, index=index)

    logging.info('finished loading %s to %s in %s', data, es_url, str(datetime.now() - start))
    
    
@route('/load_data/')
def recipes_list():
    return """Please include all nessecary values: example: 
            http://127.0.0.1:8001/load_data/load&host=internal-1pelasticsearch-deb-ILB-2051321412&thread=5&mappinglocation=tr-ips-ses-data|mappings|version_1_2|wos.mapping&datalocation=tr-ips-ses-data|json-data|wos|20150724|wos-1&port=9200&index=wos4&protocol=http&type=wos"""

@route('/load_data/<name>', method='GET')
def recipe_show( name="Mystery Recipe" ):

    values = name.split('&')
    
    #set api values
    try:
        command = values[0]
        host = values[1] + ".us-west-2.elb.amazonaws.com"
        threads = values[2]
        mapping_location = values[3].replace('|', '/')
        data_location = values[4].replace('|', '/')
        ports = values[5]
        index = values[6]
        protocol = values[7]
        type = values[8]
        access = values[9]
        secret = values[10]

        host = host.split('=')[1]
        threads = threads.split('=')[1]
        mapping_location = "s3://" + mapping_location.split('=')[1]
        data_location = "s3://" + data_location.split('=')[1]
        ports = ports.split('=')[1]
        index = index.split('=')[1]
        protocol = protocol.split('=')[1]
        types = type.split('=')[1]
        access = access.split('=')[1]
        secret = secret.split('=')[1]

    except Exception as e:
        return 'Please include all nessecary values: example: http://127.0.0.1:8001/load_data/load&host=test.com&thread=5&woslocation=s3&s3location=test&port=9200&index=wos4&protocol=http&type=wos'
    
    
    print command,host,threads,mapping_location,data_location
    start_load(secret, access, protocol, host, ports, index, types, mapping_location, data_location,threads)
    some_html = ('%s,%s,%s,%s,%s,%s,%s,%s,%s' % (command,host,threads,mapping_location,data_location, ports, index, protocol, types))
    return some_html

#@route('/recipes/<name>', method='DELETE' )
#def recipe_delete( name="Mystery Recipe" ):
#    return "DELETE RECIPE " + name

#@route('/recipes/<name>', method='PUT')
#def recipe_save( name="Mystery Recipe" ):
#    return "SAVE RECIPE " + name
if __name__ == '__main__':
    run(host='172.31.28.189', port=8001, debug=True)


