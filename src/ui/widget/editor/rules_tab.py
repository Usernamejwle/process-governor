import tkinter as tk
from tkinter import ttk, LEFT, messagebox

from constants.any import LOG
from constants.app_info import APP_NAME_WITH_VERSION
from constants.ui import UI_PADDING, ActionEvents, RulesListEvents
from enums.rules import RuleType
from service.config_service import ConfigService
from ui.widget.editor.buttons import RulesListButtons
from ui.widget.editor.rules_list import RulesList


class RulesTabs(ttk.Notebook):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._list_by_rt: dict[RuleType, RulesList] = {}
        self._frame_to_rt: dict[str, RuleType] = {}
        self._buttons_by_rt = {}
        self._create_tabs()

    def _create_tabs(self):
        for rt in RuleType:
            frame = ttk.Frame(self)
            frame._icon = rt.get_icon()  # hard reference - fix missing icon bug
            key = str(frame)

            self._frame_to_rt[key] = rt
            self._list_by_rt[rt] = rules_list = self._create_rules_list(frame, rt)
            self._buttons_by_rt[rt] = buttons = self._create_buttons(frame, rules_list)

            buttons.pack(fill=tk.X, padx=UI_PADDING, pady=(UI_PADDING, 0))
            rules_list.pack(fill=tk.BOTH, expand=True, padx=UI_PADDING, pady=UI_PADDING)

            self.add(frame, text=f" {rt.title} ", image=frame._icon, compound=LEFT)
            self._update_buttons_state(key)

    def _create_rules_list(self, frame, rule_type: RuleType):
        rules_list = RulesList(rule_type.clazz, frame)

        rules_list.bind("<<TreeviewSelect>>", lambda _: self._update_buttons_state(), "+")
        rules_list.bind(RulesListEvents.UNSAVED_CHANGES_STATE, lambda _: self._update_buttons_state(), "+")

        return rules_list

    def _create_buttons(self, frame, rules_list: RulesList):
        buttons = RulesListButtons(frame)

        buttons.bind(ActionEvents.ADD, lambda _: rules_list.add_row(), "+")
        buttons.bind(ActionEvents.DELETE, lambda _: rules_list.delete_selected_rows(), "+")
        buttons.bind(ActionEvents.UP, lambda _: rules_list.move_rows_up(), "+")
        buttons.bind(ActionEvents.DOWN, lambda _: rules_list.move_rows_down(), "+")

        return buttons

    def current_list_of_tab(self, frame=None) -> RulesList:
        key = self._frame_to_rt[frame or self.select()]
        return self._list_by_rt[key]

    def current_buttons_of_tab(self, frame=None) -> RulesListButtons:
        key = self._frame_to_rt[frame or self.select()]
        return self._buttons_by_rt[key]

    def _update_buttons_state(self, frame=None):
        rules_list = self.current_list_of_tab(frame)
        buttons = self.current_buttons_of_tab(frame)
        selected_items = rules_list.selection()

        if selected_items:
            first_selected_item = selected_items[0]
            last_selected_item = selected_items[-1]
            first_index = rules_list.index(first_selected_item)
            last_index = rules_list.index(last_selected_item)
            total_items = len(rules_list.get_children())

            buttons.move_up["state"] = tk.NORMAL if first_index > 0 else tk.DISABLED
            buttons.move_down["state"] = tk.NORMAL if last_index < total_items - 1 else tk.DISABLED
        else:
            buttons.move_up["state"] = tk.DISABLED
            buttons.move_down["state"] = tk.DISABLED

        buttons.delete["state"] = tk.NORMAL if selected_items else tk.DISABLED

        self.event_generate(RulesListEvents.UNSAVED_CHANGES_STATE)

    def has_unsaved_changes(self) -> bool:
        for rule_list in self._list_by_rt.values():
            if rule_list.has_unsaved_changes:
                return True
        return False

    def has_error(self) -> bool:
        for rule_list in self._list_by_rt.values():
            if rule_list.has_error():
                return True
        return False

    def load_data(self):
        for rt, lst in self._list_by_rt.items():
            rules = ConfigService.load_rules_raw(rt)
            lst.set_raw_data(rules)

    def save_data(self) -> bool:
        try:
            if not self.has_unsaved_changes():
                return True

            if self.has_error():
                messagebox.showerror(
                    f"Error Detected - {APP_NAME_WITH_VERSION}",
                    "Unable to save: The current rules are invalid. "
                    "Ensure all rules are correct before saving."
                )
                return False

            for rt, lst in self._list_by_rt.items():
                rules = lst.get_data()
                ConfigService.save_rules(rt, rules)
                lst.set_unsaved_changes(False)

            return True
        except:
            LOG.exception("Error when saving file.")
            messagebox.showerror(f"Error Detected - {APP_NAME_WITH_VERSION}", "An error occurred while saving.")
            return False

    def list_by_rt(self) -> dict[RuleType, RulesList]:
        return self._list_by_rt

    def buttons_by_rt(self) -> dict[RuleType, RulesListButtons]:
        return self._buttons_by_rt

