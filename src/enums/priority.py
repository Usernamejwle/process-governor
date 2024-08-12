from enum import Enum
from typing import Final

from psutil._pswindows import Priority


class PriorityStr(Enum):
    IDLE = 'Idle'
    BELOW_NORMAL = 'BelowNormal'
    NORMAL = 'Normal'
    ABOVE_NORMAL = 'AboveNormal'
    HIGH = 'High'
    REALTIME = 'Realtime'


to_priority: Final[dict[PriorityStr, Priority]] = {
    PriorityStr.IDLE: Priority.IDLE_PRIORITY_CLASS,
    PriorityStr.BELOW_NORMAL: Priority.BELOW_NORMAL_PRIORITY_CLASS,
    PriorityStr.NORMAL: Priority.NORMAL_PRIORITY_CLASS,
    PriorityStr.ABOVE_NORMAL: Priority.ABOVE_NORMAL_PRIORITY_CLASS,
    PriorityStr.HIGH: Priority.HIGH_PRIORITY_CLASS,
    PriorityStr.REALTIME: Priority.REALTIME_PRIORITY_CLASS,
    None: None
}
