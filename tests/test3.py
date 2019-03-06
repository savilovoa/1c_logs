# -*- coding: utf-8 -*-
from datetime import datetime
import logging

class t1(object):
    def foo(self):
        print("t1")
        
    def foo2(self):
        self.foo()

        
        
class t2(t1):
    def foo(self):
        #super(t2, self).foo()
        print("t2")
        
        
c = t2()
c.foo2()
#yyyyMMddHHmmss
#my_str = '20190220093807'
my_str = '20190220093807'
print(datetime.strptime(my_str, "%Y%m%d%H%M%S"))

# create logger
logger = logging.getLogger('simple_example')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s- %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

# 'application' code
logger.debug('debug message')
logger.info('info message')
logger.warn('warn message')
logger.error('error message')
logger.critical('critical message')