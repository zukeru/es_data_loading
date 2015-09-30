#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright [current year] the Melange authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#	http://www.apache.org/licenses/LICENSE-2.0
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
import socket

def shell_command_execute(command):
	p = Popen(command, stdout=PIPE, shell=True)
	(output, err) = p.communicate()
	return output
			
@route('/get_status/')
def no_comands():
	command = 'ps aux | grep vdl.py'
	python_processes = shell_command_execute(command)
	number_of_python = python_processes.split('\n')
	length_check = len(number_of_python)
	if length_check >= 3:
		return 'is_currently_loading'
	else:
		return 'not_currently_loading'
			
if __name__ == '__main__':
	reload(sys)
	sys.setdefaultencoding('utf8')
	url = os.path.dirname(os.path.realpath(__file__)) + '/logging.ini'
	logging.config.fileConfig(url)
	logger = logging.getLogger('vdl_status')
	ip_address = socket.gethostbyname(socket.gethostname())
	logger.info('Starting API SERVER.')
	run(host=ip_address, port=8002, debug=True)

