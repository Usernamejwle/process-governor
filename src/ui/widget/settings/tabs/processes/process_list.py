import os.path
from typing import Callable, Optional

from PIL import ImageTk
from pydantic import BaseModel

from configuration.rule import ProcessRule, ServiceRule
from constants.log import LOG
from constants.resources import UI_SERVICE, \
    UI_PROCESS
from constants.threads import THREAD_PROCESS_LIST_ICONS
from constants.ui import COLUMN_WIDTH_WITH_ICON, \
    ERROR_TRYING_UPDATE_TERMINATED_TKINTER_INSTANCE
from enums.filters import FilterByProcessType
from enums.rules import RuleType
from enums.selector import SelectorType
from model.process import Process
from ui.widget.common.treeview.pydantic import PydanticTreeviewLoader
from ui.widget.common.treeview.sortable import SortableTreeview
from ui.widget.settings.tabs.processes.process_list_context_menu import ProcessContextMenu
from util.scheduler import TaskScheduler
from util.ui import load_img
from util.utils import get_icon_from_exe


class ProcessList(SortableTreeview):
    def __init__(
            self,
            model: type[BaseModel],
            add_rule_command: Callable[[RuleType, Optional[SelectorType]], None],
            find_rules_by_process_command: Callable[[Process], list[tuple[str, ProcessRule | ServiceRule]]],
            go_to_rule_command: Callable[[str, RuleType], None],
            *args, **kwargs
    ):
        columns = [key for key, field_info in model.model_fields.items() if not field_info.exclude]

        super().__init__(
            *args,
            **kwargs,
            show='tree headings',
            columns=columns,
            selectmode="browse"
        )

        self.heading("#0", text="")
        self.column("#0", width=COLUMN_WIDTH_WITH_ICON, stretch=False)

        self._filter_by_type: FilterByProcessType = FilterByProcessType.ALL
        self._filter_by_search_query: Optional[str] = None

        self._process_icon = load_img(UI_PROCESS)
        self._service_icon = load_img(UI_SERVICE)
        self._icons = {}

        self._data: dict[int, Process] = {}
        self._loader = PydanticTreeviewLoader(self, model)
        self._setup_context_menu(add_rule_command, find_rules_by_process_command, go_to_rule_command)

    def set_data(self, values: dict[int, Process]):
        self._data = values

    def set_display_columns(self, filter_by_type):
        display_columns = list(self['columns'])

        if filter_by_type == FilterByProcessType.PROCESSES:
            display_columns.remove('service_name')

        self['displaycolumns'] = display_columns

    def set_filter(self, by_type: FilterByProcessType, by_search_query: str):
        self._filter_by_type = by_type
        self._filter_by_search_query = by_search_query

    def update_ui(self):
        filter_by_type = self._filter_by_type
        search_query = self._filter_by_search_query
        data = self._get_filtered_data(filter_by_type, search_query)

        self.set_display_columns(filter_by_type)
        self._loader.set_data(data)

        self._update_process_icons()

    def _update_process_icons(self):
        def set_icons(icons):
            try:
                for row_id, icon in icons:
                    self.item(row_id, image=icon)
            except BaseException as e:
                if ERROR_TRYING_UPDATE_TERMINATED_TKINTER_INSTANCE not in str(e):
                    LOG.exception("Update process icons error")

        def get_icons():
            try:
                icons = {row_id: self.get_process_icon(self.as_model(row_id)) for row_id in self.get_children()}
                self.after(0, lambda: set_icons(icons.items()))
            except BaseException as e:
                if ERROR_TRYING_UPDATE_TERMINATED_TKINTER_INSTANCE not in str(e):
                    LOG.exception("Get process icons error")

        TaskScheduler.schedule_task(THREAD_PROCESS_LIST_ICONS, get_icons)

    def _get_filtered_data(self, filter_by_type, search_query):
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

        return data

    def as_model(self, row_id) -> Process:
        pid = int(self.as_dict(row_id)['pid'])
        return self._data[pid]

    def get_process_icon(self, process: Process):
        bin_path = process.bin_path

        if bin_path in self._icons:
            return self._icons[bin_path]

        image = None

        if bin_path:
            path = os.path.abspath(bin_path)

            if os.path.exists(path):
                try:
                    pil_image = get_icon_from_exe(path)
                    image = ImageTk.PhotoImage(pil_image) if pil_image else None
                except:
                    pass

        if image is None:
            if process.service:
                image = self._service_icon
            else:
                image = self._process_icon

        self._icons[bin_path] = image
        return image

    def _setup_context_menu(
            self,
            add_rule_command: Callable[[RuleType, Optional[SelectorType]], None],
            find_rules_by_process_command: Callable[[Process], list[tuple[str, ProcessRule | ServiceRule]]],
            go_to_rule_command: Callable[[str, RuleType], None]
    ):
        self._context_menu = ProcessContextMenu(self, add_rule_command, find_rules_by_process_command,
                                                go_to_rule_command)
        self.bind("<Button-3>", self._context_menu.show, '+')
