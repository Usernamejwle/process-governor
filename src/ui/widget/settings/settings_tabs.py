from tkinter import ttk, messagebox
from typing import Optional

from pydantic.config import JsonDict

from constants.app_info import TITLE_ERROR
from constants.log import LOG
from constants.ui import ExtendedTreeviewEvents
from service.config_service import ConfigService
from ui.widget.settings.tabs.base_tab import BaseTab
from ui.widget.settings.tabs.processes.process_tab import ProcessesTab
from ui.widget.settings.tabs.rules.rules_tabs import ServiceRulesTab, ProcessRulesTab


class SettingsTabs(ttk.Notebook):
    _DEFAULT_TOOLTIP = (
        "To add a new rule, click the **Add** button.\n"
        "To edit a rule, **double-click** on the corresponding cell.\n"
        "Use the **context menu** for additional actions."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._config: Optional[JsonDict] = None
        self._create_tabs()

        self.bind(ExtendedTreeviewEvents.CHANGE, lambda _: self._update_tabs_state(), "+")

    def _create_tabs(self):
        self._process_rules_tab = ProcessRulesTab(self)
        self._service_rules_tab = ServiceRulesTab(self)
        self._process_list_tab = ProcessesTab(self)

        self._process_list_tab.place()
        self._process_rules_tab.place()
        self._service_rules_tab.place()

        self._update_tabs_state()

    def current_tab(self) -> BaseTab:
        current_index = self.index(self.select())
        tab_id = self.tabs()[current_index]
        return self.nametowidget(tab_id)

    def has_unsaved_changes(self) -> bool:
        for tab in self.frames():
            if tab.has_changes():
                return True
        return False

    def has_error(self) -> bool:
        for tab in self.frames():
            if tab.has_error():
                return True
        return False

    def load_data(self):
        self._config = ConfigService.load_config_raw()

        for tab in self.frames():
            tab.load_from_config(self._config)

    def save_data(self) -> bool:
        try:
            if not self.has_unsaved_changes() or self._config is None:
                return True

            if self.has_error():
                messagebox.showerror(
                    TITLE_ERROR,
                    "Unable to save: The current rules are invalid. "
                    "Ensure all rules are correct before saving."
                )
                return False

            for tab in self.frames():
                if not tab.has_changes():
                    continue

                tab.save_to_config(self._config)
                ConfigService.save_config_raw(self._config)
                tab.commit_changes()

            return True
        except:
            LOG.exception("An error occurred while saving.")
            messagebox.showerror(TITLE_ERROR, "An error occurred while saving.")
            return False

    def frames(self) -> list[BaseTab]:
        return [self.nametowidget(tab_id) for tab_id in self.tabs()]

    def frames_by_tab(self) -> dict[str, BaseTab]:
        return {
            tab_id: self.nametowidget(tab_id)
            for tab_id in self.tabs()
        }

    def get_default_tooltip(self):
        return self.current_tab().default_tooltip()

    def _update_tabs_state(self):
        tabs = self.frames_by_tab()

        for id, tab in tabs.items():
            star = "*" if tab.has_changes() or tab.has_error() else " "
            self.tab(id, text=f" {tab.title()} {star}")

    def next_tab(self):
        current_tab = self.index(self.select())
        next_tab = (current_tab + 1) % self.index("end")
        self.select(next_tab)

    def prev_tab(self):
        current_tab = self.index(self.select())
        next_tab = (current_tab - 1) % self.index("end")
        self.select(next_tab)
