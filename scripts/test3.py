# -*- coding: utf-8 -*-
from datetime import datetime

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
