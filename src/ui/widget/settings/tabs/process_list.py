import textwrap
from tkinter import PhotoImage, ttk, X, BOTH, NORMAL, DISABLED, CENTER, Menu, LEFT, END
from tkinter.ttk import Notebook
from typing import Optional

from constants.log import LOG
from constants.resources import UI_PROCESS_LIST, UI_REFRESH
from constants.threads import THREAD_PROCESS_LIST
from constants.ui import UI_PADDING, ActionEvents, LEFT_PACK, CMENU_ADD_PROCESS_RULE_LABEL, \
    CMENU_ADD_SERVICE_RULE_LABEL
from enums.filters import FilterByProcessType
from enums.rules import RuleType
from enums.selector import SelectorType
from model.process import Process
from service.processes_info_service import ProcessesInfoService
from ui.widget.common.button import ExtendedButton
from ui.widget.common.combobox import EnumCombobox
from ui.widget.common.entry import ExtendedEntry
from ui.widget.common.treeview.pydantic import PydanticTreeviewLoader
from ui.widget.common.treeview.sortable import SortableTreeview
from ui.widget.settings.tabs.base_tab import BaseTab
from ui.widget.settings.tabs.rules.rules_list import RulesList
from util.scheduler import TaskScheduler
from util.ui import load_img


class ProcessListTab(BaseTab):
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
        self._data: dict[int, Process] = {}

        super().__init__(master)

        self._setup_widgets()
        self._loader = PydanticTreeviewLoader(self.process_list, self.model)
        self._pack()
        self._setup_context_menu()

    def _create_process_list(self):
        columns = [key for key, field_info in self.model.model_fields.items() if not field_info.exclude]

        return SortableTreeview(
            self,
            show='headings',
            columns=columns,
            selectmode="browse"
        )

    def _create_progress_bar(self):
        progress_bar = ttk.Progressbar(self.process_list, mode='indeterminate')
        progress_bar.start()
        return progress_bar

    def _create_actions(self):
        actions = ProcessListTabActions(self)
        actions.bind(ActionEvents.REFRESH, lambda _: self._refresh(), "+")
        actions.bind(ActionEvents.FILTER_BY_TYPE, lambda _: self._update_process_list(), "+")
        actions.bind(ActionEvents.SEARCH_CHANGE, lambda _: self._update_process_list(), "+")

        return actions

    def _pack(self):
        self.actions.pack(fill=X, padx=UI_PADDING, pady=(UI_PADDING, 0))
        self.process_list.pack(fill=BOTH, expand=True, padx=UI_PADDING, pady=UI_PADDING)

    def load_from_config(self, config: dict):
        self._refresh()

    def _update_process_list(self):
        filter_by_type = self.actions.filterByType.get_enum_value()
        search_query = self.actions.search.get().strip().lower()

        data = []

        for row in self._data.values():
            by_type = (filter_by_type == FilterByProcessType.ALL
                       or filter_by_type == FilterByProcessType.PROCESSES and row.service is None
                       or filter_by_type == FilterByProcessType.SERVICES and row.service is not None)

            by_search = not search_query or any(
                value is not None and search_query in str(value).lower()
                for value in row.model_dump().values()
            )

            if by_type and by_search:
                data.append(row)

        self._set_display_columns(filter_by_type)
        self._loader.set_data(data)

    def _set_display_columns(self, filter_by_type):
        process_list = self.process_list
        display_columns = list(process_list['columns'])

        if filter_by_type == FilterByProcessType.PROCESSES:
            display_columns.remove('service_name')

        process_list['displaycolumns'] = display_columns

    def _refresh(self):
        try:
            self._refresh_state(True)
            self.process_list.clear()

            def load():
                try:
                    def set_data(data):
                        try:
                            self._data = data
                            self._update_process_list()
                        except:
                            LOG.exception("Refresh error")
                        finally:
                            self._refresh_state(False)

                    values = ProcessesInfoService.get_processes(False)
                    self.after(0, set_data, values)
                except:
                    self._refresh_state(False)
                    LOG.exception("Refresh error")

            TaskScheduler.schedule_task(THREAD_PROCESS_LIST, load)
        except:
            self._refresh_state(False)
            LOG.exception("Refresh error")

    def _refresh_state(self, lock: bool):
        try:
            actions = self.actions
            actions.refresh['state'] = DISABLED if lock else NORMAL

            progress_bar = self._progress_bar
            if lock:
                progress_bar.place(relx=0.5, rely=0.5, anchor=CENTER)
            else:
                progress_bar.place_forget()
        except:
            # When the window was closed while getting the process list
            pass

    def save_to_config(self, config: dict):
        pass

    def has_changes(self) -> bool:
        return False

    def has_error(self) -> bool:
        return False

    def commit_changes(self):
        pass

    def _setup_widgets(self):
        self.process_list = self._create_process_list()
        self._progress_bar = self._create_progress_bar()
        self.actions = self._create_actions()

    def as_model(self, row_id) -> Process:
        pid = int(self.process_list.as_dict(row_id)['pid'])
        return self._data[pid]

    def _setup_context_menu(self):
        process_list = self.process_list

        self._context_menu = context_menu = Menu(process_list, tearoff=0)
        self._process_menu = Menu(context_menu, tearoff=0)

        context_menu.add_cascade(
            label=CMENU_ADD_PROCESS_RULE_LABEL,
            menu=self._process_menu
        )

        context_menu.add_command(
            label=CMENU_ADD_SERVICE_RULE_LABEL,
            command=lambda: self._add_rule(RuleType.SERVICE)
        )

        process_list.bind("<Button-3>", self._show_context_menu)

    def _show_context_menu(self, event):
        context_menu = self._context_menu
        menu = self._process_menu
        process_list = self.process_list
        row_id = process_list.identify_row(event.y)

        if row_id:
            process_list.selection_set(row_id)
            row = self.as_model(row_id)
            exists = False

            menu.delete(0, END)
            if row.process_name:
                exists = True
                menu.add_command(
                    label=f"By {SelectorType.NAME.value}: {row.process_name}",
                    command=lambda: self._add_rule(RuleType.PROCESS, SelectorType.NAME)
                )

            if row.bin_path:
                exists = True
                menu.add_command(
                    label=textwrap.shorten(
                        f"By {SelectorType.PATH.value}: {row.bin_path}",
                        width=128,
                        placeholder="..."
                    ),
                    command=lambda: self._add_rule(RuleType.PROCESS, SelectorType.PATH)
                )

            if row.cmd_line:
                exists = True
                menu.add_command(
                    label=textwrap.shorten(
                        f"By {SelectorType.CMDLINE.value}: {row.cmd_line}",
                        width=128,
                        placeholder="..."
                    ),
                    command=lambda: self._add_rule(RuleType.PROCESS, SelectorType.CMDLINE)
                )

            self._context_menu.entryconfig(CMENU_ADD_PROCESS_RULE_LABEL, state=NORMAL if exists else DISABLED)
            self._context_menu.entryconfig(CMENU_ADD_SERVICE_RULE_LABEL, state=NORMAL if row.service else DISABLED)

            context_menu.post(event.x_root, event.y_root)

    def _add_rule(self, rule_type: RuleType, selector_type: Optional[SelectorType] = None):
        if rule_type == RuleType.SERVICE and selector_type is not None:
            raise ValueError("rule_type == RuleType.SERVICE and selector_type is not None")

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


class ProcessListTabActions(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._search_delay_timer = None
        self._setup_btn()

    def _setup_btn(self):
        self.refresh = refresh = ExtendedButton(
            self,
            # text="Refresh",
            event=ActionEvents.REFRESH,
            image=load_img(file=UI_REFRESH),
            description="**Refreshes** the list of __processes__."
        )

        self.filterByType = filterByType = EnumCombobox(
            self,
            FilterByProcessType,
            description="**Filters** processes by __type__.",
            state="readonly"
        )

        self.search = search = ExtendedEntry(
            self,
            description="**Searches** processes by __name__ or __attribute__.",
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

        self._search_delay_timer = self.after(250, self._trigger_search_change_event)

    def _trigger_search_change_event(self):
        self.event_generate(ActionEvents.SEARCH_CHANGE)
        self._search_delay_timer = None
