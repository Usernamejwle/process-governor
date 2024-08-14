from enum import Enum
from typing import Final

from psutil._pswindows import IOPriority


class IOPriorityStr(str, Enum):
    VERYLOW = 'VeryLow'
    LOW = 'Low'
    NORMAL = 'Normal'
    HIGH = 'High'

    def __str__(self):
        return str(self.value)


to_iopriority: Final[dict[IOPriorityStr, IOPriority]] = {
    IOPriorityStr.VERYLOW: IOPriority.IOPRIO_VERYLOW,
    IOPriorityStr.LOW: IOPriority.IOPRIO_LOW,
    IOPriorityStr.NORMAL: IOPriority.IOPRIO_NORMAL,
    IOPriorityStr.HIGH: IOPriority.IOPRIO_HIGH,
    None: None
}
