from enum import Enum


class ProcessParameter(str, Enum):
    AFFINITY = "affinity"
    NICE = "priority"
    IONICE = "I/O priority"

    def __str__(self):
        return str(self.value)
