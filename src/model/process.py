from typing import Optional

import psutil
from psutil._pswindows import Priority, IOPriority
from pydantic import BaseModel, Field, ConfigDict

from model.service import Service


class Process(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)

    """
    The Process class represents information about a running process.

    It includes attributes such as process ID (pid), executable name (exe), process name (name), priority (nice), I/O priority
    (ionice), CPU core affinity, and the associated psutil.Process object.
    """

    pid: int = Field(
        title="PID",
        description="The unique identifier of the __process__ (**Process ID**).",
        default_sort_column_ui=True,
        width_ui=75
    )

    process_name: Optional[str] = Field(
        title="Process Name",
        description="The **name** of the __process__.",
        justify_ui="left",
        width_ui=200
    )

    service_name: Optional[str] = Field(
        title="Service Name",
        description="The **name** of the __service__ associated with this __process__.\n"
                    "This field may be absent if the process is not a service.",
        justify_ui="left",
        width_ui=250
    )

    bin_path: Optional[str] = Field(
        title="Executable Path",
        description="The **full path** to the executable binary of the __process__.",
        stretchable_column_ui=True,
        justify_ui="left"
    )

    cmd_line: Optional[str] = Field(
        title="Command Line",
        description="The **command line** used to start the __process__, including all arguments.",
        stretchable_column_ui=True,
        justify_ui="left"
    )

    priority: Optional[Priority] = Field(
        title="Priority",
        description="The **priority level** of the __process__.",
        exclude=True
    )

    io_priority: Optional[IOPriority] = Field(
        title="I/O Priority",
        description="The **I/O priority** of the __process__.",
        exclude=True
    )

    affinity: Optional[list[int]] = Field(
        title="CPU Core Affinity",
        description="A list of integers representing the CPU cores to which the __process__ is bound (**CPU core affinity**).",
        exclude=True
    )

    process: psutil.Process = Field(
        description="The psutil.Process object associated with the __process__, providing access to additional control.",
        exclude=True
    )

    service: Optional[Service] = Field(
        description="Contains information about the service if the current __process__ is associated with one.\n"
                    "If the __process__ is not related to a service, this will be None.",
        exclude=True
    )

    def __hash__(self):
        return hash((self.pid, self.bin_path, self.process_name, self.cmd_line))

    def __eq__(self, other):
        if isinstance(other, Process):
            return ((self.pid, self.bin_path, self.process_name, self.cmd_line) ==
                    (other.pid, other.bin_path, other.process_name, other.cmd_line))
        return False
