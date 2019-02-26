# -*- coding: utf-8 -*-

import re
import sys
import pathlib
import os
from os import path
from elasticsearch import Elasticsearch
from logs_1c import *
import logging


class send_2_elastic(scan_1c_logs):
    def __init__(self, file_name: str, info: bool=False, connect=[{'host': 'localhost', 'port': 9200}]):
        super(send_2_elastic, self).__init__(file_name, info)
        self.connect = connect
        self.index_name = ""        
                
    def connect_elasticsearch(self):
        self.es = None
        self.es = Elasticsearch(self.connect)
        if self.es.ping():
            print('Yay Connect')
        else:
            print('Awww it could not connect!')


    def create_index(index_name='erp_prod'):
        created = False
        self.index_name = index_name
        # index settings
        settings = {
            "settings": {
              "index": {
                "number_of_shards": "2",
                "number_of_replicas": "0",
                "refresh_interval": "10s"
              }
            },
            "mappings": {
              "_default_": {
                "properties": {
                  "@timestamp": {
                    "type": "date"
                  },
                  "path": {
                    "type": "text"
                  },
                  "User": {
                    "type": "keyword"
                  },
                  "UserId": {
                    "type": "text"
                  },
                  "Data1": {
                    "type": "text"
                  },
                  "Data2": {
                    "type": "text"
                  },
                  "SecondIpPort": {
                    "type": "text"
                  },
                  "Metadata": {
                    "type": "keyword"
                  },
                  "MetadataId": {
                    "type": "text"
                  },
                  "Importance": {
                    "type": "text"
                  },
                  "MoreMetadata": {
                    "type": "text"
                  },
                  "Computer": {
                    "type": "keyword"
                  },
                  "ComputerId": {
                    "type": "text"
                  },
                  "WorkServer": {
                    "type": "keyword"
                  },
                  "WorkserverId": {
                    "type": "text"
                  },
                  "Comment": {
                    "type": "text"
                  },
                  "NumberTransaction": {
                    "type": "text"
                  },
                  "Connection": {
                    "type": "text"
                  },
                  "StatusTransaction": {
                    "type": "text"
                  },
                  "MainIpPort": {
                    "type": "text"
                  },
                  "Transaction": {
                    "type": "text"
                  },
                  "NameApplication": {
                    "type": "keyword"
                  },
                  "NameApplicationId": {
                    "type": "text"
                  },
                  "RepresentationData": {
                    "type": "text"
                  },
                  "Event": {
                    "type": "keyword"
                  },
                  "EventId": {
                    "type": "text"
                  },
                  "ArrayDataType": {
                    "type": "text"
                  },
                  "Session": {
                    "type": "text"
                  }
                }
              }
            },
            "aliases": {}
        }        
        try:
            if not self.es.indices.exists(index_name):
                # Ignore 400 means to ignore "Index Already Exist" error.
                self.es.indices.create(index=index_name, ignore=400, body=settings)
                print('Created Index')
            created = True
        except Exception as ex:
            print(str(ex))
        finally:
            return created

    def store_record(record):
        try:
            if self.index_name != "":
                outcome = self.es.index(index=self.index_name, doc_type='log1c', body=record)
        except Exception as ex:
            print('Error in indexing data')
            print(str(ex))
    

        
    def __message_add__(self, mess):
        doc = {
                '@timestamp': mess[0],
                'path': mess[1],
                "User": {
                  "type": "keyword"
                },
                "UserId": {
                  "type": "text"
                },
                "Data1": {
                  "type": "text"
                },
                "Data2": {
                  "type": "text"
                },
                "SecondIpPort": {
                  "type": "text"
                },
                "Metadata": {
                  "type": "keyword"
                },
                "MetadataId": {
                  "type": "text"
                },
                "Importance": {
                  "type": "text"
                },
                "MoreMetadata": {
                  "type": "text"
                },
                "Computer": {
                  "type": "keyword"
                },
                "ComputerId": {
                  "type": "text"
                },
                "WorkServer": {
                  "type": "keyword"
                },
                "WorkserverId": {
                  "type": "text"
                },
                "Comment": {
                  "type": "text"
                },
                "NumberTransaction": {
                  "type": "text"
                },
                "Connection": {
                  "type": "text"
                },
                "StatusTransaction": {
                  "type": "text"
                },
                "MainIpPort": {
                  "type": "text"
                },
                "Transaction": {
                  "type": "text"
                },
                "NameApplication": {
                  "type": "keyword"
                },
                "NameApplicationId": {
                  "type": "text"
                },
                "RepresentationData": {
                  "type": "text"
                },
                "Event": {
                  "type": "keyword"
                },
                "EventId": {
                  "type": "text"
                },
                "ArrayDataType": {
                  "type": "text"
                },
                "Session": {
                  "type": "text"
                }
                
            }

    




    
    

