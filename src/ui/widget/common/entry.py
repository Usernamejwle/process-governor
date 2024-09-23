from tkinter import END, Entry

from util.history import HistoryManager


class ExtendedEntry(Entry):
    def __init__(self, master=None, placeholder=None, color='grey', description=None, *args, **kwargs):
        super().__init__(
            master,
            *args,
            **kwargs
        )

        self._commit_history = True
        self.description = description
        self._setup_placeholder(color, placeholder)
        self._setup_history()

    def _setup_placeholder(self, color, placeholder):
        self._placeholder = placeholder

        if placeholder is not None:
            self._placeholder_color = color
            self._default_fg_color = self['fg']

            self.bind("<FocusIn>", self._focus_in, '+')
            self.bind("<FocusOut>", self._focus_out, '+')

            self._focus_out()

    def _setup_history(self):
        self.history = history = HistoryManager(self.get, self.set)

        # Doesn't work globally
        # self.bind("<<Redo>>", lambda _: history.redo() or print('redo'), '+')
        # self.bind("<<Undo>>", lambda _: history.undo() or print('undo'), '+')

        self.config(validate="key", validatecommand=(self.register(self._text_changed)))

    def _text_changed(self):
        if self._commit_history:
            self.history.commit()
        return True

    def _set_placeholder(self):
        self.set(self._placeholder)
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

    def set(self, value):
        try:
            self._commit_history = False
            self.delete(0, END)
            self.insert(0, value)
        finally:
            self._commit_history = True
