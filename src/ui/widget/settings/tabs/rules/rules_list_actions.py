from tkinter import ttk

from constants.resources import UI_ADD, UI_DELETE, UI_UP, UI_DOWN
from constants.ui import ActionEvents, LEFT_PACK
from ui.widget.common.button import ExtendedButton
from util.ui import load_img


class RulesListActions(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup_btn()

    def _setup_btn(self):
        self.add = add = ExtendedButton(
            self,
            text="Add",
            event=ActionEvents.ADD,
            image=load_img(file=UI_ADD),
            description="**Adds** a rule before the current. \n**Hotkey:** __Ctrl+D__."
        )

        self.delete = delete = ExtendedButton(
            self,
            text="Del",
            event=ActionEvents.DELETE,
            image=load_img(file=UI_DELETE),
            description="**Deletes** the selected rules. \n**Hotkey:** __Del__."
        )

        self.move_up = move_up = ExtendedButton(
            self,
            text="Up",
            event=ActionEvents.UP,
            image=load_img(file=UI_UP),
            description="**Moves** the current rule __up__."
        )

        self.move_down = move_down = ExtendedButton(
            self,
            text="Down",
            event=ActionEvents.DOWN,
            image=load_img(file=UI_DOWN),
            description="**Moves** the current rule __down__."
        )

        add.pack(**LEFT_PACK)
        delete.pack(**LEFT_PACK)
        move_up.pack(**LEFT_PACK)
        move_down.pack(**LEFT_PACK)
