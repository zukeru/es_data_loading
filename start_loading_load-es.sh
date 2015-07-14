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

echo "
{
    "settings": {
        "number_of_shards": "$shards",
        "number_of_replicas": "$replicas",
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
}
" >> $WORKSPACE/wos.mapping

python $WORKSPACE/load-es.py --data "$wos" --host $host --index $index --port $port --type $type --mapping $WORKSPACE/$mapping --threads $threads
