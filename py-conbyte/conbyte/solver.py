import logging
import sys
import time
import os
from subprocess import Popen, PIPE, STDOUT
from hashlib import sha224
import subprocess
from string import Template

log = logging.getLogger("ct.solver")

class Solver(object):
    options = {"lan": "smt.string_solver=z3str3", "stdin": "-in"}
    cvc_options = ["--produce-models", "--lang", "smt", "--strings-exp", "--quiet"]
    cnt = 0

    def __init__(self, query_store, solver_type, ss):
        self.query = None
        self.asserts = None
        self.prefix = None
        self.ending = None
        self.variables = dict()
        self.query_store = query_store
        self.solver_type = solver_type
        self.ss = ss

        if solver_type == "z3seq":
            self.cmd = "z3 -in"
        elif solver_type == "z3str":
            self.cmd = "z3"
            for option in self.options:
                self.cmd = self.cmd + " " + self.options[option]
        elif solver_type == "trauc":
            self.cmd = "trauc"
            for option in self.options:
                self.cmd = self.cmd + " " + self.options[option]
        elif solver_type == "cvc4":
            self.cmd = "cvc4"
            for option in self.cvc_options:
                self.cmd = self.cmd + " " + option



    def set_variables(self, variables):
        self.varables = variables
        for v in variables:
            self.variables[v] = variables[v]


    def find_counter_example(self, asserts, query, extend_vars, extend_queries, timeout=None):
        start_time = time.process_time()
        if "z3" in self.solver_type or  "trauc" in self.solver_type:
            if timeout is not None:
                cmd = self.cmd + " -T:" + str(timeout)
            else:
                cmd = self.cmd + " -T:1"
        else:
            if timeout is not None:
                cmd = self.cmd + (" --tlimit=%s" % (int(timeout) * 1000))
            else:
                cmd = self.cmd + " --tlimit=1000"
        self.asserts = asserts
        self.query = query
        result, model = self._find_model(cmd, extend_vars, extend_queries)
        endtime = time.process_time()
        solve_time = endtime - start_time
        return result, model


    def _find_model(self, cmd, extend_vars, extend_queries):

        formulas = self._build_expr(extend_vars, extend_queries)

        # log.debug("\n" + formulas)
        if self.query_store is not None:
            #smthash = sha224(bytes(str(self.query), 'UTF-8')).hexdigest()
            #filename = os.path.join(self.query_store, "{}.smt2".format(smthash))
            filename = os.path.join(self.query_store, "{}.smt2".format(self.cnt))
            with open(filename, 'w') as f:
                f.write(formulas)

        model = None
        try:
            process = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        except subprocess.CalledProcessError as e:
            print(e.output)

        stdout, stderr = process.communicate(input=formulas.encode())

        log.debug("\n" + stdout.decode())

        output = stdout.decode()
        # print(formulas)
        # print(output)

        if output is None or len(output) == 0:
            ret = "UNKNOWN"
        else:
            output = output.splitlines()
            while "error" in output[0]:
                output.pop(0)
            ret = output[0].lower()
            if "unsat" in ret:
                ret = "UNSAT"
            elif "sat" in ret:
                ret = "SAT"
                model = self._get_model(output[1:])
            elif "timeout" in ret:
                ret = "TIMEOUT"
            elif "unknown" in ret and "error" not in stdout.decode():
                model = self._get_model(output[1:])
            else:
                ret = "UNKNOWN"

        log.debug("%s smt, Result: %s" % (self.cnt, ret))
        self.cnt += 1
        return ret, model


    def _get_model(self, models):
        model = dict()
        for line in models:
            name, value = line.replace("((", "").replace("))", "").split(" ", 1)
            if self.variables[name] == "Int":
                if "(" in value:
                    value = value.replace("(", "").replace(")", "").split(" ")[1]
                    result = -int(value)
                else:
                    result = int(value)
            else:
                value = value.replace("\"", "", 1).replace("\"", "", -1)
                result = value

            if name.startswith("_ARR_"):
                name = name.replace("_ARR_", "").split("_", 1)[1]
                if name not in model:
                    model[name] = list()
                model[name].append(result)
            else:
                model[name] = result
        return model


    def _build_expr(self, extend_vars, extend_queries):
        f_template = Template("""
$declarevars

$query

(check-sat)

$getvars
""")
        assignments = dict()
        assignments['declarevars'] = "\n"
        for (name, var) in self.variables.items():
            if var != "List":
                assignments['declarevars'] += "(declare-fun {} () {})\n".format(name, var)

        for (name, var) in extend_vars.items():
            assignments['declarevars'] += "(declare-fun {} () {})\n".format(name, var)

        assignments['query'] = "\n".join(assertion.get_formula() for assertion in self.asserts)
        assignments['query'] += self.query.get_formula()
        if self.ss:
            assignments['query'] += "(assert (str.in.re a (re.+ (re.range \"0\" \"1\"))))\n"
            assignments['query'] += "(assert (str.in.re b (re.+ (re.range \"0\" \"1\"))))\n"

        for query in extend_queries:
            assignments['query'] += "%s\n" % query

        assignments['getvars'] = "\n"
        for name, var in self.variables.items():
            if var != "List":
                assignments['getvars'] += "(get-value ({}))\n".format(name)
        return f_template.substitute(assignments).strip()
