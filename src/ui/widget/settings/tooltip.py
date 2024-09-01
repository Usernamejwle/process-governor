from tkinter import ttk, StringVar, LEFT, Y, BOTH

from constants.resources import UI_INFO_TOOLTIP, UI_WARN_TOOLTIP
from constants.ui import UI_PADDING
from ui.widget.common.label import RichLabel, Image
from util.ui import load_img


class Tooltip(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        text = kwargs.pop("text", "")

        super().__init__(master, *args, **kwargs)
        self._text = StringVar(self, value=text)

        self._image = Image(
            self,
            image=load_img(file=UI_INFO_TOOLTIP)
        )
        self._image.pack(side=LEFT, fill=Y, padx=(0, UI_PADDING))

        label = RichLabel(self, height=5.25, textvariable=self._text)
        label.pack(expand=True, fill=BOTH)
        label.pack_propagate(False)

    def set(self, text: str, error: bool = False):
        if error:
            self._image.configure(image=load_img(file=UI_WARN_TOOLTIP))
        else:
            self._image.configure(image=load_img(file=UI_INFO_TOOLTIP))
        self._text.set(text)
