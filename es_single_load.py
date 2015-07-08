import argparse
import subprocess
import sys
import boto.ec2
import random
import multiprocessing
import time
import os
from datetime import datetime

#folder argument for s3 which folder to get data from
#bucket argument

def shell_command_execute(command):
    print 'Executing Command',command
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=False)
    (output, err) = p.communicate()
    return output

def spawn_worker_node(command):
    try:
        print 'Spawning Python Daemon for Loading.'
        print 'Executing Command', command
        while True:
            p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=False)
            (output, err) = p.communicate()
            f = open('loading.log', 'w')
            write_string = str(datetime.now()) + str(output) + '\n'
            f.write(write_string)
            f.close()
        
    except Exception as e:
        print 'Error, in worker process',e

def download_s3(failures,wos,bucket,folder, access_key, secret_key):
    try:
        # connect to the bucket
        print ('Begining Download for Data %s/%s/%s' %(bucket,folder,wos))
        conn = boto.connect_s3(access_key, secret_key,is_secure=False)
        bucket = conn.get_bucket(bucket) 
        
        if failures:    
            try:
                def retry_failure(d,l):
                    try:
                        print 'Re-try failures'
                        l.get_contents_to_filename(d)
                    except:
                        print 'retry again.'
                        retry_failure(d,l)
                for d,l in failures:
                    retry_failure(d,l)
                
                failures = []
            except Exception as e:
                print e
                pass
        
        LOCAL_PATH = os.path.dirname(os.path.realpath(__file__))
        bucket_list = bucket.list()
        
        for l in bucket_list:
            keyString = str(l.key)
            d = LOCAL_PATH + '/' + keyString
            search_string = '/' + wos + '/'
            if search_string in str(l) and str(folder) in str(l):
                if str(wos) == 'wos_1' and '/wos_10/' in str(l):
                    continue
                try:
                    #print 'Downloading: %s' % d
                    l.get_contents_to_filename(d)
                except OSError:
                    if not os.path.exists(d):
                        os.makedirs(d)
            else:
                continue
        conn.close()
        return d,LOCAL_PATH
    
    except:
        if str(d) not in str(failures):
            failures.append((d,l))
            
        print 'Download timed out. Waiting 1 minute and trying again.'
        print 'Current Failures: %s' % failures
        
        time.sleep(60)
        download_s3(failures,wos,bucket,folder, access_key, secret_key)

def download_s3_files(bucket, access_key, secret_key):
    # connect to the bucket
    conn = boto.connect_s3(access_key, secret_key)
    bucket = conn.get_bucket(bucket)
    LOCAL_PATH = os.path.dirname(os.path.realpath(__file__))
    bucket_list = bucket.list()
    for l in bucket_list:
        keyString = str(l.key)
        d = LOCAL_PATH + '/' + keyString
        if 'backups' in str(l):
            continue
        if 'definition' in str(l):
            continue
        
        try:
            l.get_contents_to_filename(d)
        except OSError:
            if not os.path.exists(d):
                os.makedirs(d)

        
    conn.close()
    return LOCAL_PATH

def make_mapping(shards, replicas):
    wos_file_ins = """{
                        "settings": {
                            "number_of_shards": "%s",
                            "number_of_replicas": "%s",
                            "analysis": {
                                "analyzer": {
                                    "default": {
                                        "type": "standard",
                                        "position_offset_gap": 512,
                                        "filter": [
                                            "standard",
                                            "icu_folding",
                                            "lowercase"
                                        ]
                                    },
                                    "lower_analyzer": {
                                        "tokenizer": "keyword",
                                        "position_offset_gap": 512,
                                        "filter": [
                                            "icu_folding",
                                            "lowercase"
                                        ]
                                    },
                                    "en_std_lem": {
                                        "tokenizer": "standard",
                                        "position_offset_gap": 512,
                                        "filter": [
                                            "standard",
                                            "icu_folding",
                                            "lowercase",
                                            "en_lemmatization"
                                        ]
                                    },
                                    "en_std_syn": {
                                        "tokenizer": "standard",
                                        "position_offset_gap": 512,
                                        "filter": [
                                            "standard",
                                            "icu_folding",
                                            "lowercase",
                                            "en_synonym"
                                        ]
                                    },
                                    "en_std_synaddress": {
                                        "tokenizer": "standard",
                                        "position_offset_gap": 512,
                                        "filter": [
                                            "standard",
                                            "icu_folding",
                                            "lowercase",
                                            "en_synonym_address"
                                        ]
                                    }
                                },
                                "filter": {
                                    "en_lemmatization": {
                                        "type": "synonym",
                                        "synonyms_path": "en_lem_NAV.txt"
                                    },
                                    "en_synonym": {
                                        "type": "synonym",
                                        "synonyms_path": "en_synonyms.txt"
                                    },
                                    "en_synonym_address": {
                                        "type": "synonym",
                                        "synonyms_path": "en_synonyms_address.txt"
                                    }
                                }
                            }
                        },
                        "mappings": {
                            "wos": {
                                "_all": {
                                    "enabled": "false"
                                },
                               
                                "properties": {
                                    "addresses": {
                                        "type": "nested",
                                        "properties": {
                                            "full_address": {
                                                "type": "string",
                                                "search_analyzer": "en_std_synaddress"
                                            },
                                            "street": {
                                                "type": "string"
                                            },
                                            "city": {
                                                "type": "string"
                                            },
                                            "state": {
                                                "type": "string"
                                            },
                                            "zip": {
                                                "type": "string"
                                            },
                                            "country": {
                                                "type": "string"
                                            },
                                            "organization": {
                                                "type": "string"
                                            },
                                            "suborganization": {
                                                "type": "string"
                                            },
                                            "external_link": {
                                                "type": "string"
                                            },
                                            "laboratory": {
                                                "type": "string"
                                            },
                                            "province": {
                                                "type": "string"
                                            },
                                            "post_num": {
                                                "type": "string"
                                            },
                                            "display_name": {
                                                "type": "string"
                                            },
                                            "full_name": {
                                                "type": "string"
                                            },
                                            "email_addr": {
                                                "type": "string"
                                            },
                                            "wos_standard": {
                                                "type": "string"
                                            }
                                        }
                                    },
                                    "address": {
                                        "type": "string",
                                        "search_analyzer": "en_std_synaddress"
                                    },
                                    "title": {
                                        "type": "string",
                                        "index_analyzer": "en_std_lem",
                                        "search_analyzer": "en_std_syn"
                                    },
                                    "abstract": {
                                        "type": "string",
                                        "index_analyzer": "en_std_lem",
                                        "search_analyzer": "en_std_syn"
                                    },
                                    "keywords": {
                                        "type": "string",
                                        "index_analyzer": "en_std_lem",
                                        "search_analyzer": "en_std_syn"
                                    },
                                    "keywordsplus": {
                                        "type": "string",
                                        "index_analyzer": "en_std_lem",
                                        "search_analyzer": "en_std_syn"
                                    },
                                    "sourcega": {
                                        "type": "string"
                                    },
                                    "source": {
                                        "type": "string",
                                        "fields": {
                                            "sourcenavigator": {
                                                "type": "string",
                                                "index": "not_analyzed",
                                                "doc_values": true
                                            }
                                        }
                                    },
                                    "sourcesort": {
                                        "type": "string",
                                        "index": "not_analyzed",
                                        "doc_values": true
                                    },
                                    "authorsort": {
                                        "type": "string",
                                        "index": "not_analyzed",
                                        "doc_values": true
                                    },
                                    "authors": {
                                        "type": "string"
                                    },
                                    "authorsphrase": {
                                        "type": "string",
                                        "analyzer": "lower_analyzer",
                                        "copy_to": "authors"
                                    },
                                    "authorsrefine": {
                                        "type": "string",
                                        "index": "no",
                                        "fields": {
                                            "authorsnavigator": {
                                                "type": "string",
                                                "index": "not_analyzed",
                                                "doc_values": true
                                            }
                                        }
                                    },
                                    "corpauthors": {
                                        "type": "string",
                                        "fields": {
                                            "corpauthorsnavigator": {
                                                "type": "string",
                                                "index": "not_analyzed",
                                                "doc_values": true
                                            }
                                        }
                                    },
                                    "institution": {
                                        "type": "string",
                                        "fields": {
                                            "institutionnavigator": {
                                                "type": "string",
                                                "index": "not_analyzed",
                                                "doc_values": true
                                            }
                                        }
                                    },
                                    "prefinstitution": {
                                        "type": "string",
                                        "fields": {
                                            "prefinstnavigator": {
                                                "type": "string",
                                                "index": "not_analyzed",
                                                "doc_values": true
                                            }
                                        }
                                    },
                                    "allinstitution": {
                                        "type": "string"
                                    },
                                    "suborganization": {
                                        "type": "string"
                                    },
                                    "street": {
                                        "type": "string"
                                    },
                                    "city": {
                                        "type": "string"
                                    },
                                    "state": {
                                        "type": "string"
                                    },
                                    "country": {
                                        "type": "string",
                                        "fields": {
                                            "countrynavigator": {
                                                "type": "string",
                                                "index": "not_analyzed",
                                                "doc_values": true
                                            }
                                        }
                                    },
                                    "zip": {
                                        "type": "string"
                                    },
                                    "conferencetitle": {
                                        "type": "string",
                                        "fields": {
                                            "conferencetitlenavigator": {
                                                "type": "string",
                                                "index": "not_analyzed",
                                                "doc_values": true
                                            }
                                        }
                                    },
                                    "conferencesort": {
                                        "type": "string",
                                        "index": "not_analyzed",
                                        "doc_values": true
                                    },
                                    "conferenceinfo": {
                                        "type": "string"
                                    },
                                    "url": {
                                        "type": "string",
                                        "index": "no"
                                    },
                                    "proctime": {
                                        "type": "date",
                                        "format": "dateOptionalTime",
                                        "doc_values": true
                                    },
                                    "sortdate": {
                                        "type": "date",
                                        "format": "dateOptionalTime",
                                        "doc_values": true
                                    },
                                    "acday180": {
                                        "type": "integer",
                                        "doc_values": true
                                    },
                                    "acalltime": {
                                        "type": "integer",
                                        "doc_values": true
                                    },
                                    "binnum": {
                                        "type": "long"
                                    },
                                    "binid": {
                                        "type": "long"
                                    },
                                    "fuid": {
                                        "type": "string",
                                        "index": "not_analyzed"
                                    },
                                    "artno": {
                                        "type": "string",
                                        "analyzer": "lower_analyzer"
                                    },
                                    "dokid": {
                                        "type": "long"
                                    },
                                    "bibissueyear": {
                                        "type": "string",
                                        "fields": {
                                            "bibissueyearnavigator": {
                                                "type": "integer",
                                                "doc_values": true
                                            }
                                        }
                                    },
                                    "editions": {
                                        "type": "string",
                                        "fields": {
                                            "editionnavigator": {
                                                "type": "string",
                                                "index": "not_analyzed",
                                                "doc_values": true
                                            }
                                        }
                                    },
                                    "itemtype": {
                                        "type": "string",
                                        "fields": {
                                            "doctypenavigator": {
                                                "type": "string",
                                                "index": "not_analyzed",
                                                "doc_values": true
                                            }
                                        }
                                    },
                                    "normdoctype": {
                                        "type": "string",
                                        "fields": {
                                            "normdoctypenavigator": {
                                                "type": "string",
                                                "index": "not_analyzed",
                                                "doc_values": true
                                            }
                                        }
                                    },
                                    "ckey": {
                                        "type": "string",
                                        "analyzer": "lower_analyzer"
                                    },
                                    "category": {
                                        "type": "string",
                                        "fields": {
                                            "categorynavigator": {
                                                "type": "string",
                                                "index": "not_analyzed",
                                                "doc_values": true
                                            }
                                        }
                                    },
                                    "heading": {
                                        "type": "string",
                                        "fields": {
                                            "headingnavigator": {
                                                "type": "string",
                                                "index": "not_analyzed",
                                                "doc_values": true
                                            }
                                        }
                                    },
                                    "volume": {
                                        "type": "string"
                                    },
                                    "volumesort": {
                                        "type": "integer",
                                        "doc_values": true
                                    },
                                    "issue": {
                                        "type": "string"
                                    },
                                    "page": {
                                        "type": "string"
                                    },
                                    "pagesort": {
                                        "type": "integer",
                                        "doc_values": true
                                    },
                                    "languageslimit": {
                                        "type": "string",
                                        "fields": {
                                            "languagesnavigator": {
                                                "type": "string",
                                                "index": "not_analyzed",
                                                "doc_values": true
                                            }
                                        }
                                    },
                                    "rid": {
                                        "type": "string",
                                        "analyzer": "lower_analyzer"
                                    },
                                    "snid": {
                                        "type": "string",
                                        "index": "not_analyzed"
                                    },
                                    "fundingag": {
                                        "type": "string",
                                        "fields": {
                                            "fundingagnavigator": {
                                                "type": "string",
                                                "index": "not_analyzed",
                                                "doc_values": true
                                            }
                                        }
                                    },
                                    "grantno": {
                                        "type": "string",
                                        "analyzer": "lower_analyzer",
                                        "fields": {
                                            "grantnonavigator": {
                                                "type": "string",
                                                "index": "not_analyzed",
                                                "doc_values": true
                                            }
                                        }
                                    },
                                    "meshheading": {
                                        "type": "string",
                                        "fields": {
                                            "meshheadingnavigator": {
                                                "type": "string",
                                                "index": "not_analyzed",
                                                "doc_values": true
                                            }
                                        }
                                    },
                                    "meshqualifier": {
                                        "type": "string",
                                        "fields": {
                                            "meshqualifiernavigator": {
                                                "type": "string",
                                                "index": "not_analyzed",
                                                "doc_values": true
                                            }
                                        }
                                    },
                                    "fundingtxt": {
                                        "type": "string"
                                    },
                                    "citingyears": {
                                        "type": "integer"
                                    },
                                    "citingeditiondates": {
                                        "type": "integer"
                                    },
                                    "siloid": {
                                        "type": "string",
                                        "fields": {
                                            "collectionnavigator": {
                                                "type": "string",
                                                "index": "not_analyzed",
                                                "doc_values": true
                                            }
                                        }
                                    },
                                    "dbname": {
                                        "type": "string",
                                        "fields": {
                                            "dbnamenavigator": {
                                                "type": "string",
                                                "index": "not_analyzed",
                                                "doc_values": true
                                            }
                                        }
                                    },
                                    "patentno": {
                                        "type": "string"
                                    },
                                    "issueids": {
                                        "type": "string",
                                        "fields": {
                                            "issueidsnavigator": {
                                                "type": "string",
                                                "index": "not_analyzed",
                                                "doc_values": true
                                            }
                                        }
                                    },
                                    "orgcount": {
                                        "type": "integer"
                                    },
                                    "citingsrcscount": {
                                        "type": "integer",
                                        "doc_values": true
                                    },
                                    "citingsrcslocalcount": {
                                        "type": "integer"
                                    },
                                    "colluid": {
                                        "type": "string",
                                        "analyzer": "lower_analyzer"
                                    },
                                    "cuid": {
                                        "type": "string",
                                        "index": "no"
                                    },
                                    "pmid": {
                                        "type": "string"
                                    },
                                    "refunifids": {
                                        "type": "long"
                                    },
                                    "allrefids": {
                                        "type": "long"
                                    },
                                    "daisids": {
                                        "type": "integer",
                                        "fields": {
                                            "daisidsnavigator": {
                                                "type": "integer",
                                                "doc_values": true
                                            }
                                        }
                                    },
                                    "editor": {
                                        "type": "string",
                                        "fields": {
                                            "editornavigator": {
                                                "type": "string",
                                                "index": "not_analyzed",
                                                "doc_values": true
                                            }
                                        }
                                    },
                                    "assignee": {
                                        "type": "string",
                                        "fields": {
                                            "assigneenavigator": {
                                                "type": "string",
                                                "index": "not_analyzed",
                                                "doc_values": true
                                            }
                                        }
                                    },
                                    "literaturetype": {
                                        "type": "string",
                                        "fields": {
                                            "literaturetypenavigator": {
                                                "type": "string",
                                                "index": "not_analyzed",
                                                "doc_values": true
                                            }
                                        }
                                    },
                                    "concept": {
                                        "type": "string",
                                        "fields": {
                                            "conceptnavigator": {
                                                "type": "string",
                                                "index": "not_analyzed",
                                                "doc_values": true
                                            }
                                        }
                                    },
                                    "mconcept": {
                                        "type": "string",
                                        "fields": {
                                            "mconceptnavigator": {
                                                "type": "string",
                                                "index": "not_analyzed",
                                                "doc_values": true
                                            }
                                        }
                                    },
                                    "supertaxa": {
                                        "type": "string",
                                        "fields": {
                                            "supertaxanavigator": {
                                                "type": "string",
                                                "index": "not_analyzed",
                                                "doc_values": true
                                            }
                                        }
                                    },
                                    "taxonomic": {
                                        "type": "string"
                                    },
                                    "organisms": {
                                        "type": "string"
                                    },
                                    "genename": {
                                        "type": "string"
                                    },
                                    "chemical": {
                                        "type": "string"
                                    },
                                    "chembio": {
                                        "type": "string"
                                    },
                                    "idcodes": {
                                        "type": "string"
                                    },
                                    "disease": {
                                        "type": "string"
                                    },
                                    "sequence": {
                                        "type": "string"
                                    },
                                    "seqcasreg": {
                                        "type": "string"
                                    },
                                    "partsstructure": {
                                        "type": "string"
                                    },
                                    "methodsequipment": {
                                        "type": "string"
                                    },
                                    "geographic": {
                                        "type": "string"
                                    },
                                    "geologictime": {
                                        "type": "string"
                                    },
                                    "miscdesc": {
                                        "type": "string"
                                    },
                                    "ifactor": {
                                        "type": "float"
                                    },
                                    "toppaper": {
                                        "type": "string",
                                        "index": "no",
                                        "fields": {
                                            "toppapernavigator": {
                                                "type": "string",
                                                "index": "not_analyzed",
                                                "doc_values": true
                                            }
                                        }
                                    },
                                    "oasjournal": {
                                        "type": "string",
                                        "index": "no",
                                        "fields": {
                                            "oasjournalnavigator": {
                                                "type": "string",
                                                "index": "not_analyzed",
                                                "doc_values": true,
                                                "null_value": "No"
                                            }
                                        }
                                    },
                                    "esicategory": {
                                        "type": "string",
                                        "index": "not_analyzed"
                                    },
                                    "organismadvanced": {
                                        "type": "string"
                                    },
                                    "generic1": {
                                        "type": "string",
                                        "fields": {
                                            "generic1navigator": {
                                                "type": "string",
                                                "index": "not_analyzed",
                                                "doc_values": true
                                            }
                                        }
                                    },
                                    "generic2": {
                                        "type": "string"
                                    },
                                    "fuidxml": {
                                        "type": "string"
                                    },
                                    "compositexml": {
                                        "type": "string"
                                    },
                                    "siloxml": {
                                        "type": "string"
                                    },
                                    "fullmetaxml": {
                                        "type": "string"
                                    },
                                    "itemxml": {
                                        "type": "string"
                                    },
                                    "contributorsxml": {
                                        "type": "string"
                                    },
                                    "datasetlinksxml": {
                                        "type": "string"
                                    },
                                    "citationxml": {
                                        "type": "string"
                                    },
                                    "icrelatedxml": {
                                        "type": "string"
                                    },
                                    "identifiersxml": {
                                        "type": "string",
                                        "index": "no"
                                    },
                                    "datesxml": {
                                        "type": "string"
                                    },
                                    "addressxml": {
                                        "type": "string"
                                    },
                                    "umrelatedxml": {
                                        "type": "string"
                                    },
                                    "clusteredids": {
                                        "type": "string",
                                        "index": "no"
                                    },
                                    
                                    "fullrecord": {
                                        "type": "object",
                                        "enabled" : false,
                                        "properties": {
                                            "title": {
                                                "type": "string"
                                            },
                                            
                                            "authors": {
                                                "type": "object",
                                                "properties": {
                                                    "name": {
                                                        "type": "string"
                                                    },
                                                    "wos_standard": {
                                                        "type": "string"
                                                    },
                                                    "addr_no": { 
                                                        "type": "integer"
                                                    }
                                                    
                                                }
                                            },
                                            
                                           "address": {
                                                "type": "string"
                                            },
                                                    
                                            "bookauthor": {
                                                "type": "string"
                                            },
                                            "bookgroupauthor": {
                                                "type": "string"
                                            },
                                            "groupauthor": {
                                                "type": "string"
                                            },
                                            "editor": {
                                                "type": "string"
                                            },
                                            "source": {
                                                "type": "string"
                                            },
                                            "bookseries": {
                                                "type": "string"
                                            },
                                            "volume": {
                                                "type": "string"
                                            },
                                            "issue": {
                                                "type": "string"
                                            },
                                            "page": {
                                                "type": "string"
                                            },
                                            "partno": {
                                                "type": "string"
                                            },
                                            "supplement": {
                                                "type": "string"
                                            },
                                            "specialissue": {
                                                "type": "string"
                                            },
                                            "meetingabsno": {
                                                "type": "string"
                                            },
                                            "artno": {
                                                "type": "string"
                                            },
                                            "doi": {
                                                "type": "string"
                                            },
                                            "pubdate": {
                                                "type": "string"
                                            },
                                            "conferences": {
                                                "type": "object",
                                                "properties": {
                                                    "title": {
                                                        "type": "string"
                                                    },
                                                    "location": {
                                                        "type": "string"
                                                    },
                                                    "host": {
                                                        "type": "string"
                                                    },
                                                    "city": {
                                                        "type": "string"
                                                    },
                                                    "state": {
                                                        "type": "string"
                                                    },
                                                    "date": {
                                                        "type": "string"
                                                    },
                                                    "sponsors": {
                                                        "type": "string"
                                                    }
                                                }
                                            },
                                            "abstract": {
                                                "type": "string"
                                            },
                                            "keywords": {
                                                "type": "string"
                                            },
                                            "keywordsplus": {
                                                "type": "string"
                                            },    
                                            
                                            "reprintinfo": {
                                                "type": "object",
                                                "properties": {
                                                    "author": {
                                                        "type": "string"
                                                    },
                                                    "address": {
                                                        "type": "string"
                                                    },
                                                     "organizations": {
                                                        "type": "string"
                                                    }
                                                }
                                            },
                                            "email": {
                                                "type": "string"
                                            },
                                            "ridinfo": {
                                                "type": "object",
                                                "properties": {
                                                    "name": {
                                                        "type": "string"
                                                    },
                                                    "rid": {
                                                        "type": "string"
                                                    },
                                                    "orcid": {
                                                        "type": "string"
                                                    }
                                                }
                                            },
                                            "fundinginfo": {
                                                "type": "object",
                                                "fundingtxt": {
                                                    "type": "string"
                                                },
                                                "fundingag": {
                                                    "type": "object",
                                                    "properties": {
                                                        "agency": {
                                                            "type": "string"
                                                        },
                                                        "grantno": {
                                                            "type": "string"
                                                        }
                                                    }
                                                }
                                            },
                                            "publishers": {
                                                "type": "object",
                                                "properties": {
                                                    "name": {
                                                        "type": "string"
                                                    },
                                                    "address": {
                                                        "type": "string"
                                                    }
                                                }
                                            },
                                            "woscategory": {
                                                "type": "string"
                                            },
                                            "researchareas": {
                                                "type": "string"
                                            },
                                            "doctype": {
                                                "type": "string"
                                            },
                                            "languages": {
                                                "type": "string"
                                            },
                                            "accno": {
                                                "type": "string"
                                            },
                                            "pmid": {
                                                "type": "string"
                                            },
                                            "issn": {
                                                "type": "string"
                                            },
                                            "eisbn": {
                                                "type": "string"
                                            },
                                            "bookchapter": {
                                                "type": "string"
                                            },
                                            "bookdoi": {
                                                "type": "string"
                                            },
                                            "isbn": {
                                                "type": "string"
                                            },
                                            "citingsrcscount": {
                                                "type": "integer"
                                            },
                                            "citedrefcount": {
                                                "type": "integer"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }""" % (shards, replicas)
    wos_file = open("wos.mapping", "wa")
    wos_file.write(wos_file_ins)
    wos_file.close()

def load_syn_files(es_host_name, directory):
    es_hosts = []
    command = "curl -s '" + es_host_name + ":9200/_nodes?pretty'| grep '" + '"' + 'ip' + '"' + "'"
    output = shell_command_execute(command)
    elastic_instances = output.split(':')
    for instance in elastic_instances:
        if '1' not in str(instance):
            continue
        else:
            es_hosts.append(instance.replace(',', '').replace('ip','').replace('"', '').strip())
    #remove old host ansible file to create a new one.
    
    print 'Removing old Ansible host file'
    command = "rm -rf copy_syn_host"
    shell_command_execute(command)
    
    print 'Creating new ansible host file.'
    build_string = '[all]\n' + str(es_hosts).replace(',', '\n').replace(']', '').replace('[','').replace("'",'')
    command = ('echo "%s" >> copy_syn_host'%(build_string))
    shell_command_execute(command)
    
    files = ['en_synonyms.txt','en_lem_NAV.txt','en_synonyms_address.txt']
    for file in files:
        command = ('ansible all -i %s/copy_syn_host -m copy -a "src=%s/%s dest=/etc/elasticsearch/%s owner=root group=root" -u ec2-user -s' % (directory, directory, file, file))
        output = shell_command_execute(command)

def set_settings(settings_flag,es_host_name):
    if settings_flag == 'ins':
        es_settings = """curl -XPUT http://""" + es_host_name + """:9200/_cluster/settings -d '{
            "persistent" : {
            "cluster.routing.allocation.awareness.attributes": "aws_availability_zone",
            "cluster.routing.allocation.awareness.force.aws_availability_zone.values": "us-west-2c,us-west-2b,us-west-2a",
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
        }'"""
        shell_command_execute(es_settings)
    else:
        es_settings = """curl -XPUT http://""" + es_host_name + """:9200//_cluster/settings -d '{
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--threads', help='Number of threads', required=False)
    parser.add_argument('--host', help='ES Host Address', required=False)
    parser.add_argument('--wos', help='ES WOS', required=False)
    parser.add_argument('--shards', help='ES Shards', required=False)
    parser.add_argument('--replicas', help='ES Replicas', required=False)
    parser.add_argument('--index', help='ES index', required=False)
    parser.add_argument('--access_key', help='aws access key', required=False)
    parser.add_argument('--secret_key', help='aws secret key', required=False)
    parser.add_argument('--bucket', help='aws s3 bucket', required=False)
    parser.add_argument('--folder', help='aws s3 data folder', required=False)
    parser.add_argument('--region', help='aws region', required=False)
    args = parser.parse_args()
    
    access_key = args.access_key
    secret_key = args.secret_key
    failures = []
    wos_data = args.wos
    es_host_name = args.host
    threads = args.threads
    shards = args.shards
    replicas = args.replicas
    index = args.index
    bucket = args.bucket
    folder = args.folder
    region = args.region

    conn = boto.ec2.connect_to_region(region,
                                      aws_access_key_id=access_key, 
                                      aws_secret_access_key=secret_key)
    
    #download the loading data.    
    directory = download_s3(failures, 
                            wos_data, 
                            bucket,
                            folder,
                            access_key, 
                            secret_key)
    
    #Download and load synonym files to all instances in the ES cluster is done by calling the following two functions.
    directory_uploadfiles = download_s3_files('1pelasticsearch-data', 
                                              access_key, 
                                              secret_key)
    load_syn_files(es_host_name, directory_uploadfiles)
    
    make_mapping(shards, replicas)
    
    directory = directory[1] + '/' + 'json_data/wos/'+folder+'/' + wos_data
    
    set_settings('ins', es_host_name)
    location = os.path.dirname(os.path.realpath(__file__)) + '/load-es.py'
    mapping = os.path.dirname(os.path.realpath(__file__)) + '/wos.mapping'
    type = 'wos'
    command = ("""python %s --data %s --host %s --index %s --type %s --mapping %s --threads %s""" % (location, 
                                                                                                     directory, 
                                                                                                     es_host_name, 
                                                                                                     index, 
                                                                                                     type, 
                                                                                                     mapping, 
                                                                                                     threads ))
    
    p = multiprocessing.Process(name='loading worker process', target=spawn_worker_node, args=(command))
    p.daemon = True
    p.start()
    conn.close()
    print 'Daemon has been executed. Program will now exit.'
    
