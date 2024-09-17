from abc import ABC
from tkinter import X, BOTH, NORMAL, DISABLED
from tkinter.ttk import Notebook

from constants.ui import UI_PADDING, ActionEvents, ExtendedTreeviewEvents
from enums.rules import RuleType
from ui.widget.settings.tabs.base_tab import BaseTab
from ui.widget.settings.tabs.rules.rules_list import RulesList
from ui.widget.settings.tabs.rules.rules_list_actions import RulesListActions


class BaseRulesTab(BaseTab, ABC):
    @staticmethod
    def default_tooltip() -> str:
        return (
            "To add a new rule, click the **Add** button.\n"
            "To edit a rule, **double-click** on the corresponding cell.\n"
            "Use the **context menu** for additional actions."
        )

    def __init__(self, master: Notebook, rule_type: RuleType):
        super().__init__(master)

        self.rule_type: RuleType = rule_type
        self.model = rule_type.clazz
        self.rules_list = self._create_rules_list()
        self.actions = self._create_actions()

        self._pack()

    def _pack(self):
        self.actions.pack(fill=X, padx=UI_PADDING, pady=(UI_PADDING, 0))
        self.rules_list.pack(fill=BOTH, expand=True, padx=UI_PADDING, pady=UI_PADDING)

    def _create_rules_list(self):
        rules_list = RulesList(self.rule_type.clazz, self)

        rules_list.bind("<<TreeviewSelect>>", lambda _: self._update_actions_state(), "+")
        rules_list.bind(ExtendedTreeviewEvents.CHANGE, lambda _: self._update_actions_state(), "+")
        rules_list.bind(ExtendedTreeviewEvents.CHANGE,
                        lambda _: self.master.event_generate(ExtendedTreeviewEvents.CHANGE), "+")

        return rules_list

    def _create_actions(self):
        actions = RulesListActions(self)
        rules_list = self.rules_list

        actions.bind(ActionEvents.ADD, lambda _: rules_list.add_row(), "+")
        actions.bind(ActionEvents.DELETE, lambda _: rules_list.delete_selected_rows(), "+")
        actions.bind(ActionEvents.UP, lambda _: rules_list.move_rows_up(), "+")
        actions.bind(ActionEvents.DOWN, lambda _: rules_list.move_rows_down(), "+")

        return actions

    def _update_actions_state(self):
        rules_list = self.rules_list
        actions = self.actions
        selected_items = rules_list.selection()

        if selected_items:
            first_selected_item = selected_items[0]
            last_selected_item = selected_items[-1]
            first_index = rules_list.index(first_selected_item)
            last_index = rules_list.index(last_selected_item)
            total_items = len(rules_list.get_children())

            actions.move_up["state"] = NORMAL if first_index > 0 else DISABLED
            actions.move_down["state"] = NORMAL if last_index < total_items - 1 else DISABLED
        else:
            actions.move_up["state"] = DISABLED
            actions.move_down["state"] = DISABLED

        actions.delete["state"] = NORMAL if selected_items else DISABLED

    def load_from_config(self, config: dict):
        self.rules_list.set_data(config.get(self.rule_type.field_in_config, []))
        self.rules_list.history.clear()

    def save_to_config(self, config: dict):
        rules_list = self.rules_list
        config[self.rule_type.field_in_config] = rules_list.get_data()

    def has_changes(self) -> bool:
        return self.rules_list.has_changes()

    def commit_changes(self):
        self.rules_list.commit_changes()

    def has_error(self) -> bool:
        return self.rules_list.has_error()
