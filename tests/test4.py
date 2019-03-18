
class foo1(object):
    def p1(self):
        print("Ok")
    
    
class foo2(object):
    def p2(self, obj):
        l = obj()
        l.p1()
        
f = foo2()
f.p2(foo1)