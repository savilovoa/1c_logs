# -*- coding: utf-8 -*-

import sys
from elasticsearch import Elasticsearch
import logging
from send2elastic import *
import configparser


if len(sys.argv) > 1:
    fn_name = sys.argv[1] # "d:/20190210000000.lgp"
else:
    fn_name = "d:/20190221000000.lgp"

logging.basicConfig(filename = "1с_log_scan.log", level=logging.WARN)    
logs = send_2_elastic(False, [{'host': 'elk.id.local', 'port': 9200}])
if logs.connect_elasticsearch():
    if logs.lgf_load("d:/1cv8.lgf"):
        logs.create_index("erp_prod")
        if logs.scan_file():
            print("Ok")
        
                    






