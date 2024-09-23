from tkinter import ttk, DISABLED

from constants.resources import UI_CONFIG, UI_LOG, UI_SAVE
from constants.ui import OPEN_CONFIG_LABEL, ActionEvents, OPEN_LOG_LABEL, LEFT_PACK, RIGHT_PACK
from ui.widget.common.button import ExtendedButton
from util.ui import load_img


class SettingsActions(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup_btn()

    def _setup_btn(self):
        self.open_config = open_config = ExtendedButton(
            self,
            text=f"{OPEN_CONFIG_LABEL}",
            event=ActionEvents.CONFIG,
            image=load_img(file=UI_CONFIG),
            description="**Opens** the __config file__."
        )

        self.open_log = open_log = ExtendedButton(
            self,
            text=f"{OPEN_LOG_LABEL}",
            event=ActionEvents.LOG,
            image=load_img(file=UI_LOG),
            description="**Opens** the __log file__."
        )

        self.save = save = ExtendedButton(
            self,
            text="Save",
            state=DISABLED,
            event=ActionEvents.SAVE,
            image=load_img(file=UI_SAVE),
            description="**Saves** the __settings__. \n**Hotkey:** __Ctrl+S__."
        )

        open_config.pack(**LEFT_PACK)
        open_log.pack(**LEFT_PACK)
        save.pack(**RIGHT_PACK)
