from enum import StrEnum
from typing import Final

from psutil._pswindows import IOPriority


class IOPriorityStr(StrEnum):
    VERYLOW = 'VeryLow'
    LOW = 'Low'
    NORMAL = 'Normal'


to_iopriority: Final[dict[IOPriorityStr, IOPriority]] = {
    IOPriorityStr.VERYLOW: IOPriority.IOPRIO_VERYLOW,
    IOPriorityStr.LOW: IOPriority.IOPRIO_LOW,
    IOPriorityStr.NORMAL: IOPriority.IOPRIO_NORMAL,
    None: None
}
