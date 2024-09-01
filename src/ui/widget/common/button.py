from tkinter import ttk, LEFT, PhotoImage
from typing import Optional

from constants.ui import UI_PADDING
from util.ui import get_button_font, single_font_width


class ExtendedButton(ttk.Button):

    def __init__(
            self,
            master,
            *args,
            event: str,
            text: Optional[str] = None,
            width: Optional[int] = None,
            image=None,
            description=None,
            compound=None,
            **kwargs
    ):
        self._font = get_button_font()
        self.description = description

        if compound is None:
            compound = LEFT if text else None

        super().__init__(
            master,
            *args,
            text=f" {text}" if image and text else text,
            command=lambda: master.event_generate(event),
            image=image,
            compound=compound,
            width=self._calc_width(text, image, width),
            **kwargs
        )

    def _calc_width(self, text: Optional[str], image: Optional[PhotoImage], width: Optional[int]) -> Optional[int]:
        if width:
            return width

        width_image = getattr(image, 'width', lambda: 0)()

        if not text:
            return None

        return int((self._font.measure(text) + width_image + UI_PADDING) / single_font_width()) + 1
