# -*- coding: utf-8 -*-

import re
import sys
import os
from os import path
from elasticsearch import Elasticsearch
from logs_1c import scan_1c_logs, logger
from datetime import datetime
import time

class send_2_elastic(scan_1c_logs):
    connect = [{'host': 'localhost', 'port': 9200}]
    index_name = ""
    es = None
    def __init__(self):
        super(send_2_elastic, self).__init__()
        if self.config.has_option("ELASTICSEARCH", "host"):
             self.connect[0]['host'] = self.config.get("ELASTICSEARCH", "host")
        if self.config.has_option("ELASTICSEARCH", "port"):
            self.connect[0]["port"] = self.config.getint("ELASTICSEARCH", "port")
        if self.config.has_option("ELASTICSEARCH", "index_name"):
            self.index_name = self.config.get("ELASTICSEARCH", "index_name")


    def connect_elasticsearch(self, connect = []):
        self.es = None
        if connect != []:
            self.connect = connect
        try:
            self.es = Elasticsearch(self.connect)
            if self.es.ping():
                logger.info("Connection SUCCESS!")
                return True
            else:
                logger.info("Not connection in {}".format(self.connect))
                return False
        except:
            logger.error("Connection in {}".format(self.connect))
            return False


    def create_index(self, index_name='erp_prod', index_date=""):
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
                    "type": "keyword"
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
            i = index_name+index_date
            if not self.es.indices.exists(i):
                # Ignore 400 means to ignore "Index Already Exist" error.
                self.es.indices.create(index=i, body=settings)
                logger.info('create index {}'.format(i))
            created = True
        except Exception:
            logger.exception()
        finally:
            return created

    def store_record(self, rec_id, record, indexdate=""):
        try:
            if self.index_name != "":
                if indexdate != "":
                    if not self.create_index(self.index_name, indexdate):
                        raise RuntimeError("Not create index {}".format(self.index_name + indexdate))
                self.es.index(index=self.index_name + indexdate, id=rec_id, doc_type='log1c', body=record)                                    
                logger.debug('{}: {}'.format(self.index_name + indexdate, record))
            else:
                raise RuntimeError("Not index name")
        except Exception:
            logger.error("STORE RECORD {} {} {}".format(self.index_name + indexdate, rec_id, record), exc_info=True)
            



    def message_add(self, rec_id, mess):

        user = dict(self.users).setdefault(mess[4])
        comp = dict(self.computers).setdefault(mess[5])
        appsname = dict(self.appsname).setdefault(mess[6])
        event = dict(self.events).setdefault(mess[8])
        mdata = dict(self.metadata).setdefault(mess[11])
        # пропускаем начало и конец транзакций обмена
        if user == "wsdl" and mess[10] == '' and mess[11]=="0" and mess[9] == "I":            
            logger.debug("Skip {} {}".format(rec_id, mess))
            return False

        #mdata_guid = self.metadata_guid[mess[11]]
        server = dict(self.servers).setdefault(mess[14])
        p = dict(self.ports).setdefault(mess[15])
        portadv = dict(self.portsadv).setdefault(mess[16])
        doc = {
                '@timestamp': datetime.strptime(mess[0], "%Y%m%d%H%M%S"),
                "User": user,
                "UserId": mess[4],
                "Data1": mess[12],
                "SecondIpPort": portadv,
                "Metadata": mdata,
                "MetadataId": mess[11],
                "Importance": mess[9],
                "MoreMetadata": mess[18],
                "Computer": comp,
                "ComputerId": mess[5],
                "WorkServer": server,
                "WorkserverId": mess[14],
                "Comment": mess[10],
                "NumberTransaction": mess[3],
                "Connection": mess[7],
                "StatusTransaction": mess[1],
                "MainIpPort": p,
                "Transaction": mess[2],
                "NameApplication": appsname,
                "NameApplicationId": mess[6],
                "RepresentationData": mess[13],
                "Event": event,
                "EventId": mess[8],
                "Session": mess[17]
            }
        index_date = "-" + mess[0][:8]
        self.store_record(rec_id, doc, index_date)
        logger.debug("{} {}".format(rec_id, mess))
        return True




i = 0
logs = send_2_elastic()
while True:
    if logs.connect_elasticsearch():   
        logs.loads()
    time.sleep(30)
    i += 1
    if i > 1000:
        Exit(1)
