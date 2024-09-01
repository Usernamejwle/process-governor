from tkinter import END, Entry


class ExtendedEntry(Entry):
    def __init__(self, master=None, placeholder=None, color='grey', description=None, *args, **kwargs):
        super().__init__(
            master,
            *args,
            **kwargs
        )

        self.description = description
        self._placeholder = placeholder

        if placeholder is not None:
            self._placeholder_color = color
            self._default_fg_color = self['fg']

            self.bind("<FocusIn>", self._focus_in, '+')
            self.bind("<FocusOut>", self._focus_out, '+')

            self._focus_out()

    def _set_placeholder(self):
        self.insert(0, self._placeholder)
        self['fg'] = self._placeholder_color

    def _focus_in(self, *args):
        if super().get() == self._placeholder:
            self.delete(0, END)
            self['fg'] = self._default_fg_color

    def _focus_out(self, *args):
        if not self.get():
            self._set_placeholder()

    def get(self):
        current_text = super().get()

        if self._placeholder is not None and current_text == self._placeholder:
            return ""
        else:
            return current_text
