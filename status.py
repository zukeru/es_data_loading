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
from multiprocessing import Pool, Process
from datetime import datetime
import boto3
import sys
import os
import argparse
import logging
import logging.config
from bottle import route, run
from boto.cloudformation.stack import Output
import json


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

#This is what is called when no arguments are given
@route('/load_data/')
def no_comands():
    return """Please include all nessecary values: example: 
                Start Load
                http://127.0.0.1:8001/load_data/load&host=ip or DNS&thread=5&mappinglocation=tr-ips-ses-data|mappings|version_1_2|wos.mapping&datalocation=tr-ips-ses-data|json-data|wos|20150724|wos-1&port=9200&index=wos4&protocol=http&type=wos&access=access_key&secret=secret_key
                Delete Index
                http://127.0.0.1:8001/delete/wos4&host=ip or DNS&port=9200
                
                with loading you must specify the load command as shown above
                use & to seperate values
                use = to seperate key value pairs
                use | to insert \
                """
@route('/get_status/<name>')
def get_status( name="Get Loading Status"):
    values = name.split('&')
    #split apart the url syntax items are split by & key values by = and any plcae that needs \ gets |
    #set auto refrest split values
    #+ ".us-west-2.elb.amazonaws.com"
    try:
        host = str(values[0]) 
        port = str(values[1])
        host = 'http://' + host + ':' + port
        
        index = values[2] 
        cat_es_thread_pool = 'curl ' + host + '/_cat/thread_pool'
        build_html_newlines = ''
        output = shell_command_execute(cat_es_thread_pool)
        for line in output.split('\n'):
            try:
                values = line.split()
                build_html_newlines = build_html_newlines + '<td align="right">' + values[0] + '</td>' + '<td align="right">' + values[1] + '</td>' + '<td align="right">' + values[2] + '</td>' + '<td align="right">' + values[3] + '</td>' + '<td align="right">' + values[4] + '</td></tr>'
            except:
                continue    
        thread_pool_html = '<table><tr><td>instance</td><td>ip</td><td>thread pool active</td><td>thread pool queue</td><td>thread pool rejected</td></tr><tr>' + str(build_html_newlines) + '</table>'
        stats = 'curl ' + str(host) + '/' + str(index) +'/_stats?pretty=true'
        return_stats = shell_command_execute(stats)
        ret_json = json.loads(return_stats)
        index_rate_html = '<table><td>Indexing Rate:</td><td>' + str(ret_json['_all']['total']['indexing']['index_current']) + '</td></table></html>'
        top_html = '<META HTTP-EQUIV="refresh" CONTENT="15"><html><title>VDL Status</title><body>'
        logs = open(os.path.dirname(os.path.realpath(__file__)) + '/load-es.log')
        log_contents = logs.read()
        log_values = log_contents.split('\n')
        log_html = ''
        for line in log_values:
            log_html += '<tr><td> ' + line + '</td></tr>'
        
        log_html = '<table>' + log_html + '</table>'
        
        file_html = top_html + thread_pool_html + index_rate_html + '<br><br>' + log_html
        return file_html
    except Exception as e:
        return (""" Error getting status %s, %s """ % (e, host)) 
                
if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf8')
    url = os.path.dirname(os.path.realpath(__file__)) + '/status-logging.ini'
    print url
    logging.config.fileConfig(url)
    run(host='172.31.28.189', port=8002, debug=True)
    #run(host='127.0.0.1', port=8001, debug=True)

