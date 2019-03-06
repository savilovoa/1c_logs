# -*- coding: utf-8 -*-

import sys
from elasticsearch import Elasticsearch
import logging
from send2elastic import send_2_elastic
import configparser
from logs_1c import scan_1c_logs


logging.basicConfig(filename = "1с_log_scan.log", level=logging.WARN)
logs = send_2_elastic()
if logs.connect_elasticsearch([{'host': 'elk.id.local', 'port': 9200}]):    
            if logs.create_index("erp_prod"):
                        logs.loads("")
        
                    






