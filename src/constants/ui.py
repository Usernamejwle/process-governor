from tkinter import LEFT, RIGHT
from typing import Final

UI_PADDING = 10
RC_WIN_SIZE = (1280, 768)

LEFT_PACK = dict(side=LEFT, padx=(0, UI_PADDING))
RIGHT_PACK = dict(side=RIGHT, padx=(UI_PADDING, 0))

COLUMN_TITLE_PADDING = 30
ERROR_ROW_COLOR = "#ffcdd2"
CHANGED_ROW_COLOR = "#b8e6bb"

SETTINGS_TITLE = "Settings"
OPEN_CONFIG_LABEL = "Open config file"
OPEN_LOG_LABEL = "Open log file"

CMENU_ADD_PROCESS_RULE_LABEL = " Add Process Rule"
CMENU_ADD_SERVICE_RULE_LABEL = " Add Service Rule"


class ActionEvents:
    ADD: Final[str] = "<<Add>>"
    DELETE: Final[str] = "<<Delete>>"
    UP: Final[str] = "<<Up>>"
    DOWN: Final[str] = "<<Down>>"
    CANCEL: Final[str] = "<<Cancel>>"
    APPLY: Final[str] = "<<Apply>>"
    APPLY_N_CLOSE: Final[str] = "<<ApplyAndClose>>"
    REFRESH: Final[str] = "<<Refresh>>"
    CONFIG: Final[str] = "<<Config>>"
    LOG: Final[str] = "<<LOG>>"
    FILTER_BY_TYPE: Final[str] = "<<FilterByType>>"
    SEARCH_CHANGE: Final[str] = "<<SearchChange>>"


class ExtendedTreeviewEvents:
    CHANGE: Final[str] = "<<Change>>"


class EditableTreeviewEvents:
    ESCAPE: Final[str] = "<<Escape>>"
    START_EDIT_CELL: Final[str] = "<<StartEditCell>>"
    SAVE_CELL: Final[str] = "<<SaveCell>>"


class ScrollableTreeviewEvents:
    SCROLL: Final[str] = "<<Scroll>>"
