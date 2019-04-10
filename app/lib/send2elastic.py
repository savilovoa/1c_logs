# -*- coding: utf-8 -*-

import re
import sys
import os
from os import path
from elasticsearch import Elasticsearch
from logs_1c import scan_1c_logs, logger, config, multilogs
from datetime import datetime
import time
import loggingrocket

test_not_elk = False
if config.has_option("ELASTICSEARCH", "test_not_elk"):
    test_not_elk = config.get("ELASTICSEARCH", "test_not_elk")

def connect_elasticsearch(connect = []):
    es = None
    connected = False
    if test_not_elk:
        return True, None
    try:
        es = Elasticsearch(connect)
        if es.ping():
            logger.info("Connection SUCCESS!")
            connected = True
        else:
            logger.info("Not connection in {}".format(connect))
    except:
        logger.error("Connection in {}".format(connect))
    finally:
        return connected, es



class send_2_elastic(scan_1c_logs):
    es = None
    def __init__(self, dbname, logsdir, es):
        self.es = es
        super(send_2_elastic, self).__init__(dbname, logsdir)


    def create_index(self, indexname):
        created = False
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
            if not self.es.indices.exists(indexname):
                # Ignore 400 means to ignore "Index Already Exist" error.
                self.es.indices.create(index=indexname, body=settings)
                logger.info('create index {}'.format(indexname))
            created = True
        except Exception:
            logger.error("CREATE INDEX {}".format(indexname), exc_info=True)
        finally:
            return created

    def store_record(self, rec_id, record, indexname):
        try:
            if self.es == None:
                return True
            if not self.create_index(indexname):
                raise RuntimeError("Not create index {}".format(indexname))
            self.es.index(index=indexname, id=rec_id, doc_type='log1c', body=record)
            logger.debug('{}: {}'.format(indexname, record))
        except Exception:
            logger.error("STORE RECORD {} {} {}".format(indexname, rec_id, record), exc_info=True)




    def message_add(self, rec_id, mess):

        user = dict(self.users).setdefault(mess[4])
        comp = dict(self.computers).setdefault(mess[5])
        appsname = dict(self.appsname).setdefault(mess[6])
        event = dict(self.events).setdefault(mess[8])
        mdata = dict(self.metadata).setdefault(mess[11])
        # пропускаем начало и конец транзакций обмена
        if user in ["wsdl", "1C"] and mess[10] == '' and mess[11]=="0" and mess[9] == "I":
            logger.debug("Skip {} {}".format(rec_id, mess))
            return False

        #mdata_guid = self.metadata_guid[mess[11]]
        server = dict(self.servers).setdefault(mess[14])
        p = dict(self.ports).setdefault(mess[15])
        portadv = dict(self.portsadv).setdefault(mess[16])
        doc = {
                '@timestamp': datetime.strptime(mess[0]+"+0300", "%Y%m%d%H%M%S%z"),
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
        indexname = self.dbname + "-" + mess[0][:8]
        self.store_record(rec_id, doc, indexname)
        logger.debug("{} {} {}".format(indexname, rec_id, mess))
        return True


class multilogs_elk(multilogs):
    es = None
    connect = [{"host": "localhost", "port": 9200}]

    def __init__(self):
        super(multilogs_elk, self).__init__()
        if config.has_option("ELASTICSEARCH", "host"):
            self.connect[0]['host'] = config.get("ELASTICSEARCH", "host")
        if config.has_option("ELASTICSEARCH", "port"):
            self.connect[0]["port"] = config.getint("ELASTICSEARCH", "port")


    def logs_add(self, dbname, dirname):
        l = send_2_elastic(dbname, dirname, self.es)
        self.logs.append(l)

    def start(self):
        
        i = 0
        while True:
            connected, self.es = connect_elasticsearch(self.connect)
            if connected:
                # расставляем ссылки на объект elastic
                self.logs_build()
                e = 0
                while True:
                    for l in self.logs:
                        if not l.scandirs():
                            e += 1
                    time.sleep(self.rescan_sleep)
                    if e > 10000:
                        logger.error("Much errors. Exit(1)")
                        sys.exit(1)                        
            else:
                time.sleep(30)
                i += 1
                if i > 1000:
                    logger.error("Not connection in {}".format(self.connect))
                    sys.exit(1)


m = multilogs_elk()
m.start()