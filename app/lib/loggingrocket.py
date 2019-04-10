# -*- coding: utf-8 -*-
from rocketchat.api import RocketChatAPI
import logging
from logging import Handler
import json
from datetime import datetime, timedelta
from logs_1c import config, logger
import time

BOT_USER = ""
BOT_PW = ""
# errors            
BOT_ROOT="vsbndLtYixmmoQCo5"

def RocketSendMessage (message, to=BOT_ROOT):
    api = RocketChatAPI(settings={'username': BOT_USER, 'password': BOT_PW,
                              'domain': 'https://chat.limak.ru'})
    #print (api.get_private_rooms())
    api.send_message(message, to)
    return True

class RocketHandler(Handler,object):
    LastMessage=""
    LastDttm =  time.time()

    def __init__(self):
        super(RocketHandler, self).__init__()

    def parse_record_to_json(self, record):
        return {
            'timestamp': datetime.fromtimestamp(self.LastDttm).strftime('%m/%d/%Y %H:%M:%S'),
            'Prog': '1c_logs_to_elastic',
            'method': record.funcName,
            'level': record.levelname,            
            'module': record.module,
            'message': self.LastMessage,            
        }

    def emit(self,record):
        created = datetime.fromtimestamp(record.created)        
        d = int(record.created - self.LastDttm)
        s = record.getMessage()
        if self.LastMessage == s:
            if d > 3600:
                self.LastMessage = s
                self.LastDttm = record.created
                RocketSendMessage (str(self.parse_record_to_json(record)))
        else:
            self.LastMessage = s
            self.LastDttm = record.created
            RocketSendMessage (str(self.parse_record_to_json(record)))            
        



if config.has_option("GLOBAL", "bot_user"):
    BOT_USER = config.get("GLOBAL", "bot_user")
if config.has_option("GLOBAL", "bot_pw"):
    BOT_PW = config.get("GLOBAL", "bot_pw")

if config.has_option("GLOBAL", "bot_root"):
    BOT_ROOT = config.get("GLOBAL", "bot_root")

if BOT_USER != "" and BOT_PW != "" and BOT_ROOT != "":
    handler = RocketHandler()
    handler.setLevel(logging.ERROR)
    logger.addHandler(handler)
