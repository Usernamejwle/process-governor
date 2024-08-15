import tkinter as tk
from abc import ABC
from tkinter import ttk, PhotoImage
from tkinter.ttk import Notebook

from constants.resources import UI_ADD, UI_DELETE, UI_UP, UI_DOWN
from constants.ui import UI_PADDING, RulesListEvents, ActionEvents
from enums.rules import RuleType
from ui.widget.common.button import IconedButton
from ui.widget.settings.tabs.base_tab import BaseTab
from ui.widget.settings.tabs.rules.rules_list import RulesList


class BaseRulesTab(BaseTab, ABC):
    def __init__(self, master: Notebook, rule_type: RuleType):
        super().__init__(master)

        self.rule_type: RuleType = rule_type
        self.rules_list = self._create_rules_list()
        self.buttons = self._create_buttons()

        self._update_buttons_state()
        self._pack()

    def _pack(self):
        self.buttons.pack(fill=tk.X, padx=UI_PADDING, pady=(UI_PADDING, 0))
        self.rules_list.pack(fill=tk.BOTH, expand=True, padx=UI_PADDING, pady=UI_PADDING)

    def _create_rules_list(self):
        rules_list = RulesList(self.rule_type.clazz, self)

        rules_list.bind("<<TreeviewSelect>>", lambda _: self._update_buttons_state(), "+")
        rules_list.bind(RulesListEvents.UNSAVED_CHANGES_STATE, lambda _: self._update_buttons_state(), "+")

        return rules_list

    def _create_buttons(self):
        buttons = RulesTabButtons(self)

        buttons.bind(ActionEvents.ADD, lambda _: self.rules_list.add_row(), "+")
        buttons.bind(ActionEvents.DELETE, lambda _: self.rules_list.delete_selected_rows(), "+")
        buttons.bind(ActionEvents.UP, lambda _: self.rules_list.move_rows_up(), "+")
        buttons.bind(ActionEvents.DOWN, lambda _: self.rules_list.move_rows_down(), "+")

        return buttons

    def _update_buttons_state(self):
        rules_list = self.rules_list
        buttons = self.buttons
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

        self.master.event_generate(RulesListEvents.UNSAVED_CHANGES_STATE)

    def load_from_config(self, config: dict):
        self.rules_list.set_data(config.get(self.rule_type.field_in_config, []))

    def save_to_config(self, config: dict):
        rules_list = self.rules_list
        config[self.rule_type.field_in_config] = rules_list.get_data()
        rules_list.set_unsaved_changes(False)

    def has_unsaved_changes(self) -> bool:
        return self.rules_list.has_unsaved_changes

    def has_error(self) -> bool:
        return self.rules_list.has_error()


class RulesTabButtons(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup_btn()

    def _setup_btn(self):
        self.add = add = IconedButton(
            self,
            text=" Add",
            command=lambda: self.event_generate(ActionEvents.ADD),
            image=PhotoImage(file=UI_ADD)
        )

        self.delete = delete = IconedButton(
            self,
            text=" Del",
            command=lambda: self.event_generate(ActionEvents.DELETE),
            image=PhotoImage(file=UI_DELETE)
        )

        self.move_up = move_up = IconedButton(
            self,
            text=" Up",
            command=lambda: self.event_generate(ActionEvents.UP),
            image=PhotoImage(file=UI_UP)
        )

        self.move_down = move_down = IconedButton(
            self,
            text=" Down",
            command=lambda: self.event_generate(ActionEvents.DOWN),
            image=PhotoImage(file=UI_DOWN)
        )

        left_btn_pack = dict(side=tk.LEFT, padx=(0, UI_PADDING))
        add.pack(**left_btn_pack)
        delete.pack(**left_btn_pack)
        move_up.pack(**left_btn_pack)
        move_down.pack(**left_btn_pack)
