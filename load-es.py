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

# load a local file to elasticsearch
def load_local_file(file_name, es_host, es_port, es_index, es_type):
    logging.info('loading %s', file_name)
    with open(file_name, 'r') as file_handle:
        file_contents = file_handle.read()
        if file_contents:
            if file_name.endswith('.gz'):
                file_contents = decompress_gzip(file_contents)
            es = Elasticsearch(host=es_host, port=es_port, timeout=180)
            es.bulk(body=file_contents, index=es_index, doc_type=es_type, timeout=120)

# load an S3 file to elasticsearch
def load_s3_file(s3_bucket, s3_key, es_host, es_port, es_index, es_type):
    logging.info('loading s3://%s/%s', s3_bucket, s3_key)
    s3 = boto3.client('s3')
    file_handle = s3.get_object(Bucket=s3_bucket, Key=s3_key)
    file_contents = file_handle['Body'].read()
    if file_contents:
        if s3_key.endswith('.gz'):
            file_contents = decompress_gzip(file_contents)
        es = Elasticsearch(host=es_host, port=es_port, timeout=180)
        es.bulk(body=file_contents, index=es_index, doc_type=es_type, timeout=120)


# 1. create the index
# 2. set the index's refresh to -1
# 3. load data on child threads, wait till threads join
# 4. set the index's refresh to 1s
if __name__ == '__main__':
    start = datetime.now()

    parser = argparse.ArgumentParser()
    parser.add_argument('--data', help='The data directory. Either a local directory [/path/to/data] or an S3 bucket [s3://bucket/path/to/data].', required=True)
    parser.add_argument('--host', help='The elasticsearch host name [ex: localhost]', required=True)
    parser.add_argument('--protocol', help='The elasticsearch protocol [default: http]', default='http')
    parser.add_argument('--port', help='The elasticsearch port [default: 9200]', type=int, default=9200)
    parser.add_argument('--index', help='The elasticsearch index [ex: my-index]', required=True)
    parser.add_argument('--type', help='The elasticsearch type [ex: my-type]', required=True)
    parser.add_argument('--mapping', help='A file containing the elasticsearch mappings and settings to create the index. Either a local file [/path/to/mapping.json] or an S3 object [s3://bucket/path/to/mapping.json].', default=None)
    parser.add_argument('--threads', help='The number of threads to run the bulk uploads in parallel.', type=int, default=1)
    args = parser.parse_args()
    es_url = args.protocol + '://' + args.host + ':' + str(args.port) + '/' + args.index + '/' + args.type

    es = Elasticsearch(host=args.host, port=args.port, timeout=180)

    # create index with mapping file if the --mapping flag is set
    if args.mapping:
        logging.info('creating index %s with mapping %s', es_url, args.mapping)
        if args.mapping.startswith('s3://'):
            # S3 file - https://boto3.readthedocs.org/en/latest/reference/services/s3.html#object
            s3 = boto3.client('s3')
            s3_bucket, s3_key = parse_s3_path(args.mapping)
            file_handle = s3.get_object(Bucket=s3_bucket, Key=s3_key)
            mapping = file_handle['Body'].read()
        else:
            # local file
            with open(args.mapping, 'r') as file_handle:
                mapping = file_handle.read()
        try:
            es.indices.create(index=args.index, body=mapping)
        except RequestError, e:
            # you will end up here if the index already exists
            logging.exception(e)
#            sys.exit(1)

    # load data
    logging.info('starting to load %s to %s', args.data, es_url)
    es.indices.put_settings({'index': {'refresh_interval': '-1'}}, index=args.index)  

    pool = Pool(processes=args.threads)
    if args.data.startswith('s3://'):
        # S3 - https://boto3.readthedocs.org/en/latest/reference/services/s3.html#bucket
        s3 = boto3.resource('s3')
        s3_bucket, s3_key = parse_s3_path(args.data)
        for file_summary in s3.Bucket(s3_bucket).objects.all():
            # filter down to files that start with the specified path
            if file_summary.key.startswith(s3_key):
                pool.apply_async(load_s3_file, args=(s3_bucket, file_summary.key, args.host, args.port, args.index, args.type))
    else:
        # local directory
        for root, subdirs, files in os.walk(args.data):
            for file_name in files:
                # ignore dot files
                if not file_name.startswith('.'):
                    file_name = os.path.join(root, file_name)
                    pool.apply_async(load_local_file, args=(file_name, args.host, args.port, args.index, args.type))

    pool.close()
    pool.join()

    es.indices.put_settings({'index': {'refresh_interval': '1s'}}, index=args.index)

    logging.info('finished loading %s to %s in %s', args.data, es_url, str(datetime.now() - start))