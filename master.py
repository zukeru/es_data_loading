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
from bottle import route, run, Bottle, template,request
from boto import ec2,boto
import json
import re
from collections import defaultdict
import hashlib
import time
import sqlite3 as lite
import random
import time
import socket
from awscli.customizations.emr.sshutils import check_command_key_format

global access_key
global secret_key
secret_key = os.environ.get('AWS_SECRET_KEY')
access_key = os.environ.get('AWS_ACCESS_KEY')


def shell_command_execute(command):
	p = Popen(command, stdout=PIPE, shell=True)
	(output, err) = p.communicate()
	return output

def connect_db():
	con = None
	con = lite.connect('master.db')
	cur = con.cursor() 
	objects = []
	#objects.append(con,cur)
	objects.append(con)
	objects.append(cur)
	return objects

def queue_manager(logger):
	'''
	This is a daemon process that watches the db and manages the queue.
	'''
	try:
		while True:
			logger.info('queue_manager_running')
			#init two dbs one for listing the queue the other for updating and retriving worker ip
			try:
				init_db = connect_db()
				con = init_db[0]
				cur = init_db[1]
				update_init_db = connect_db()
				update_con = init_db[0]
				update_cur = init_db[1]	
			except Exception as e:
				logger.error(str(e))
			
			'''
			You first select everything from the queue
			if there is something in the queue select all entries again to reload the cursor
			then you loop those entries.
			then you check the status. Curently status is only loading and calm, but calm is just a trigger, later will be a check to see if it had error during load
			then you retrieve the ip of the machine thats loading
			then you call the machines status api which does a ps grep for the number of processes loading named vdl.py which means if it is <= 3 it will be in the process of loading
			if not then it will not be
			I changed the status to return either loading or not loading in a unique way to use as a conditional statement for what to do next.
			this is how we are going to determine load finish and delete it from the queue on complettion else continue
			if calm is the trigger for status it will then go retrieve the ip of the machine from the db and then pass the command in queue to the ip it found via a curl request 
			then it will update the status to loading and it will check it everytime through with get_status to see if it is indeed still loading. And thus you have a queue manager
			
			'''		
			cur.execute('select * from queue')
			check_queue = cur.fetchone()
			if check_queue:
				cur.execute('select * from queue')
				for id,worker_id,command,status,idx in cur.fetchall():
					if status == 'loading':
						update_cur.execute('select ip from workers where id=?',(worker_id,))
						ip = update_cur.fetchone()
						curl_request = ('curl -XGET %s:8002/get_status/' % ip)
						loading_status = shell_command_execute(curl_request)
						if 'loadingelasticdata' in str(loading_status):
							continue
						else:
							update_cur.execute('delete from queue where id=?',(id,))
							update_con.commit()											
					else:
						update_cur.execute('select ip from workers where id=?',(worker_id,))
						ip = update_cur.fetchone()
						curl_request = ('curl -XGET %s:8001/load_data/%s' % (ip,command))
						shell_command_execute(curl_request)
						update_cur.execute('update queue set status="loading" where id =?',(id,))
						update_con.commit()
			con.close()
			update_con.close()
			time.sleep(2)
	except Exception as e:
		logger.error(str(e))					
					
@route('/load_data/<name>', method='GET')
def commands( name="Execute Load" ):
	
	try:
		values = name.split('&')
		logger.info('Getting Access and Secret Key As Master.')
		access = values[9]
		secret = values[10]
		index = values[6]
		index = index.split('=')[1]
		access_key = access.split('=')[1]
		secret_key = secret.split('=')[1]
	except Exception as e:
		logger.error(str(e))
		return str(e)
	
		
	try: 
		init_db = connect_db()
		con = init_db[0]
		cur = init_db[1]			
		cur.execute('SELECT * from workers')
		for id,ip in cur.fetchall():
			init_db2 = connect_db()
			con2 = init_db2[0]
			cur2 = init_db2[1]
			cur2.execute('select * from queue where worker_id=? ', (id,))	
			worker_in_queue = cur2.fetchone()
		
			if worker_in_queue:
				cur2.commit()
				con2.close()
				continue
			else:
				cur2.execute("INSERT INTO queue VALUES(?,?,?,'calm',?)", (random.randint(1, 10000),id, name, index))
				con2.commit()
				con2.close()
		return 'Command successfully sent to the queue'
	except Exception as e:
		logger.error(str(e))
		return	"""%s""" % str(e)	
	


def get_ec2_instances(region):
	try:
		ec2_conn = boto.ec2.connect_to_region(region,
				aws_access_key_id=access_key,
				aws_secret_access_key=secret_key)
		reservations = ec2_conn.get_all_reservations()
		return reservations
	except Exception as e:
		return """%s""" % str(e)

#This is what is cvalled when /delete/ is used.
@route('/delete/<name>', method='GET' )
def delete( name="Delete Index" ):		 
	values = name.split('&')
	try:
		#split apart the url syntax items are split by & key values by |
		index = values[0]
		host = values[1]
		host = host.split('=')[1]
		port = values[2]
		port = port.split('=')[1]
	except Exception as e:
		logger.error(e)
		return """%s""" % str(e)
				
	try:	 
		#This is the command that deletes the index.	 
		curl_command = 'curl -XDELETE http://' + host + ':9200/' + index	 
		shell_command_execute(curl_command)
		return "Successfully Deleted Index"
	except Exception as e:
		logger.error(str(e))
		return "Failed to Deleted Index %s" % str(e)

def worker_status():
	import time
	
	def connect_db():
		con = None
		con = lite.connect('master.db')
		cur = con.cursor() 
		objects = []
		#objects.append(con,cur)
		objects.append(con)
		objects.append(cur)
		return objects
	
	init_db = connect_db()
	con = init_db[0]
	cur = init_db[1]	
	
	while True:
		cur.execute('SELECT * from workers')
		for id,ip in cur.fetchall():
			check_command = 'sudo ssh ec2-user@%s; ps -ef | grep vdl;' % ip	
			print check_command
			shell_command_execute(check_command)
			print check_command
		'''				
			cur.execute('SELECT * from workers where ip=?',(str(instance.private_ip_address),))
			data = cur.fetchone()
			if data == None:
				cur.execute("INSERT INTO workers VALUES(?,?)" , (index, str(instance.private_ip_address),))
			else:
				logger.info(str(data) + "Already in DB")
				continue	
		'''	
	time.sleep(1)

def ui_server():	
	def connect_db():
		con = None
		con = lite.connect('master.db')
		cur = con.cursor() 
		objects = []
		#objects.append(con,cur)
		objects.append(con)
		objects.append(cur)
		return objects
	
	app = Bottle()
	@app.route('/')	
	def index():
		init_db = connect_db()
		con = init_db[0]
		cur = init_db[1]		
		cur.execute('SELECT * from workers')
		worker_html = '<div id="workers"><table>'
		for id,ip in cur.fetchall():
			worker_html += "<tr><td>"+ip+"</td></tr>"
		worker_html += '</div></table>'			 
		#UI
		wallpaper = os.path.dirname(os.path.realpath(__file__)) + '/bg.png'
		info = {'zookeepers':worker_html, 'wallpaper':wallpaper}
		return template('main.tpl', info)

	ip_address = socket.gethostbyname(socket.gethostname())
	logger.info('Starting API SERVER.')
	run(app, host=ip_address, port=8001, debug=True)
	
if __name__ == '__main__':
	#init logging
	try:
		url = os.path.dirname(os.path.realpath(__file__)) + '/logging.ini'
		logging.config.fileConfig(url)
		logger = logging.getLogger('queue_manager')	
	except:
		sys.exit(2)
	
	#build database tables, if they exist do nothing		
	try:
		logger.info('Building Database Tables.') 
		init_db = connect_db()
		con = init_db[0]
		cur = init_db[1]
		cur.execute("""CREATE TABLE workers(Id INT, ip TEXT)""")
		cur.execute("""CREATE TABLE worker_status(Id INT, ip TEXT, status TEXT)""")
		cur.execute("""CREATE TABLE queue(Id INT, worker_id TEXT, command TEXT, status TEXT, idx TEXT)""")
		con.commit()
		con.close()
	except Exception as e:
		logger.info(str(e))
		pass
		
		#this builds the database of host, uses ec2 discovery.
	try:	
		logger.info('Initiate Auto Discovery of Workers.') 
		init_db = connect_db()
		con = init_db[0]
		cur = init_db[1]
		reservations = []
		reservations = get_ec2_instances('us-west-2')
		instances = [i for r in reservations for i in r.instances]
		for index, instance in enumerate(instances):
			if str(instance.tags.get('Name')) == 'es-data-loader':
				cur.execute('SELECT * from workers where ip=?',(str(instance.private_ip_address),))
				data = cur.fetchone()
				if data == None:
					cur.execute("INSERT INTO workers VALUES(?,?)" , (index, str(instance.private_ip_address),))
				else:
					logger.info(str(data) + "Already in DB")
					continue
		con.commit()
		con.close()
	except Exception as e:
		logger.error(str(e))

	try:
		logger.info('Setting utf-8 format.')
		reload(sys)
		sys.setdefaultencoding('utf8')
	except Exception as e:
		logger.error(str(e))

	try:
		logger.info('Starting queue manager')
		d = Process(name='queue-manager-daemon', target=queue_manager, args=(logger,))
		d.daemon = True
		d.start()
	except Exception as e:
		logger.error(str(e))
	'''	
	try:
		logger.info('Starting status checker')
		d = Process(name='queue-manager-daemon', target=worker_status)
		d.daemon = True
		d.start()
	except Exception as e:
		logger.error(str(e))
	'''		
	try:	
		ip_address = socket.gethostbyname(socket.gethostname())
		logger.info('Starting API SERVER.')
		#run(app, host=ip_address, port=8001, debug=True)
		ui_d = Process(name='ui-daemon', target=ui_server)
		ui_d.daemon = True
		ui_d.start()
		run(host=ip_address, port=8002, debug=True)
	except Exception as e:
		logger.error(str(e))
