
# Imported by call_obj.py

import sub_sub_import

class TheSubClass:
    def __init__(self, value:str):
        self.sub = sub_sub_import.TheSubSubClass(value)
        self.value = sub_sub_import.sub_sub_func(value, value)
        self.value = value

    def __str__(self):
        return self.value

def sub_func(a, b):
    a = a + 1
    return a
