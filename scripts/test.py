# -*- coding: utf-8 -*-

import sys
from elasticsearch import Elasticsearch
import logging
from send2elastic import *


if len(sys.argv) > 1:
    fn_name = sys.argv[1] # "d:/20190210000000.lgp"
else:
    fn_name = "d:/2019022000099.lgp"

logging.basicConfig(filename = "1с_log_scan.log", level=logging.INFO)    
#logs = scan_1c_logs(fn_name)
#logs.scan_file()



se = send_2_elastic(fn_name, False, [{'host': '192.168.30.32', 'port': 9200}])
se.connect_elasticsearch()
                    

doc = {
                'eng': elem[0][0].text.encode('utf-8'),
                'rus': elem[1][0].text.encode('utf-8')
            }

    





