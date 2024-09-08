from tkinter import ttk, LEFT, BOTH, RIGHT, Y

from constants.ui import ScrollableTreeviewEvents
from ui.widget.common.treeview.extended import ExtendedTreeview


class ScrollableTreeview(ExtendedTreeview):
    def __init__(self, master=None, *args, **kwargs):
        self._frame = ttk.Frame(master)
        self._scrollbar = ttk.Scrollbar(
            self._frame,
            orient="vertical",
            takefocus=0
        )

        super().__init__(self._frame, *args, **kwargs)

        self._scrollbar.configure(command=self._on_scrollbar)
        super().configure(yscrollcommand=self._on_scrollbar_mouse)

        self._scrollbar.pack(side=RIGHT, fill=Y)
        super().pack(fill=BOTH, expand=True, side=LEFT)

        self.bind("<<TreeviewSelect>>", self.__on_select, '+')

    def on_scroll(self):
        pass

    def _forward_geometry_options(self, method, *args, **kwargs):
        geometry_options = ['anchor', 'expand', 'fill', 'in_', 'ipadx', 'ipady', 'padx', 'pady', 'side']
        frame_kwargs = {key: value for key, value in kwargs.items() if key in geometry_options}
        other_kwargs = {key: value for key, value in kwargs.items() if key not in geometry_options}

        if frame_kwargs:
            getattr(self._frame, method)(*args, **frame_kwargs)

        if other_kwargs:
            getattr(super(ScrollableTreeview, self), method)(*args, **other_kwargs)

    def pack_configure(self, *args, **kwargs):
        return self._forward_geometry_options('pack_configure', *args, **kwargs)

    def pack_forget(self):
        self._frame.pack_forget()

    def pack_info(self):
        return self._frame.pack_info()

    def place_configure(self, *args, **kwargs):
        self._frame.place_configure(*args, **kwargs)

    def place_forget(self):
        self._frame.place_forget()

    def place_info(self):
        return self._frame.place_info()

    pack = pack_configure
    forget = pack_forget
    info = pack_info

    def _on_scrollbar(self, *args):
        self.yview(*args)
        self.event_generate(ScrollableTreeviewEvents.SCROLL)

    def _on_scrollbar_mouse(self, first, last):
        self._scrollbar.set(first, last)
        self.event_generate(ScrollableTreeviewEvents.SCROLL)

    def __on_select(self, _):
        for item in self.selection():
            self.see(item)
