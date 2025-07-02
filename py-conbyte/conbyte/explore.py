import sys
import os
import logging
import dis
import inspect
import traceback
import json
import copy

import coverage
from func_timeout import func_timeout, FunctionTimedOut

from .utils import * 
from .function import *
from .frame import *
from .executor import *
from .path_to_constraint import *

from .concolic_types import concolic_type
from .solver import Solver 

log = logging.getLogger("ct.explore")
Target_line = 0
def print_inst(obj):
    lines = dis.get_instructions(obj)
    for line in lines:
        log.debug(line)

class ExplorationEngine:

    def __init__(self, path, filename, module, entry, ini_vars, query_store, solver_type, ss, target_line):
        # Set up import environment
        sys.path.append(path)
        self.t_module = __import__(module)
        if entry == None:
            self.entry = module
        else:
            self.entry = entry

        self.trace_into = []
        self.functions = dict()

        self.ini_vars = ini_vars
        self.symbolic_inputs = None 
        self.new_constraints = []
        self.constraints_to_solve = Queue()
        self.solved_constraints = Queue()
        self.finished_constraints = []
        self.num_processed_constraints = 0
        self.input_sets = []
        self.error_sets = []
        self.in_ret_sets = []

        self.global_execution_coverage = coverage.CoverageData()

        self.call_stack = Stack()
        self.mem_stack = Stack()

        self.path = PathToConstraint(lambda c: self.add_constraint(c))
        self.executor = Executor(self.path)

        """
        # Append builtin in trace_into
        """
        self.trace_into.append("__init__")
        self.trace_into.append("__str__")

        self.query_store = query_store
        if self.query_store is not None:
            if not os.path.isdir(self.query_store):
                raise IOError("Query folder {} not found".format(self.query_store))

        self.solver = Solver(query_store, solver_type, ss)
        global Target_line
        Target_line = target_line

    def extract(self):
        dis.dis(self.t_module)

    def add_constraint(self, constraint):
        self.new_constraints.append(constraint)

    # Legacy
    def get_members(self, target_module):
        for name, obj in inspect.getmembers(target_module):
            """
            if inspect.ismodule(obj):
                print("module", name)
                self.get_members(obj)
            """

            if inspect.isclass(obj):
                """
                print("class", name)
                for name_o, obj_o in inspect.getmembers(obj):
                    if inspect.isfunction(obj_o):
                        print( "function ", name_o)
                        #print_inst(obj_o)
                dis.dis(obj)
                """
            if inspect.ismethod(obj):
                """
                # print("method", name)
                #dis.dis(obj)
                # print_inst(obj)
                """
            if inspect.isfunction(obj):
                # dis.dis(obj)
                # print_inst(obj)
                self.trace_into.append(name)
                self.functions[name] = Function(obj)
                # print("function ", name)
                # dis.dis(obj)

    def execute_instructs(self, frame, func_name=None):
        # Handle previous jump first
        re = None
        while frame.next_offset != None:
            instruct = frame.get_instruct(frame.next_offset)

            if frame.instructions_store.contains(instruct):
                frame.next_offset = None
                log.debug("** Back to instructions queue")
                while instruct != frame.instructions_store.top():
                    frame.instructions_store.pop()
            else:
                log.debug("** Pure counter control")
                log.debug("- instr %s %s %s %s" % (instruct.offset, instruct.opname, instruct.argval, instruct.argrepr))
                re = self.executor.execute_instr(self.call_stack, instruct, func_name)
                if re:
                    return re

        while not frame.instructions_store.is_empty():
            frame.instructions.push(frame.instructions_store.pop())
        instructs = frame.instructions
        re = None

        while not instructs.is_empty():
            instruct = instructs.pop()
            log.debug("- instr %s %s %s %s" % (instruct.offset, instruct.opname, instruct.argval, instruct.argrepr))
            if instruct.opname == "CALL_FUNCTION":
                re = self.executor.execute_instr(self.call_stack, instruct, func_name)
                if re is None:
                    return
            elif instruct.opname == "CALL_METHOD":
                re = self.executor.execute_instr(self.call_stack, instruct, func_name)
                if re is None:
                    return
            else:
                re = self.executor.execute_instr(self.call_stack, instruct, func_name)
        return re

    def execute_frame(self, func_name=None):
        if self.call_stack.is_empty():
            return
        current_frame = self.call_stack.top()
        return self.execute_instructs(current_frame, func_name)


    def get_line_instructions(self, lineno, instructions):
        instructs = []
        start_record = False
        i = 0
        for instruct in instructions:
            if start_record:
                if instruct.starts_line == None:
                    instructs.append(instruct)
                else:
                    break
            else:
                if instruct.starts_line != None:
                    if instruct.starts_line == lineno:
                        start_record = True
                        instructs.append(instruct)
            i += 1
        return instructs

    def trace_lines(self, frame, event, arg):
        global Target_line
        if event != 'line':
            return

        co = frame.f_code
        func_name = co.co_name
        line_no = frame.f_lineno
        log.debug('+ %s line %s' % (func_name, line_no))
        if line_no == Target_line:
            print("<<<<<<<<<<<<<<<< MATCH RESULT BEGIN >>>>>>>>>>>>>>>>")
            print(str(frame.f_locals))
            print("<<<<<<<<<<<<<<<< MATCH RESULT END >>>>>>>>>>>>>>>>")
        instructions = self.get_line_instructions(line_no, dis.get_instructions(co))

        if self.call_stack.is_empty():
            return
        c_frame = self.call_stack.top()
        for instruct in instructions:
            c_frame.instructions_store.push(instruct)
            # print("   push", instruct.opname, instruct.argval, instruct.argrepr)

        is_return = self.execute_frame(func_name)

        while is_return:
            self.call_stack.pop()
            is_return = self.execute_frame(func_name)

    def trace_calls(self, frame, event, arg):
        if event != 'call':
            return
        co = frame.f_code
        func_name = co.co_name
        if "/python3." in co.co_filename :
            return
        current_frame = Frame(frame, self.mem_stack)
        if not self.call_stack.is_empty():
            if func_name == "__init__":
                current_frame.set_locals(self.call_stack.top().mem_stack, True)
            else:
                current_frame.set_locals(self.call_stack.top().mem_stack, False)
        else:
            self.symbolic_inputs = current_frame.init_locals()
            self.solver.set_variables(self.symbolic_inputs)
        # current_frame.set_local()
        self.call_stack.push(current_frame)
        return self.trace_lines

    def _is_exploration_complete(self):
        num_constr = self.constraints_to_solve.q_size()
        if num_constr == 0 and self.solved_constraints.is_empty():
            return True
        else:
            return False

    def explore(self, max_iterations, timeout=None):
        # First Execution
        self._one_execution(self.ini_vars)
        self.executor.extend_prune()
        iterations = 1

        # TODO: Currently single thread
        while not self._is_exploration_complete():
            if iterations >= max_iterations:
                break
                
            if not self.solved_constraints.is_empty():
                selected_id, result, model = self.solved_constraints.pop()

                if selected_id in self.finished_constraints:
                    continue

                selected_constraint = self.path.find_constraint(selected_id)
            else:
                cnt = 0
                while not self.constraints_to_solve.is_empty():
                    target, extend_var, extend_queries = self.constraints_to_solve.pop()
                    log.debug("Solving: %s" % target)
                    asserts, query = target.get_asserts_and_query()

                    ret, model = self.solver.find_counter_example(asserts, query, extend_var, extend_queries, timeout)

                    self.solved_constraints.push((target.id, ret, model))
                    # Every 4 solve check if any new inputs
                    cnt += 1
                    if cnt == 4:
                        break
                continue

            if model is not None:
                log.info("=== Iterations: %s ===" % iterations)
                iterations += 1
                args = self._recordInputs(model)
                try:
                    ret = func_timeout(5, self._one_execution, args=(args, selected_constraint))
                except FunctionTimedOut:
                    log.error("Execution Timeout: %s" % args)
                except Exception as e: 
                    log.error("Execution exception for: %s" % args)
                    traceback.print_exc()
                self.executor.extend_prune()
                if args not in self.input_sets:
                    self.error_sets.append(args)
                self.num_processed_constraints += 1
            self.finished_constraints.append(selected_id)
            break

        # self.execute_coverage()

    def _getInputs(self):
        return self.symbolic_inputs.copy()

    def _recordInputs(self, model):
        args = []
        for name, value in model.items():
            args.append(value)
        # args.reverse()
        return args


    def _one_execution(self, init_vars, expected_path=None):
        log.info("Inputs: " + str(init_vars))
        copy_vars = copy.deepcopy(init_vars)

        self.call_stack.sanitize()
        self.mem_stack.sanitize()
        self.path.reset(expected_path)

        execute = getattr(self.t_module, self.entry)
        sys.settrace(self.trace_calls)
        try:
            ret = execute(*copy_vars)
        except:
            ret = None
        finally:
            sys.settrace(None)
        log.info("Return: %s" % ret)
        while len(self.new_constraints) > 0:
            constraint = self.new_constraints.pop()
            constraint.inputs = self._getInputs()
            extend_var, extend_queries = self.executor.get_extend()
            self.constraints_to_solve.push((constraint, extend_var, extend_queries))

        self.input_sets.append(init_vars)
        self.in_ret_sets.append({"input": init_vars, "result": ret})


    def execute_coverage(self):
        execute = getattr(self.t_module, self.entry)
        cov = coverage.Coverage(branch=True)
        for args in self.input_sets:
            cov.start()
            copy_args = copy.deepcopy(args)
            ret = execute(*copy_args)
            cov.stop()
            self.global_execution_coverage.update(cov.get_data())


    def print_coverage(self):
        total_lines, executed_lines, missing_lines, executed_branches = self.coverage_statistics()
        print("Line coverage {}/{} ({:.2%})".format(executed_lines, total_lines, (executed_lines/total_lines) if total_lines > 0 else 0))
        print("Branch coverage {}".format(executed_branches))
        if len(missing_lines) > 0:
            print("Missing lines:")
            for file, lines in missing_lines.items():
                print("  {}: {}".format(file, lines))
        print("")

    def print_result(self):
        pass

    def coverage_statistics(self):
        cov = coverage.Coverage(branch=True)
        total_lines = 0
        executed_lines = 0
        executed_branches = 0
        missing_lines = {}
        for file in self.global_execution_coverage.measured_files():
            _, executable_lines, _, _ = cov.analysis(file)

            # total_lines -1 to discard the 'def xx():' line
            total_lines += (len(set(executable_lines)) - 1)
            executed_lines += len(set(self.global_execution_coverage.lines(file)))
            executed_branches += len(set(self.global_execution_coverage.arcs(file)))

            # executable_lines starting from 1 do discard the 'def xx():' line
            m_lines = []
            for line in set(executable_lines[1:]):
                if line not in self.global_execution_coverage.lines(file):
                    m_lines.append(line)
            if len(m_lines) > 0:
                missing_lines[file] = m_lines
        return total_lines, executed_lines, missing_lines, executed_branches

    def result_to_json(self):
        res = dict()
        res["inputs"] = self.input_sets
        res["error_inputs"] = self.error_sets
        total_lines, executed_lines, executed_branches = self.coverage_statistics()
        res["total_lines"] = total_lines
        res["executed_lines"] = executed_lines
        res["executed_branches"] = executed_branches

        return json.dumps(res)

