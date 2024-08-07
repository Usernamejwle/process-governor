from tkinter import ttk, messagebox
from typing import Optional

from constants.app_info import APP_NAME_WITH_VERSION
from constants.log import LOG
from service.config_service import ConfigService
from ui.widget.settings.tabs.rules.base_rules_tab import BaseRulesTab
from ui.widget.settings.tabs.rules.rules_tab import ServiceRulesTab, ProcessRulesTab


class SettingsTabs(ttk.Notebook):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._config: Optional[dict] = None
        self._create_tabs()

    def _create_tabs(self):
        ProcessRulesTab(self)
        ServiceRulesTab(self)

    def current_tab(self) -> BaseRulesTab:
        current_index = self.index(self.select())
        tab_id = self.tabs()[current_index]
        return self.nametowidget(tab_id)

    def has_unsaved_changes(self) -> bool:
        for tab in self.frames():
            if tab.has_unsaved_changes():
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
                    f"Error Detected - {APP_NAME_WITH_VERSION}",
                    "Unable to save: The current rules are invalid. "
                    "Ensure all rules are correct before saving."
                )
                return False

            for tab in self.frames():
                tab.save_to_config(self._config)

            ConfigService.save_config_raw(self._config)
            return True
        except:
            LOG.exception("Error when saving file.")
            messagebox.showerror(f"Error Detected - {APP_NAME_WITH_VERSION}", "An error occurred while saving.")
            return False

    def frames(self) -> list[BaseRulesTab]:
        return [self.nametowidget(tab_id) for tab_id in self.tabs()]
