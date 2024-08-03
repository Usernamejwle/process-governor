from typing import Final

UI_PADDING = 10
BUTTON_SIZE = 7
ERROR_COLOR = "#e57373"
ERROR_ROW_COLOR = "#ffcdd2"
TOOLTIP_ICON_SIZE = 75
RC_WIN_SIZE = (900, 600)
RC_TITLE = "Rules Configurator"


class ActionEvents:
    ADD: Final[str] = "<<Add>>"
    DELETE: Final[str] = "<<Delete>>"
    UP: Final[str] = "<<Up>>"
    DOWN: Final[str] = "<<Down>>"
    CANCEL: Final[str] = "<<Cancel>>"
    SAVE: Final[str] = "<<Save>>"


class RulesListEvents:
    UNSAVED_CHANGES_STATE: Final[str] = "<<UnsavedChangesState>>"


class EditableTreeviewEvents:
    CHANGE: Final[str] = "<<Change>>"
    ESCAPE: Final[str] = "<<Escape>>"
    START_EDIT_CELL: Final[str] = "<<StartEditCell>>"
    SAVE_CELL: Final[str] = "<<SaveCell>>"


class ScrollableTreeviewEvents:
    SCROLL: Final[str] = "<<Scroll>>"
