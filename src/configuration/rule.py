from typing import Optional

from pydantic import BaseModel, Field

from configuration.handler.affinity import Affinity
from enums.bool import BoolStr
from enums.io_priority import IOPriorityStr
from enums.priority import PriorityStr
from enums.selector import SelectorType


class ProcessRule(BaseModel):
    selectorBy: SelectorType = Field(
        default=SelectorType.NAME,
        title="Selector By",
        description="Determines how the __Process Selector__ value is interpreted, influencing how the __process__ is matched.\n"
                    "**Options:**\n"
                    "- `Name` - matches by process name (e.g., `notepad.exe`);\n"
                    "- `Path` - matches by the full executable path (e.g., `C:/Windows/System32/notepad.exe`);\n"
                    "- `Command line` - matches by command line arguments (e.g., `App.exe Document.txt` or `D:/Folder/App.exe Document.txt`)."
    )

    selector: str = Field(
        title="Process Selector",
        description="Specifies the **name**, **pattern** or **path** of the __process__ to which this rule applies.\n\n"
                    "**Supports wildcard:** `*` (matches any characters), `?` (matches any single character) and `**` (matches any sequence of directories).\n"
                    "**Examples:** `name.exe`, `logioptionsplus_*.exe`, `D:/FolderName/App.exe` or `C:/Program Files/**/app.exe --file Document.txt`.",
        stretchable_column_ui=True,
        justify_ui="left"
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
        description="Sets the **CPU core affinity** for the __process__, defining which CPU cores are allowed for execution.\n\n"
                    "**Format:** range `0-3`, specific cores `0;2;4`, combination `1;3-5`.",
        justify_ui="left",
        width_ui=200
    )

    force: BoolStr = Field(
        default=BoolStr.NO,
        title="Force",
        description="**Forces** the settings to be continuously applied to the __process__, even if the application tries to override them.\n\n"
                    "**Possible values:**\n"
                    "- `Y` for continuous application;\n"
                    "- `N` for one-time application.",
    )

    delay: Optional[int] = Field(
        gt=0,
        default=0,
        title="Delay",
        description="Specifies the **delay** in __seconds__ before the settings are applied to the __process__.\n\n"
                    "**Possible values:**\n"
                    "- If not specified, the settings are applied immediately;\n"
                    "- Positive values set a delay in seconds before applying the settings."
    )


class ServiceRule(BaseModel):
    selector: str = Field(
        title="Service Selector",
        description="Specifies the **name** of the __service__ to which this rule applies.\n\n"
                    "**Supports wildcard:** `*` (matches any characters) and `?` (matches any single character)\n"
                    "**Examples:** `ServiceName` or `Audio*`.",
        stretchable_column_ui=True,
        justify_ui="left"
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
        description="Sets the **CPU core affinity** for the __service__, defining which CPU cores are allowed for execution.\n\n"
                    "**Format:** range `0-3`, specific cores `0;2;4`, combination `1;3-5`.",
        justify_ui="left",
        width_ui=200
    )

    force: BoolStr = Field(
        default=BoolStr.NO,
        title="Force",
        description="**Forces** the settings to be continuously applied to the __service__, even if the application tries to override them.\n\n"
                    "**Possible values:**\n"
                    "- `Y` for continuous application;\n"
                    "- `N` for one-time application.",
    )

    delay: Optional[int] = Field(
        gt=0,
        default=0,
        title="Delay",
        description="Specifies the **delay** in __seconds__ before the settings are applied to the __service__.\n\n"
                    "**Possible values:**\n"
                    "- If not specified, the settings are applied immediately;\n"
                    "- Positive values set a delay in seconds before applying the settings."
    )
