# -*- coding: utf-8 -*-
import logging
import os
from logging.handlers import RotatingFileHandler
import time


# настройка логгирования
logger = logging.getLogger("log_test")
logger.setLevel(logging.INFO)

formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
# create console handler and set level to info
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)


os.environ['TZ'] = 'Europe/Moscow'
time.tzset()

logger.addHandler(handler)
logger.info("Test str")
print (time.localtime())


