from enum import Enum
from tkinter import ttk, Tk
from typing import Optional

from util.ui import get_default_font, single_font_width
from util.utils import extract_type, get_values_from_enum


class EnumCombobox(ttk.Combobox):
    def __init__(
            self,
            master,
            annotation: type[Enum] | Optional[type[Enum]],
            description=None,
            auto_width=True,
            *args,
            **kwargs
    ):
        self.description = description
        self._font = get_default_font() if auto_width else None
        self._enum_type = extract_type(annotation)
        self._values = get_values_from_enum(annotation)

        super().__init__(
            master,
            values=self._values,
            width=self._calculate_max_width() if auto_width else None,
            *args,
            **kwargs
        )

    def get_enum_value(self) -> Optional[Enum]:
        selected_value = self.get()

        if selected_value:
            return self._enum_type(selected_value)

        return None

    def _calculate_max_width(self):
        return max(map(self._font.measure, self._values)) // single_font_width() + 1


if __name__ == "__main__":
    # Пример использования

    class MyEnum(str, Enum):
        OPTION1 = "Option 1"
        OPTION2 = "Option 2"
        OPTION3 = "Option 3"


    root = Tk()

    combobox = EnumCombobox(root, MyEnum, state="readonly")
    combobox.pack(padx=10, pady=10)


    def on_select(event):
        enum_value = combobox.get_enum_value()
        print(f"Selected Enum: {enum_value}")


    combobox.bind("<<ComboboxSelected>>", on_select, '+')

    root.mainloop()
