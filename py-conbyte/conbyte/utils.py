
class Stack:
    def __init__(self):
        self.stack = []

    def pop(self):
        return self.stack.pop(0)
    
    def push(self, item):
        self.stack.insert(0, item)

    def top(self):
        if len(self.stack) == 0:
            return None
        return self.stack[0]

    def s_size(self):
        return len(self.queue)

    def is_empty(self):
        if len(self.stack) != 0:
            return False
        else:
            return True

    def sanitize(self):
        while not self.is_empty():
            self.pop()

    def contains(self, target):
        if target in self.stack:
            return True
        else:
            return False

    def __str__(self):
        if len(self.stack) == 0:
            return "  Stack: nil"
        return "  Stack: %s" % ",".join(val.__str__() for val in self.stack)


class Queue:
    def __init__(self):
        self.queue = []

    def head(self):
        return self.queue[0]

    def pop(self):
        return self.queue.pop(0)

    def push(self, item):
        self.queue.append(item)

    def q_size(self):
        return len(self.queue)

    def is_empty(self):
        if len(self.queue) != 0:
            return False
        else:
            return True

    def top(self):
        if len(self.queue) == 0:
            return None
        return self.queue[0]

    def sanitize(self):
        while not self.is_empty():
            self.pop()

    def contains(self, target):
        if target in self.queue:
            return True
        else:
            return False

    def __str__(self):
        if len(self.queue) == 0:
            return "  Queue: nil"
        return "  Queue: %s" % ",".join(val.__str__() for val in self.queue)
