#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright [current year] the Melange authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
import json

# decompress a gzip string
def decompress_gzip(data):
    return Popen(['zcat'], stdout=PIPE, stdin=PIPE).communicate(input=data)[0]

# parse an s3 path into a bucket and key 's3://my-bucket/path/to/data' -> ('my-bucket', 'path/to/data')
def parse_s3_path(str):
    _, _, bucket, key = str.split('/', 3)
    return (bucket, key)

# load an S3 file to elasticsearch
def shell_command_execute(command):
    p = Popen(command, stdout=PIPE, shell=True)
    (output, err) = p.communicate()
    logging.info(output)
    return output

def delete_entry(host,port,index,id):
    delete_command = 'curl -XDELETE http://' + host + ':' + port + '/' + index + '/_query?q=id:' +id
    shell_command_execute(delete_command)
    
def load_single_s3_file(s3_bucket, s3_key, es_host, es_port, es_index, es_type, access, secret):
    try:
        s3 = boto3.client('s3',  aws_access_key_id=access, aws_secret_access_key=secret)
        file_handle = s3.get_object(Bucket=s3_bucket, Key=s3_key)
        file_contents = file_handle['Body'].read()
        if file_contents:
            if s3_key.endswith('.del.gz'):
                file_contents = decompress_gzip(file_contents)
                split_lines = file_contents.split('\n')
                for line in split_lines:
                    new_line = line.split('"')
                    index = new_line[5]
                    id = new_line[13]
                    print 'print delete',id,index
                    #get index and id from json
                    #delete_entry(es_host,es_port,index,id)

            if s3_key.endswith('.gz') and 'del' not in str(s3_key):
                file_contents = decompress_gzip(file_contents)
                split_lines = file_contents.split('\n')
                for line in split_lines:
                    if len(line) <=45:
                        new_line = line.split('"')
                        id = new_line[5]
                        print 'insert',id       
                        #check if exist
                        #if exist update if not insert
                        #filecontent is the file.
                    else:
                        continue
            #es = Elasticsearch(host=es_host, port=es_port, timeout=180)
            #res = es.get(index="test-index", doc_type='tweet', id=1)
            #es.insert(body = file_contents, index = es_index, doc_type=es_type, timeout=120)
    except Exception as e:
        print e


#this is what is called to set up the loading process from the api.    
def start_load(secret, access, protocol, host, ports, index, type, mapping, data,threads):
    
    start = datetime.now()
    es_url = protocol + '://' + host + ':' + str(ports) + '/' + index + '/' + type
    #es = Elasticsearch(host=host, port=ports, timeout=180)
    pool = Pool(processes=int(threads))
    
    s3 = boto3.resource('s3', aws_access_key_id=access, aws_secret_access_key=secret)
    s3_bucket, s3_key = parse_s3_path(data)
    
    for file_summary in s3.Bucket(s3_bucket).objects.all():
        if file_summary.key.startswith(s3_key):
            load_single_s3_file(s3_bucket, file_summary.key, host, ports, index, type, access, secret)
            #pool.apply_async(load_single_s3_file, args=(s3_bucket, file_summary.key, host, ports, index, type, access, secret))
    pool.close()
    pool.join()
    #es.indices.put_settings({'index': {'refresh_interval': '1s'}}, index=index)
    #reset_es_settings(host, ports)

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf8')
    
    host='internal-1pelasticsearch-deb-ILB-2051321412'
    threads='5'
    mapping='s3://tr-ips-ses-data/mappings/version_1_2/wos.mapping'
    data='s3://tr-ips-ses-data/wos-incremental-load-sample'
    ports='9200'
    index='wos1'
    protocol='http'
    type='wos'
    access=''
    secret=''
    start_load(secret, access, protocol, host, ports, index, type, mapping, data,threads)
    #url = os.path.dirname(os.path.realpath(__file__)) + '/logging.ini'
    #print url
    #logging.config.fileConfig(url)


