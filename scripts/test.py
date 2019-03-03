# -*- coding: utf-8 -*-

import sys
from elasticsearch import Elasticsearch
import logging
from send2elastic import send_2_elastic
import configparser
from logs_1c import scan_1c_logs


if len(sys.argv) > 1:
    fn_name = sys.argv[1] # "d:/20190210000000.lgp"
else:
    fn_name = "C:/Users/User/YandexDisk/Prog/logstash/2019022000099.lgp"

logging.basicConfig(filename = "1с_log_scan.log", level=logging.WARN)
logs = scan_1c_logs()
logs.loads("C:/Users/User/YandexDisk/Prog/logstash")
#logs.scan_file(fn_name)
exit(0) 

logs = send_2_elastic()
if logs.connect_elasticsearch([{'host': 'elk.id.local', 'port': 9200}]):
    if logs.lgf_load("d:/1cv8.lgf"):
        logs.create_index("erp_prod")
        if logs.loads():
            print("Ok")
        
                    






