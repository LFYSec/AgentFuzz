from .utils import * 
from .concolic_types.concolic_type import * 
from .concolic_types.concolic_int import * 
from .concolic_types.concolic_str import * 
from .concolic_types.concolic_object import * 

import dis

log = logging.getLogger("ct.frame")

class Frame:
    def __init__(self, frame, mem_stack):
        log.debug("New Frame")
        """
        print("locals")
        for g_name in frame.f_locals:
            #print(g_name,":",frame.f_locals[g_name])
            print(" ", g_name)
        """
        self.frame = frame
        self.globals = frame.f_globals
        self.locals = frame.f_locals
        self.instructions = Queue()
        self.instructions_store = Queue()
        self.all_instructs = []
        self.variables = dict()
        self.g_variables = dict()
        self.mem_stack = mem_stack
        self.enter_object = None
        self.next_offset = None            # For JUMP

        for instruct in dis.get_instructions(frame.f_code):
            self.all_instructs.append(instruct)
        """
        print("global")
        for g_name in frame.f_globals:
            if "__doc__" in g_name:
                continue
            if "__builtins__" in g_name:
                continue
            print(g_name,":",frame.f_globals[g_name])
        print()
        print()
        """
    def init_locals(self):
        symbolic_inputs = dict()
        for local in self.locals:
            concolic_var = None
            if local != "self":
                local_value = self.locals[local]
                print(" local:", local, local_value)
                if isinstance(local_value, int):
                    concolic_var = ConcolicInteger(local, local_value)
                    symbolic_inputs[local] = "Int"
                elif isinstance(local_value, str):
                    concolic_var = ConcolicStr(local, local_value)
                    symbolic_inputs[local] = "String"
                elif isinstance(local_value, list):
                    concolic_var = ConcolicList()
                    symbolic_inputs[local] = "List"
                    index = 0
                    for element in local_value:
                        name = "_ARR_%d_%s" % (index, local)
                        if isinstance(element, int):
                            c_var = ConcolicInteger(name, element)
                            symbolic_inputs[name] = "Int"
                        elif isinstance(element, str):
                            c_var = ConcolicStr(name, element)
                            symbolic_inputs[name] = "String"
                        concolic_var.append(c_var)
                        index += 1
                if  not (concolic_var is None):
                    self.variables[local] = concolic_var

        self._set_globals()
        return symbolic_inputs

    def set_locals(self, mem_stack, is_init_object):
        for local in reversed(list(self.locals.keys())):
            log.debug("   local: %s" % local)
            if local != "self":
                var = mem_stack.pop()
                self.variables[local] = var
                log.debug("        : %s" % var)
            else:
                if is_init_object:
                    self.variables[local] = ConcolicObject()
                    log.debug("        : Init" )
                else:
                    var = mem_stack.pop()
                    self.variables[local] = var
                    log.debug("        : %s" % var)
        self._set_globals()

    def _set_globals(self):
        for name, val in self.globals.items():
            if name.startswith("__"):
                continue

            if isinstance(val, int):
                log.debug("   global: %s" % name)
                log.debug("         : %s" % name)
                self.g_variables[name] = ConcolicInteger(val, val)
            elif isinstance(val, str):
                log.debug("   global: %s" % name)
                log.debug("         : %s" % name)
                self.g_variables[name] = ConcolicStr('\"' + val + '\"')
            else:
                # log.debug("         : skip")
                continue
    
    def get_instruct(self, offset):
        for instruct in self.all_instructs:
            if instruct.offset == offset:
                return instruct
        return None
