from enum import Enum


class BoolStr(str, Enum):
    NO = "N"
    YES = "Y"

    def __str__(self):
        return str(self.value)