from tkinter import PhotoImage, ttk, X, BOTH, NORMAL, DISABLED, CENTER
from tkinter.ttk import Notebook
from typing import Optional

from constants.log import LOG
from constants.resources import UI_PROCESS_LIST
from constants.threads import THREAD_PROCESS_LIST_DATA
from constants.ui import UI_PADDING, ActionEvents, ERROR_TRYING_UPDATE_TERMINATED_TKINTER_INSTANCE
from enums.rules import RuleType
from enums.selector import SelectorType
from model.process import Process
from service.processes_info_service import ProcessesInfoService
from ui.widget.settings.tabs.base_tab import BaseTab
from ui.widget.settings.tabs.processes.process_list import ProcessList
from ui.widget.settings.tabs.processes.process_list_actions import ProcessListActions
from ui.widget.settings.tabs.rules.rules_list import RulesList
from util.scheduler import TaskScheduler
from util.ui import load_img


class ProcessesTab(BaseTab):
    @staticmethod
    def default_tooltip() -> str:
        return "Use the **context menu** to add a __process__ or __service__ as a rule."

    @staticmethod
    def icon() -> PhotoImage:
        return load_img(file=UI_PROCESS_LIST)

    @staticmethod
    def title() -> str:
        return 'Process List'

    @staticmethod
    def description() -> str:
        return ("Interface for **browsing** the list of active __processes__ and __services__ with the option to "
                "**add** selected items to the rules configuration.")

    def __init__(self, master: Notebook, process_rules_list: RulesList, service_rules_list: RulesList):
        self.model = Process
        self.process_rules_list = process_rules_list
        self.service_rules_list = service_rules_list

        super().__init__(master)

        self._create_process_list()
        self._create_progress_bar()
        self._create_actions()

        self._pack()

    def _create_process_list(self):
        self.process_list = process_list = ProcessList(self.model, self._add_rule, self)
        process_list.bind("<F5>", lambda _: self._refresh(), "+")

    def _create_progress_bar(self):
        self._progress_bar = progress_bar = ttk.Progressbar(self.process_list, mode='indeterminate')
        progress_bar.start()

    def _create_actions(self):
        self.actions = actions = ProcessListActions(self)
        actions.bind(ActionEvents.REFRESH, lambda _: self._refresh(), "+")
        actions.bind(ActionEvents.FILTER_BY_TYPE, lambda _: self._update_process_list(), "+")
        actions.bind(ActionEvents.SEARCH_CHANGE, lambda _: self._update_process_list(), "+")

    def _pack(self):
        self.actions.pack(fill=X, padx=UI_PADDING, pady=(UI_PADDING, 0))
        self.process_list.pack(fill=BOTH, expand=True, padx=UI_PADDING, pady=UI_PADDING)

    def load_from_config(self, config: dict):
        self._refresh()

    def _update_process_list(self):
        try:
            filter_by_type = self.actions.filterByType.get_enum_value()
            search_query = self.actions.search.get().strip().lower()

            self.process_list.set_filter(filter_by_type, search_query)
            self.process_list.update_ui()
        except BaseException as e:
            if ERROR_TRYING_UPDATE_TERMINATED_TKINTER_INSTANCE not in str(e):
                LOG.exception("Update process list error")

    def _refresh(self):
        LOG.info("Refreshing process list...")

        def update_process_list():
            LOG.info("Updating process list...")

            try:
                self._update_process_list()
            finally:
                self._refresh_state()

        def load_data():
            LOG.info("Loading data...")

            try:
                self.process_list.set_data(ProcessesInfoService.get_processes(False))
                self.after(0, update_process_list)
            except BaseException as e:
                if ERROR_TRYING_UPDATE_TERMINATED_TKINTER_INSTANCE not in str(e):
                    LOG.exception("Load data error")

                self._refresh_state()

        try:
            self._refresh_state(True)
            self.process_list.clear()

            TaskScheduler.schedule_task(THREAD_PROCESS_LIST_DATA, load_data)
        except BaseException as e:
            if ERROR_TRYING_UPDATE_TERMINATED_TKINTER_INSTANCE not in str(e):
                LOG.exception("Refresh error")

            self._refresh_state()

    def _refresh_state(self, lock: bool = False):
        try:
            actions = self.actions
            actions.refresh['state'] = DISABLED if lock else NORMAL

            progress_bar = self._progress_bar

            if lock:
                progress_bar.place(relx=0.5, rely=0.5, anchor=CENTER)
            else:
                progress_bar.place_forget()
        except BaseException as e:
            if ERROR_TRYING_UPDATE_TERMINATED_TKINTER_INSTANCE not in str(e):
                LOG.exception("Refresh state error")

    def save_to_config(self, config: dict):
        pass

    def has_changes(self) -> bool:
        return False

    def has_error(self) -> bool:
        return False

    def commit_changes(self):
        pass

    def _add_rule(self, rule_type: RuleType, selector_type: Optional[SelectorType] = None):
        if rule_type == RuleType.SERVICE and selector_type is not None:
            raise ValueError("selector_type must be None when rule_type is SERVICE")

        process_list = self.process_list
        row_id = process_list.selection()
        row = process_list.as_dict(row_id)
        rules_list = None

        if rule_type == RuleType.PROCESS:
            rules_list = self.process_rules_list
        elif rule_type == RuleType.SERVICE:
            rules_list = self.service_rules_list

        if rules_list is None:
            raise ValueError("rules_list is None")

        rule_row = rules_list._loader.get_default_row()

        if selector_type is None:
            rule_row['selector'] = row['service_name']
        else:
            rule_row['selectorBy'] = str(selector_type)

            if selector_type == SelectorType.NAME:
                rule_row['selector'] = row['process_name']
            elif selector_type == SelectorType.PATH:
                rule_row['selector'] = row['bin_path']
            elif selector_type == SelectorType.CMDLINE:
                rule_row['selector'] = row['cmd_line']

        rules_list.add_row([*rule_row.values()], index=0)
