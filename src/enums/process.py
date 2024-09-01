from enum import StrEnum


class ProcessParameter(StrEnum):
    AFFINITY = "affinity"
    NICE = "priority"
    IONICE = "I/O priority"
