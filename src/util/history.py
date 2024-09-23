class HistoryManager:
    def __init__(self, getter, setter, max_depth=20):
        self.getter = getter
        self.setter = setter
        self.history = []
        self.redo_stack = []
        self.max_depth = max_depth
        self.commit()

    def commit(self):
        self.add(self.getter())

    def undo(self):
        if len(self.history) > 0:
            self.redo_stack.append(self.getter())
            self.setter(self.history.pop())

    def redo(self):
        if self.redo_stack:
            self.history.append(self.getter())
            self.setter(self.redo_stack.pop())

    def clear(self):
        self.history.clear()
        self.redo_stack.clear()

    def add(self, value):
        if not self.history or self.history[-1] != value:
            if len(self.history) >= self.max_depth:
                self.history.pop(0)
            self.history.append(value)
            self.redo_stack.clear()
