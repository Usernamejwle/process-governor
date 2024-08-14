from enum import Enum


class SelectorType(str, Enum):
    NAME = "Name"
    PATH = "Path"
    CMDLINE = "CommandLine"

    def __str__(self):
        return str(self.value)
