# -*- coding: utf-8 -*-
import logging
from logging.handlers import RotatingFileHandler

# настройка логгирования
logger = logging.getLogger("log_test")
logger.setLevel(logging.INFO)

formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
# create console handler and set level to info
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)

logger.addHandler(handler)
logger.info("Test str")


