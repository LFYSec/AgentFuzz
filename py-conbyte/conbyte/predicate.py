# Copyright - see copyright.txt

class Predicate:
    def __init__(self, con, result):
        self.concolic = con
        self.result = result

    def negate(self):
        """Negates the current predicate"""
        assert (self.result is not None)
        return Predicate(self.concolic, not self.result)

    def __eq__(self, other):
        if isinstance(other, Predicate):
            res = self.result == other.result and self.concolic.symbolic_eq(other.concolic)
            return res
        else:
            return False

    def get_formula(self):
        expr = self.concolic.expr
        formula =  self._get_formula(expr)
        if self.result is True:
            return "(assert " + formula + ")\n"
        else:
            return "(assert (not " + formula + "))\n"

    def _get_formula(self, expr):
        if isinstance(expr, list):
            formula = "( "
            for exp in expr:
                formula += self._get_formula(exp) + " "
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

    def __str__(self):
        return "Result: %s\tExpr: %s" % (self.result, self.concolic.expr)
