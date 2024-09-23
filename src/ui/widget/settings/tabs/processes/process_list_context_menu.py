import os
from tkinter import Menu, LEFT, END, NORMAL, DISABLED
from typing import Callable, Optional

from configuration.rule import ProcessRule, ServiceRule
from constants.resources import UI_ADD_PROCESS_RULE, UI_ADD_SERVICE_RULE, UI_COPY, UI_OPEN_FOLDER, \
    UI_OPEN_FILE_PROPERTIES, UI_OPEN_SERVICE_PROPERTIES, UI_GO_TO_RULE, UI_PROCESS_RULES, UI_SERVICE_RULES
from enums.rules import RuleType
from enums.selector import SelectorType
from model.process import Process
from util.files import explore, show_file_properties, show_service_properties
from util.ui import load_img, trim_cmenu_label

CMENU_ADD_PROCESS_RULE_LABEL = "  Add Process Rule"
CMENU_ADD_SERVICE_RULE_LABEL = "  Add Service Rule"
CMENU_COPY_LABEL = "  Copy Special"
CMENU_OPEN_PROCESS_FOLDER_LABEL = "  Open file location"
CMENU_OPEN_FILE_PROPERTIES_LABEL = "  File Properties"
CMENU_OPEN_SERVICE_PROPERTIES_LABEL = "  Service Properties"
CMENU_GO_TO_RULE_LABEL = "  Go to Rule"


class ProcessContextMenu:
    def __init__(
            self,
            master,
            add_rule_command: Callable[[RuleType, Optional[SelectorType]], None],
            find_rules_by_process_command: Callable[[Process], list[tuple[str, ProcessRule | ServiceRule]]],
            go_to_rule_command: Callable[[str, RuleType], None]
    ):
        self.master = master
        self._add_rule = add_rule_command
        self._find_rules_by_process = find_rules_by_process_command
        self._go_to_rule = go_to_rule_command

        self._context_menu_icons = {
            CMENU_ADD_PROCESS_RULE_LABEL: load_img(UI_ADD_PROCESS_RULE),
            CMENU_ADD_SERVICE_RULE_LABEL: load_img(UI_ADD_SERVICE_RULE),
            CMENU_COPY_LABEL: load_img(UI_COPY),
            CMENU_OPEN_PROCESS_FOLDER_LABEL: load_img(UI_OPEN_FOLDER),
            CMENU_OPEN_FILE_PROPERTIES_LABEL: load_img(UI_OPEN_FILE_PROPERTIES),
            CMENU_OPEN_SERVICE_PROPERTIES_LABEL: load_img(UI_OPEN_SERVICE_PROPERTIES),
            CMENU_GO_TO_RULE_LABEL: load_img(UI_GO_TO_RULE),
            ProcessRule: load_img(UI_PROCESS_RULES),
            ServiceRule: load_img(UI_SERVICE_RULES)
        }

        self._setup_context_menu()

    def _setup_context_menu(self):
        icons = self._context_menu_icons

        self._root_menu = menu = Menu(self.master, tearoff=0)
        self._process_menu = Menu(menu, tearoff=0)
        self._copy_menu = Menu(menu, tearoff=0)
        self._rules_menu = Menu(menu, tearoff=0)

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

        menu.add_cascade(
            label=CMENU_GO_TO_RULE_LABEL,
            menu=self._rules_menu,
            image=icons[CMENU_GO_TO_RULE_LABEL],
            compound=LEFT
        )

        menu.add_separator()

        menu.add_cascade(
            label=CMENU_COPY_LABEL,
            menu=self._copy_menu,
            image=icons[CMENU_COPY_LABEL],
            compound=LEFT
        )

        menu.add_separator()

        menu.add_command(
            label=CMENU_OPEN_PROCESS_FOLDER_LABEL,
            command=self._open_process_folder,
            image=icons[CMENU_OPEN_PROCESS_FOLDER_LABEL],
            compound=LEFT
        )

        menu.add_command(
            label=CMENU_OPEN_FILE_PROPERTIES_LABEL,
            command=self._open_file_properties,
            image=icons[CMENU_OPEN_FILE_PROPERTIES_LABEL],
            compound=LEFT
        )

        menu.add_command(
            label=CMENU_OPEN_SERVICE_PROPERTIES_LABEL,
            command=self.open_service_properties,
            image=icons[CMENU_OPEN_SERVICE_PROPERTIES_LABEL],
            compound=LEFT
        )

    def _open_file_properties(self):
        selected_item = self.master.selection()

        if not selected_item:
            return

        row = self.master.as_model(selected_item[0])
        show_file_properties(row.bin_path, self.master.winfo_toplevel().winfo_id())

    def _open_process_folder(self):
        selected_item = self.master.selection()

        if not selected_item:
            return

        row = self.master.as_model(selected_item[0])
        explore(row.bin_path)

    def open_service_properties(self):
        selected_item = self.master.selection()

        if not selected_item:
            return

        row = self.master.as_model(selected_item[0])
        show_service_properties(row.service.display_name)

    def _copy_to_clipboard(self, text):
        self.master.clipboard_clear()
        self.master.clipboard_append(text)
        self.master.update()

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

    def _update_rules_menu(self, row):
        icons = self._context_menu_icons
        rules_menu = self._rules_menu
        rules_menu.delete(0, END)

        rules = self._find_rules_by_process(row)

        if not rules:
            return False

        to_state = (DISABLED, NORMAL)
        is_first = True

        for row_id, rule in rules:
            rule_type = RuleType.PROCESS if isinstance(rule, ProcessRule) else RuleType.SERVICE

            rules_menu.add_command(
                label=f"  {trim_cmenu_label(rule.selector)}",
                command=lambda ri=row_id, rt=rule_type: self._go_to_rule(ri, rt),
                image=icons[type(rule)],
                compound=LEFT,
                state=to_state[is_first]
            )

            is_first = False

        return True

    def show(self, event):
        context_menu = self._root_menu
        process_list = self.master
        row_id = process_list.identify_row(event.y)

        if row_id:
            process_list.selection_set(row_id)
            row: Process = process_list.as_model(row_id)
            is_file = os.path.isfile(row.bin_path or '')
            is_service = row.service is not None
            to_state = (DISABLED, NORMAL)

            not_empty_process_menu = self._update_process_menu(row)
            self._update_copy_menu(row)
            not_empty_rules_menu = self._update_rules_menu(row)

            context_menu.entryconfig(CMENU_ADD_PROCESS_RULE_LABEL, state=to_state[not_empty_process_menu])
            context_menu.entryconfig(CMENU_ADD_SERVICE_RULE_LABEL, state=to_state[is_service])
            context_menu.entryconfig(CMENU_OPEN_PROCESS_FOLDER_LABEL, state=to_state[is_file])
            context_menu.entryconfig(CMENU_OPEN_FILE_PROPERTIES_LABEL, state=to_state[is_file])
            context_menu.entryconfig(CMENU_OPEN_SERVICE_PROPERTIES_LABEL, state=to_state[is_service])
            context_menu.entryconfig(CMENU_GO_TO_RULE_LABEL, state=to_state[not_empty_rules_menu])

            context_menu.post(event.x_root, event.y_root)
