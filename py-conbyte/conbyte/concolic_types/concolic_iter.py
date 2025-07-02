from ..utils import *
from .concolic_int import *
from .concolic_str import *
from .concolic_list import *
from .concolic_map import *


class ConcolicIter():
    def __init__(self, target):
        self.target = target
        if isinstance(target, Concolic_range):
            self.index = None
        else:
            self.index = ConcolicInteger(0)

    def next_iter(self):
        target = self.target
        if isinstance(target, Concolic_range):
            return target.next_iter()
        else:
            ret = None
            if isinstance(target, ConcolicStr):
                length = target.len()
                cond_val = self.index.value < length.value
                cond_expr = ["<", self.index.expr, length.expr]
                condition = ConcolicType(cond_expr, cond_val)
                if cond_val:
                    ret = target.get_index(self.index)
            elif isinstance(target, ConcolicList):
                length = target.len().value
                cond_val = self.index.value < length
                condition = ConcolicType("nil", cond_val)
                if cond_val:
                    ret = target.get_index(self.index)

            elif isinstance(target, ConcolicMap):
                length = target.len().value
                cond_val = self.index.value < length
                condition = ConcolicType("nil", cond_val)
                if cond_val:
                    ret = target.get_iter_at(self.index)
            
            self.index += ConcolicInteger(1)
            return condition, ret
