# Copyright: see copyright.txt

import logging
import inspect

class Constraint(object):
    cnt = 0
    def __init__(self, parent, last_predicate):
        self.inputs = None
        self.predicate = last_predicate
        self.processed = False
        self.parent = parent
        self.children = []
        self.id = self.__class__.cnt
        self.__class__.cnt += 1
        branch = self.predicate.result if self.predicate is not None else ""
        self.branch_id = self._branch_id(inspect.stack(), branch)

    def _branch_id(self, stack, branch):
        instrumentation_keywords = {"py-conbyte", "concolic"}
        for frame, filename, linenum, funcname, context, contextline in stack:
            if any(instrumentation_keyword in filename for instrumentation_keyword in instrumentation_keywords):
                continue
            return "{}:{}:{}".format(filename, linenum, branch)
        return None

    def __eq__(self, other):
        """Two Constraints are equal iff they have the same chain of predicates"""
        if isinstance(other, Constraint):
            if not self.predicate == other.predicate:
                return False
            return self.parent is other.parent
        else:
            return False

    def get_asserts_and_query(self):
        self.processed = True

        # collect the assertions
        asserts = []
        tmp = self.parent
        while tmp.predicate is not None:
            asserts.append(tmp.predicate)
            tmp = tmp.parent

        return asserts, self.predicate

    def get_length(self):
        if self.parent is None:
            return 0
        return 1 + self.parent.get_length()

    def find_child(self, predicate):
        for c in self.children:
            if predicate == c.predicate:
                return c
        return None

    def add_child(self, predicate):
        assert (self.find_child(predicate) is None)
        c = Constraint(self, predicate)
        self.children.append(c)
        return c

    def __lt__(self, other):
        return self.get_length() > other.get_length()

    def __str__(self):
        return str(self.predicate) + "  (processed: %s, path_len: %d)" % (self.processed, self.get_length())
