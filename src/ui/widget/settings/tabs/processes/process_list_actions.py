from tkinter import ttk

from constants.resources import UI_REFRESH
from constants.ui import ActionEvents, LEFT_PACK
from enums.filters import FilterByProcessType
from ui.widget.common.button import ExtendedButton
from ui.widget.common.combobox import EnumCombobox
from ui.widget.common.entry import ExtendedEntry
from util.ui import load_img


class ProcessListActions(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._search_delay_timer = None
        self._setup_btn()

    def _setup_btn(self):
        self.refresh = refresh = ExtendedButton(
            self,
            text="Refresh",
            event=ActionEvents.REFRESH,
            image=load_img(file=UI_REFRESH),
            description="**Refreshes** the list of __processes__.\n**Hotkey:** __F5__."
        )

        self.filterByType = filterByType = EnumCombobox(
            self,
            FilterByProcessType,
            description="**Filters** processes by __type__.",
            state="readonly"
        )

        self.search = search = ExtendedEntry(
            self,
            description="**Searches** processes by __name__ or __attribute__.\n**Hotkey:** __Ctrl+F__.",
            placeholder="Search",
            width=30
        )

        search.bind('<KeyRelease>', self._on_search_key_release, '+')

        filterByType.set(FilterByProcessType.ALL)
        filterByType.bind('<<ComboboxSelected>>', lambda _: self.event_generate(ActionEvents.FILTER_BY_TYPE), '+')

        search.pack(**LEFT_PACK)
        filterByType.pack(**LEFT_PACK)
        refresh.pack(**LEFT_PACK)

    def _on_search_key_release(self, _):
        if self._search_delay_timer:
            self.after_cancel(self._search_delay_timer)

        self._search_delay_timer = self.after(125, self._trigger_search_change_event)

    def _trigger_search_change_event(self):
        self.event_generate(ActionEvents.SEARCH_CHANGE)
        self._search_delay_timer = None
