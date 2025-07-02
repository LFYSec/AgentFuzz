# Copyright: see copyright.txt
import logging

from .predicate import Predicate
from .constraint import Constraint


log = logging.getLogger("ct.pathconstraint")

class PathToConstraint:
    def __init__(self, add):
        self.constraints = []
        self.root_constraint = Constraint(None, None)
        self.current_constraint = self.root_constraint
        self.expected_path = None
        self.add = add

    def reset(self, expected):
        self.current_constraint = self.root_constraint
        if expected is None:
            self.expected_path = None
        else:
            self.expected_path = []
            tmp = expected
            while tmp.predicate is not None:
                self.expected_path.append(tmp.predicate)
                tmp = tmp.parent

    def which_branch(self, concolic_type, process_neg=True):
        if concolic_type.expr == 'nil':
            log.debug("Skip nil")
            return

        if isinstance(concolic_type.expr, bool):
            # Pure bool type assignment is normally not codition branch
            return

        p = Predicate(concolic_type, concolic_type.value)
        c = self.current_constraint.find_child(p)
        pneg = p.negate()
        cneg = self.current_constraint.find_child(p)

        if c is None and cneg is None:
            c = self.current_constraint.add_child(p)
            c.processed = True
            if not process_neg:
                log.debug("Singel constraint %s" % c)
            else:
                cneg = self.current_constraint.add_child(pneg)
                # we add the new constraint to the queue of the engine for later processing
                self.add(cneg)
                log.debug("Cur constraint %s" % c)
                log.debug("Add constraint %s" % cneg)

        self.current_constraint = c

        # check for path mismatch
        # IMPORTANT: note that we don't actually check the predicate is the
        # same one, just that the direction taken is the same
        """
        if self.expected_path is not None and self.expected_path != []:
            expected = self.expected_path.pop()
            # while not at the end of the path, we expect the same predicate result
            # at the end of the path, we expect a different predicate result
            done = self.expected_path == []
            if (not done and expected.result != c.predicate.result or
                            done and expected.result == c.predicate.result):
                log.info("Replay mismatch (done=%s)" % done)
                log.debug(expected)
                log.debug(c.predicate)
        """

        self.current_constraint = c


    def find_constraint(self, id):
        return self._find_constraint(self.root_constraint, id)

    def _find_constraint(self, constraint, id):
        if constraint.id == id:
            return constraint
        else:
            for child in constraint.children:
                found = self._find_constraint(child, id)
                if found is not None:
                    return found
        return None


