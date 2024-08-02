from typing import Optional

from pydantic import BaseModel, Field

from configuration.handler.affinity import Affinity
from configuration.handler.io_priority import IOPriorityStr
from configuration.handler.priority import PriorityStr


class ProcessRule(BaseModel):
    selector: str = Field(
        title="Process Selector",
        description="Specifies the __name or pattern__ of the __process__ to which this rule applies.\n\n"
                    "**Supports wildcards:** `\*` (matches any characters) and `?` (matches any single character).\n"
                    "**Examples:** `name.exe` or `logioptionsplus_*.exe`.",
        default_ui="*",
        stretchable_column_ui=True
    )

    priority: Optional[PriorityStr] = Field(
        default=None,
        title="Priority",
        description="Sets the **priority level** for the __process__.\n"
                    "Higher priority tasks are allocated more CPU time compared to lower priority tasks."
    )

    ioPriority: Optional[IOPriorityStr] = Field(
        default=None,
        title="I/O Priority",
        description="Sets the **I/O priority** for the __process__.\n"
                    "Higher I/O priority means more disk resources and better I/O performance."
    )

    affinity: Optional[Affinity] = Field(
        default=None,
        title="Affinity",
        description="Sets the **CPU core affinity** for the __process__, "
                    "defining which CPU cores are allowed for execution.\n\n"
                    "**Format:** range `0-3`, specific cores `0;2;4`, combination `1;3-5`.",
        scale_width_ui=3
    )


class ServiceRule(BaseModel):
    selector: str = Field(
        title="Service Selector",
        description="Specifies the __name or pattern__ of the __service__ to which this rule applies.\n\n"
                    "**Supports wildcards:** `\*` (matches any characters) and `?` (matches any single character).\n"
                    "**Examples:** `ServiceName` or `Audio*`.",
        default_ui="*",
        stretchable_column_ui=True
    )

    priority: Optional[PriorityStr] = Field(
        default=None,
        title="Priority",
        description="Sets the **priority level** for the __service__.\n"
                    "Higher priority tasks are allocated more CPU time compared to lower priority tasks."
    )

    ioPriority: Optional[IOPriorityStr] = Field(
        default=None,
        title="I/O Priority",
        description="Sets the **I/O priority** for the __service__.\n"
                    "Higher I/O priority means more disk resources and better I/O performance."
    )

    affinity: Optional[Affinity] = Field(
        default=None,
        title="Affinity",
        description="Sets the **CPU core affinity** for the __service__, "
                    "defining which CPU cores are allowed for execution.\n\n"
                    "**Format:** range `0-3`, specific cores `0;2;4`, combination `1;3-5`.",
        scale_width_ui=3
    )
