from tkinter import ttk, LEFT

from constants.ui import BUTTON_SIZE


class IconedButton(ttk.Button):
    def __init__(self, *args, image=None, compound=LEFT, width=BUTTON_SIZE, **kwargs):
        self._image = image
        super().__init__(*args, image=image, compound=compound, width=width, **kwargs)

    def config(self, *args, **kwargs):
        image = kwargs.get('image')

        if image is not None:
            self._image = image

        super().config(*args, **kwargs)

    configure = config
