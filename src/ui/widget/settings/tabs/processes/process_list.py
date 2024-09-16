import os.path
from tkinter import Menu, LEFT, END, NORMAL, DISABLED
from typing import Callable, Optional

from PIL import ImageTk
from pydantic import BaseModel

from constants.log import LOG
from constants.resources import UI_ADD_PROCESS_RULE, UI_ADD_SERVICE_RULE, UI_COPY, UI_SERVICE, \
    UI_PROCESS
from constants.threads import THREAD_PROCESS_LIST_ICONS
from constants.ui import CMENU_ADD_PROCESS_RULE_LABEL, CMENU_ADD_SERVICE_RULE_LABEL, COLUMN_WIDTH_WITH_ICON, \
    CMENU_COPY_LABEL, ERROR_TRYING_UPDATE_TERMINATED_TKINTER_INSTANCE
from enums.filters import FilterByProcessType
from enums.rules import RuleType
from enums.selector import SelectorType
from model.process import Process
from ui.widget.common.treeview.pydantic import PydanticTreeviewLoader
from ui.widget.common.treeview.sortable import SortableTreeview
from util.scheduler import TaskScheduler
from util.ui import load_img, trim_cmenu_label
from util.utils import get_icon_from_exe


class ProcessList(SortableTreeview):
    def __init__(
            self,
            model: type[BaseModel],
            add_rule_command: Callable[[RuleType, Optional[SelectorType]], None],
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
            CMENU_COPY_LABEL: load_img(UI_COPY),
        }
        self._context_menu = menu = Menu(self, tearoff=0)
        self._process_menu = Menu(menu, tearoff=0)
        self._copy_menu = Menu(menu, tearoff=0)

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

        menu.add_separator()

        menu.add_cascade(
            label=CMENU_COPY_LABEL,
            menu=self._copy_menu,
            image=icons[CMENU_COPY_LABEL],
            compound=LEFT
        )

        self.bind("<Button-3>", self._show_context_menu, '+')

    def _show_context_menu(self, event):
        context_menu = self._context_menu
        process_list = self
        row_id = process_list.identify_row(event.y)

        if row_id:
            process_list.selection_set(row_id)
            row = self.as_model(row_id)
            process_exists = self._update_process_menu(row)
            self._update_copy_menu(row)

            self._context_menu.entryconfig(CMENU_ADD_PROCESS_RULE_LABEL, state=NORMAL if process_exists else DISABLED)
            self._context_menu.entryconfig(CMENU_ADD_SERVICE_RULE_LABEL, state=NORMAL if row.service else DISABLED)

            context_menu.post(event.x_root, event.y_root)

    def _update_process_menu(self, row):
        process_menu = self._process_menu
        exists = False

        process_menu.delete(0, END)

        if row.process_name:
            exists = True
            process_menu.add_command(
                label=f"By {SelectorType.NAME.value}: {row.process_name}",
                command=lambda: self._add_rule(RuleType.PROCESS, SelectorType.NAME)
            )

        if row.bin_path:
            exists = True
            process_menu.add_command(
                label=trim_cmenu_label(f"By {SelectorType.PATH.value}: {row.bin_path}"),
                command=lambda: self._add_rule(RuleType.PROCESS, SelectorType.PATH)
            )

        if row.cmd_line:
            exists = True
            process_menu.add_command(
                label=trim_cmenu_label(f"By {SelectorType.CMDLINE.value}: {row.cmd_line}"),
                command=lambda: self._add_rule(RuleType.PROCESS, SelectorType.CMDLINE)
            )

        return exists

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

    def _update_copy_menu(self, row):
        copy_menu = self._copy_menu
        copy_menu.delete(0, END)

        values = [
            row.pid,
            row.process_name,
            row.service_name,
            row.bin_path,
            row.cmd_line
        ]

        values = map(lambda o: str(o) if o else '', values)
        values = filter(lambda o: o, values)
        values = [*dict.fromkeys(values)]

        for value in values:
            copy_menu.add_command(label=trim_cmenu_label(value), command=lambda v=value: self._copy_to_clipboard(v))

    def _copy_to_clipboard(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()

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
