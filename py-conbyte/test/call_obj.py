import sub_import
from d_import import *

glo = 2

class InnerClass:
    def __init__(self, a):
        self.ia = a

    def __str__(self):
        return str(self.ia)
    
    def compare(self, t):
        if self.ia > t:
            return 0
        else:
            return 1

class TheClass:
    def __init__(self, a, b):
        self.sa = a
        self.sb = b
        self.inner = InnerClass(a)

    def __str__(self):
        return "%s %s" % (self.sa, self.sb)

    def add(self, i):
        a = self.sa 
        b = self.inner.compare(self.sb)
        return b

def call_obj(a, b):
    # does have branch, just testing
    d = sub_import.sub_func(a, b) + sub_import.sub_func(a, b)
    e = sub_import.TheSubClass("abc")


    c = TheClass(a, b)
    res = c.add(glo)
    return res 
