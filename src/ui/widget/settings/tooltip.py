import tkinter as tk
from tkinter import ttk, StringVar, PhotoImage

from constants.resources import UI_INFO_TOOLTIP, UI_WARN_TOOLTIP
from constants.ui import UI_PADDING
from ui.widget.common.label import RichLabel, Image


class Tooltip(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        text = kwargs.pop("text", "")

        super().__init__(master, *args, **kwargs)
        self._text = StringVar(self, value=text)
        self._info_icon = PhotoImage(file=UI_INFO_TOOLTIP)
        self._error_icon = PhotoImage(file=UI_WARN_TOOLTIP)

        self._image = Image(
            self,
            image=self._info_icon
        )
        self._image.pack(side=tk.LEFT, fill=tk.Y, padx=(0, UI_PADDING))

        label = RichLabel(self, height=5.25, textvariable=self._text)
        label.pack(expand=True, fill=tk.BOTH)
        label.pack_propagate(False)

    def set(self, text: str, error: bool = False):
        if error:
            self._image.configure(image=self._error_icon)
        else:
            self._image.configure(image=self._info_icon)
        self._text.set(text)
