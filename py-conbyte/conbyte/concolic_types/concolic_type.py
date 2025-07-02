# Copyright: see copyright.txt

import inspect
import functools

import logging
import sys

log = logging.getLogger("ct.con.type")

class ConcolicType(object):
    def __init__(self, expr=None, value=None):
        self.expr = expr
        self.value = value
        log.debug("  ConType, value %s, expr: %s" % (value, expr))

    def to_formula(self):
        expr = self.expr
        formula = self._to_formula(expr)
        return formula

    def _to_formula(self, expr):
        if isinstance(expr, list):
            formula = "( "
            for exp in expr:
                formula += self._to_formula(exp) + " "
            return formula + " )"
        else:
            if isinstance(expr, int):
                if expr < 0:
                    ret = "(- %s)" % -expr
                else:
                    ret = str(expr)
                return ret
            else:
                return str(expr)

    def get_concrete(self):
        return self.value
    
    def compare_op(self, operator, other):
        val_l = self.value
        val_r = other.value
        if operator == "==":
            value = val_l == val_r
            expr = ["=", self.expr, other.expr]
        elif operator == "!=":
            value = val_l != val_r
            expr = ['not', ["=", self.expr, other.expr]]
        elif operator == ">":
            value = val_l > val_r
            expr = [operator, self.expr, other.expr]
        elif operator == "<":
            value = val_l < val_r
            expr = [operator, self.expr, other.expr]
        elif operator == ">=":
            value = val_l >= val_r
            expr = [operator, self.expr, other.expr]
        elif operator == "<=":
            value = val_l <= val_r
            expr = [operator, self.expr, other.expr]
        else:
            return None

        return ConcolicType(expr, value)

    def symbolic_eq(self, other):
        return self._eq_worker(self.expr, other.expr)

    def _eq_worker(self, expr1, expr2):
        if isinstance(expr1, list):
            if not isinstance(expr2, list):
                return False
            else:
                if len(expr1) != len(expr2):
                    return False
                for i in range(len(expr1)):
                    if not self._eq_worker(expr1[i], expr2[i]):
                        return False
                return True
        else:
            return expr1 == expr2

    def __eq__(self, other):
        if self.value != other.value:
            return False
        else:
            return self._eq_worker(self.expr, other.expr)

    # TODO
    def __or__(self, other):
        value = self.value | other.value
        expr = ["and", self.expr, other.expr]
        return ConcolicType(expr, value)

    # TODO
    def __xor__(self, other):
        value = self.value ^ other.value
        expr = ["xor", self.expr, other.expr]
        return ConcolicType(expr, value)

    # TODO
    def __and__(self, other):
        value = self.value & other.value
        expr = ["and", self.expr, other.expr]
        return ConcolicType(expr, value)

    # For bool type
    def negate(self):
        self.value = not self.value
        self.expr = ['not', self.expr]

    def __str__(self):
        return "{ConType, value: %s, expr: %s)" % (self.value, self.expr)
