import dis

class Function:
    def __init__(self, obj):
        self.obj = obj
        self.name = obj.__name__
        self.instructions = []
        for instruct in dis.get_instructions(obj):
            self.instructions.append(instruct)

    def get_instruct_by_line(self, line_no: int):
        instructs = []
        start_record = False
        i = 0
        while i < len(self.instructions):
            instruct = self.instructions[i]
            if start_record:
                if instruct.starts_line == None:
                    instructs.append(instruct)
                else:
                    break
            else:
                if instruct.starts_line != None:
                    if instruct.starts_line == line_no:
                        start_record = True
                        instructs.append(self.instructions[i])
            i += 1
        return instructs

