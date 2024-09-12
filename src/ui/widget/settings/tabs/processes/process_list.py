import textwrap
from tkinter import Menu, LEFT, END, NORMAL, DISABLED
from typing import Callable, Optional

from pydantic import BaseModel

from constants.resources import UI_ADD_PROCESS_RULE, UI_ADD_SERVICE_RULE
from constants.ui import CMENU_ADD_PROCESS_RULE_LABEL, CMENU_ADD_SERVICE_RULE_LABEL
from enums.filters import FilterByProcessType
from enums.rules import RuleType
from enums.selector import SelectorType
from model.process import Process
from ui.widget.common.treeview.pydantic import PydanticTreeviewLoader
from ui.widget.common.treeview.sortable import SortableTreeview
from util.ui import load_img


class ProcessList(SortableTreeview):
    def __init__(
            self,
            model: type[BaseModel],
            add_rule_command: Callable[[RuleType, Optional[SelectorType]], None],
            *args, **kwargs
    ):
        self._filter_by_type: FilterByProcessType = FilterByProcessType.ALL
        self._filter_by_search_query: Optional[str] = None

        columns = [key for key, field_info in model.model_fields.items() if not field_info.exclude]

        super().__init__(
            *args,
            **kwargs,
            show='headings',
            columns=columns,
            selectmode="browse"
        )

        self._add_rule: Callable[[RuleType, Optional[SelectorType]], None] = add_rule_command
        self._data: dict[int, Process] = {}
        self._loader = PydanticTreeviewLoader(self, model)
        self._setup_context_menu()

    def set_data(self, values: dict[int, Process]):
        self._data = values

    def _setup_context_menu(self):
        self._context_menu_icons = icons = {
            CMENU_ADD_PROCESS_RULE_LABEL: load_img(UI_ADD_PROCESS_RULE),
            CMENU_ADD_SERVICE_RULE_LABEL: load_img(UI_ADD_SERVICE_RULE),
        }
        self._context_menu = menu = Menu(self, tearoff=0)
        self._process_menu = Menu(menu, tearoff=0)

        menu.add_cascade(
            label=CMENU_ADD_PROCESS_RULE_LABEL,
            menu=self._process_menu,
            image=icons[CMENU_ADD_PROCESS_RULE_LABEL],
            compound=LEFT
        )

        menu.add_command(
            label=CMENU_ADD_SERVICE_RULE_LABEL,
            command=lambda: self._add_rule(RuleType.SERVICE, None),
            image=icons[CMENU_ADD_SERVICE_RULE_LABEL],
            compound=LEFT
        )

        self.bind("<Button-3>", self._show_context_menu, '+')

    def _show_context_menu(self, event):
        context_menu = self._context_menu
        menu = self._process_menu
        process_list = self
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

        self.set_display_columns(filter_by_type)
        self._loader.set_data(data)

    def as_model(self, row_id) -> Process:
        pid = int(self.as_dict(row_id)['pid'])
        return self._data[pid]
