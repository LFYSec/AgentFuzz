from types import FrameType
import builtins
import sys
import threading
import os
import subprocess
import inspect
import json
import threading
import time

original_os_system = os.system
original_subprocess_run = subprocess.run
original_eval = builtins.eval
# lock = threading.Lock()
oracle_file_name = ""
build_in_oracle_rules_set = set()
events_to_monitor = ["compile"]
other_oracle_rules_set = {}
last_compile_args = ""
is_startup = True
all_if_line_num = set()
all_other_oracle_line_num = set()

BUILDIN_PATH = []
current_path = sys.path[0]
for path in sys.path[1:]:
    if path not in current_path and current_path not in path:
        BUILDIN_PATH.append(path)


WHITE_LISTS = ["bisheng_langchain", "chatchat", "agentscope"]
CALLSTACK = set()
def is_builtin(frame: FrameType):
    func_name = frame.f_code.co_name
    func_filename = frame.f_code.co_filename
    if func_name in ["exec","eval"]:
        return False
    if func_filename.startswith("<"):
        return True
    if func_name.startswith("<"):
        return True
    
    global BUILDIN_PATH

    is_in_white_list = False
    for white_list in WHITE_LISTS:
        if white_list in func_filename:
            is_in_white_list = True
            break

    if not is_in_white_list:
        for path in BUILDIN_PATH:
            if func_filename.startswith(path):
                return True


    if func_name in dir(builtins):
        return True
    return False

def is_buildin_filename(filename: str):
    if filename.startswith("<"):
        return True
    return False

class Oracle():
    file_path:str
    sink:str
    line:int
    module_file_name:str
    def __init__(self,file_path,sink,line):
        self.file_path = file_path
        self.sink = sink
        self.line = int(line)
        self.module_file_name = file_path.split("/")[-1]

    def match(self, file_path:str, line:int):
        if int(line) != int(self.line):
            return False
        if not file_path.strip().endswith(self.module_file_name):
            return False
        return True

    def dump(self, expression):
        global oracle_file_name
        with open(oracle_file_name, "a+") as f:
            f.write(f"<=======================>\n")
            f.write(f"{str(expression)}\n")
            f.write(f"{self.sink}@{self.file_path}:{self.line}\n")

class HookIfRule():
    file_path:str
    module_name:str
    func_name:str
    expr: str
    start_line: int
    def __init__(self, file_path, module_name, func_name, expr, start_line):
        self.file_path = file_path
        self.module_name = module_name
        self.func_name = func_name
        self.expr = expr
        self.start_line = int(start_line)

    def match(self, file_path:str, func_name:str, line:int):
        if not int(line) == int(self.start_line):
            return False
        if not file_path.strip().endswith(self.module_name + ".py"):
            return False
        if not func_name == self.func_name and not self.func_name.endswith("." + func_name):
            return False
        return True
    
    def dump(self, local_vars):
        global hook_log
        with open(hook_log, "a+") as f:
            f.write(f"match: {self.file_path}:L{self.start_line}, {self.func_name}\n")
            f.write(f"{self.expr}\n")
            f.write(f"{str(local_vars)}\n")


class HookCallRule():
    package_name: str
    module_name: str
    func_name: str

    def __init__(self, package_name, module_name, func_name):
        self.package_name = package_name
        self.module_name = module_name
        self.func_name = func_name
    
    def match2(self, file_name: str, func_name: str) -> bool:
        if not file_name.endswith(self.module_name + ".py"):
            return False
        if func_name != self.func_name and not self.func_name.endswith("." + func_name):
            return False
        return True
    
    def dump(self, filename):
        with open(filename, "a+") as f:
            f.write(f"match: {self.package_name}/{self.module_name}.py:{self.func_name}\n")

def get_qualified_name_from_frame(frame: FrameType):
    return frame.f_code.co_name

def load_if_rules(rule_path: str):
    global all_if_line_num
    try:
        with open(rule_path, "r") as f:
            datas = json.load(f)
            rules = []
            data_set = set()
            for data in datas:
                for k in datas[data]:
                    if_content = str(k["file_path"]) + str(k["module_name"]) + str(k["func_name"]) + str(k["expr"]) + str(k["start_line"])
                    if if_content not in data_set:
                        data_set.add(if_content)
                        rules.append(HookIfRule(k["file_path"],k["module_name"], k["func_name"], k["expr"], k["start_line"]))
                        all_if_line_num.add(int(k["start_line"]))
            return rules
    except Exception as e:
        print(e)
        return []
    
def load_call_rules(rule_path: str):
    try:
        with open(rule_path, "r") as f:
            data = json.load(f)
            rules = []
            for k in data:
                rules.append(HookCallRule(k["package_name"], k["module_name"], k["func_name"]))
            return rules
    except Exception as e:
        print(e)
        return None

def load_oracle_rule(rule_path: str):
    global all_other_oracle_line_num
    build_in_oracle_rules_set = set()
    oracle = {}
    path_set = {}
    try:
        with open(rule_path, "r") as f:
            data = json.load(f)
            for k1 in data:
                for single_sink in data[k1]:
                    if single_sink["sink"] not in path_set:
                        path_set[single_sink["sink"]] = set()

                    if str(single_sink["file_path"]) + str(single_sink["sink"]) + str(single_sink["line"]) in path_set[single_sink["sink"]]:
                        continue
                    else:
                        path_set[single_sink["sink"]].add(str(single_sink["file_path"]) + str(single_sink["sink"]) + str(single_sink["line"]))


                    if single_sink["sink"] not in ["eval","exec"]:
                        if single_sink["sink"] not in oracle:
                            oracle[single_sink["sink"]] = set()
                        oracle[single_sink["sink"]].add(Oracle(single_sink["file_path"], single_sink["sink"], single_sink["line"]))
                        all_other_oracle_line_num.add(int(single_sink["line"]))

                    else:
                        build_in_oracle_rules_set.add(Oracle(single_sink["file_path"], single_sink["sink"], single_sink["line"]))
                        

            return build_in_oracle_rules_set, oracle
    except Exception as e:
        print(e)
        return build_in_oracle_rules_set, oracle


def enter_frame(frame:FrameType):
    global enter_rules
    global match_log_file
    global call_stack_log_file
    global CALLSTACK

    if enter_rules:
        func_filename = frame.f_code.co_filename
        qual_func_name = ""
        if sys.version_info >= (3, 11):
            qual_func_name = frame.f_code.co_qualname
        else:
            qual_func_name = get_qualified_name_from_frame(frame)

        for rule in enter_rules:
            if rule.match2(func_filename, qual_func_name):
                rule.dump(match_log_file)
        if not os.path.exists(call_stack_log_file):
            CALLSTACK = set()
        
        if qual_func_name not in CALLSTACK:
            CALLSTACK.add(qual_func_name)
            with open(call_stack_log_file, 'a+') as f:
                f.write(f"{qual_func_name} \n")

def line_frame(frame:FrameType):
    global rules
    global other_oracle_rules_set
    global all_if_line_num
    global all_other_oracle_line_num

    # for if condition
    if int(frame.f_lineno) in all_if_line_num:
        for rule in rules:
            if rule.match(frame.f_code.co_filename, get_qualified_name_from_frame(frame), frame.f_lineno):
                rule.dump(str(frame.f_locals))


    # for oracle
    if int(frame.f_lineno) in all_other_oracle_line_num:
        for event in other_oracle_rules_set:
            for rule in other_oracle_rules_set[event]:
                if rule.match(frame.f_code.co_filename, frame.f_lineno):
                    rule.dump(str(frame.f_locals))



def leave_frame(frame:FrameType):
    pass



def real_start_trace(on_call, on_line, on_return):
    """wraper for real trace function"""
    def real_trace(frame, event, arg):

        if is_builtin(frame):
            return real_trace

        if event == 'call':
            on_call(frame)
        if event == 'return':
            on_return(frame)
        if event == 'line':
            on_line(frame)

        return real_trace

    sys.settrace(real_trace)
    threading.settrace(real_trace)
    print("set ce trace ok")


def audit_hook(event, args):
    global events_to_monitor
    global build_in_oracle_rules_set
    global is_startup
    if not is_startup and event in events_to_monitor:
        if not is_buildin_filename(inspect.stack()[1].filename):
            is_match = False
            for stack in inspect.stack()[::-1]:
                for oracle in build_in_oracle_rules_set:
                    if oracle.match(stack.filename, stack.lineno):
                        oracle.dump(str(args[0]))
                        is_match = True
                        break
                if is_match:
                    break


def hooked_os_system(command):
    global other_oracle_rules_set
    if "system" not in other_oracle_rules_set:
        return original_os_system(command)
    if is_buildin_filename(inspect.stack()[1].filename):
        return original_os_system(command)
    for oracle in other_oracle_rules_set["system"]:
        for stack in inspect.stack()[::-1]:
            if oracle.match(stack.filename, stack.lineno):
                oracle.dump(command)
                break
    return original_os_system(command)


def hooked_subprocess_run(*args, **kwargs):
    global other_oracle_rules_set
    if "run" not in other_oracle_rules_set:
        return original_subprocess_run(*args, **kwargs)
    if is_buildin_filename(inspect.stack()[1].filename):
        return original_subprocess_run(*args, **kwargs)
    for oracle in other_oracle_rules_set["run"]:
        for stack in inspect.stack()[::-1]:
            if oracle.match(stack.filename, stack.lineno):
                oracle.dump(args)
                break
    return original_subprocess_run(*args, **kwargs)

def hooked_eval(expression, *args, **kwargs):
    global build_in_oracle_rules_set
    if (not isinstance(expression, str)) or (str(expression).startswith("<code object")) or (str(expression).startswith("lambda _cls")):
        return original_eval(expression, *args, **kwargs)
    if not is_buildin_filename(inspect.stack()[1].filename):
        is_match = False
        for stack in inspect.stack()[::]:
            for oracle in build_in_oracle_rules_set:
                if oracle.match(stack.filename, stack.lineno):
                    oracle.dump("b'" + expression + "'")
                    is_match = True
                    break
            if is_match:
                break
    return original_eval(expression, *args, **kwargs)


def do_hook():
    subprocess.run = hooked_subprocess_run




def update_global_variable():
    global is_startup
    time.sleep(40)  
    is_startup = False


def start_ce_trace(conf="if.json", enter_input_conf="enter_hook.json", oracle_rule_conf = "oracle.json", log="/tmp/if.log", match_log = "/tmp/hook.log", call_stack_log = "/tmp/callstack.log", oracle_name = "/tmp/oracle.log"):
    global rule_path
    global rules
    global hook_log
    global enter_rules
    global enter_conf
    global match_log_file
    global call_stack_log_file
    global oracle_file_name
    global other_oracle_rules_set
    global build_in_oracle_rules_set
    oracle_file_name = oracle_name

    rule_path = conf
    hook_log = log
    rules = load_if_rules(rule_path)
    print(f"{len(rules)} rules")


    enter_conf = enter_input_conf
    enter_rules = load_call_rules(enter_conf)
    print(f"{len(enter_rules)} rules")


    build_in_oracle_rules_set, other_oracle_rules_set = load_oracle_rule(oracle_rule_conf)

    match_log_file = match_log
    call_stack_log_file = call_stack_log
    thread = threading.Thread(target=update_global_variable)
    thread.start()
    sys.addaudithook(audit_hook)
    do_hook()
    real_start_trace(enter_frame, line_frame, leave_frame)

rule_path = "if.json"
hook_log = "/tmp/if.log"