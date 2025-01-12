import os
from tkinter import messagebox, ttk, Tk, X, TOP, BOTH, DISABLED, NORMAL
from typing import Optional

from configuration.migration.all_migration import run_all_migration
from constants.app_info import APP_NAME_WITH_VERSION, APP_NAME, TITLE_ERROR, APP_TITLE
from constants.files import LOG_FILE_NAME
from constants.log import LOG
from constants.resources import APP_ICON
from constants.threads import THREAD_SETTINGS
from constants.ui import UI_PADDING, RC_WIN_SIZE, ActionEvents, SETTINGS_TITLE, EditableTreeviewEvents, \
    ExtendedTreeviewEvents
from ui.settings_actions import SettingsActions
from ui.widget.common.entry import ExtendedEntry
from ui.widget.settings.settings_tabs import SettingsTabs
from ui.widget.settings.tabs.base_tab import BaseTab
from ui.widget.settings.tabs.processes.process_tab import ProcessesTab
from ui.widget.settings.tabs.rules.base_rules_tab import BaseRulesTab
from ui.widget.settings.tabs.rules.rules_list import RulesList
from ui.widget.settings.tooltip import Tooltip
from util.files import open_config_file, open_log_file
from util.history import HistoryManager
from util.messages import yesno_error_box
from util.scheduler import TaskScheduler


class Settings(Tk):
    def __init__(self):
        super().__init__()

        self._tabs: SettingsTabs
        self._tooltip: Tooltip
        self._actions: SettingsActions

        self._create_widgets()
        self._pack()
        self._setup_window()

        self.after(1, self._after_init)

    def _after_init(self):
        self._setup_tooltips()
        self._setup_binds()

        self._tabs.load_data()

    def _setup_window(self):
        self._center_window()

        self.protocol("WM_DELETE_WINDOW", self.close)
        self.iconbitmap(APP_ICON)
        self.title(APP_TITLE)
        self.minsize(*RC_WIN_SIZE)

    def _setup_binds(self):
        self._tabs.bind(ExtendedTreeviewEvents.CHANGE, lambda _: self._update_actions_state(), "+")

        self._actions.bind(ActionEvents.SAVE, lambda _: self._save(), "+")
        self._actions.bind(ActionEvents.CONFIG, lambda _: open_config_file(), "+")
        self._actions.bind(ActionEvents.LOG, lambda _: open_log_file(), "+")

        self.bind("<Control-Tab>", lambda _: self._tabs.next_tab(), "+")
        self.bind("<Shift-Control-Tab>", lambda _: self._tabs.prev_tab(), "+")
        self.bind("<Key>", self._fix_cyrillic_binds, "+")
        self.bind("<KeyPress>", self._global_actions, "+")

    def _fix_cyrillic_binds(self, event):
        ctrl = (event.state & 0x4) != 0

        if not ctrl:
            return

        keycode = event.keycode
        keysym = event.keysym.upper()

        if keysym != "??":
            return

        keysym = chr(keycode)
        key_to_event = {
            "X": "<<Cut>>",
            "V": "<<Paste>>",
            "C": "<<Copy>>",
            "A": "<<SelectAll>>"
        }

        if keysym not in key_to_event:
            return

        self.focus_get().event_generate(key_to_event[keysym])

    def _global_actions(self, event):
        ctrl = (event.state & 0x4) != 0
        shift = (event.state & 0x1) != 0

        if not ctrl:
            return

        keycode = event.keycode
        keysym = event.keysym.upper()

        if keysym == "??":
            keysym = chr(keycode)

        if shift:
            key = ("Shift", keysym)
        else:
            key = (keysym,)

        key_to_callback = {
            ("D",): lambda: self._add_row(),
            ("F",): lambda: self._search_focus(),

            ("S",): lambda: self._save(),
            ("Z",): lambda: self._history_shift(event, False),

            ("Shift", "Z"): lambda: self._history_shift(event, True),
            ("Y",): lambda: self._history_shift(event, True)
        }

        if key not in key_to_callback:
            return

        key_to_callback[key]()

    def _center_window(self):
        x = (self.winfo_screenwidth() // 2) - (RC_WIN_SIZE[0] // 2)
        y = (self.winfo_screenheight() // 2) - (RC_WIN_SIZE[1] // 2)

        self.geometry(f"{RC_WIN_SIZE[0]}x{RC_WIN_SIZE[1]}+{x}+{y}")

    def _create_widgets(self):
        self._tabs = SettingsTabs(self)
        self._tooltip = Tooltip(self, text=self._tabs.get_default_tooltip())
        self._actions = SettingsActions(self)

    def _save(self):
        result = self._tabs.save_data()
        self._tabs._update_tabs_state()
        self._update_actions_state()
        return result

    def close(self):
        has_error = self._tabs.has_error()

        if self._tabs.has_unsaved_changes():
            if has_error:
                self.to_front()

                message = ("There are errors in the rules, and they can't be saved. "
                           "Do you want to DISCARD them and exit?")
                result = messagebox.askyesno(TITLE_ERROR, message)

                if not result:
                    return False
            else:
                self.to_front()

                message = ("There are unsaved changes. "
                           "Do you want to save them before exiting?")
                result = messagebox.askyesnocancel(APP_TITLE, message)

                if result is None:
                    return False

                if result and not self._save():
                    return False
        else:
            if has_error:
                self.to_front()

                message = (
                    f"There are errors in the rules, and they must be corrected before the application can work properly. "
                    f"Do you still want to close the {SETTINGS_TITLE}?")
                result = messagebox.askyesno(APP_TITLE, message)

                if not result:
                    return False

        self.destroy()
        return True

    def _update_actions_state(self, _=None):
        tabs = self._tabs
        actions = self._actions

        actions.save["state"] = NORMAL if tabs.has_unsaved_changes() and not tabs.has_error() else DISABLED

    def _setup_tooltips(self):
        self._setup_tooltip(self._actions.open_config)
        self._setup_tooltip(self._actions.open_log)
        self._setup_tooltip(self._actions.save)

        tabs = self._tabs
        tabs.bind("<Motion>", self._set_tooltip_by_tab, "+")
        tabs.bind("<Leave>", lambda _: self._tooltip.set(self._tabs.get_default_tooltip()), "+")

        for tab in tabs.frames():
            tab: BaseRulesTab | ProcessesTab
            actions = tab.actions

            if isinstance(tab, BaseRulesTab):
                self._setup_tooltip(actions.add)
                self._setup_tooltip(actions.delete)
                self._setup_tooltip(actions.move_up)
                self._setup_tooltip(actions.move_down)

                rules_list = tab.rules_list
                rules_list.bind("<Motion>", self._set_tooltip_by_tree, "+")
                rules_list.bind(EditableTreeviewEvents.START_EDIT_CELL, self._setup_tooltip_cell_editor, "+")
                rules_list.error_icon_created = lambda icon, tooltip: self._setup_tooltip(icon, tooltip, True, False)
                self._setup_tooltip(rules_list, "", enter=False)

            if isinstance(tab, ProcessesTab):
                self._setup_tooltip(actions.refresh)
                self._setup_tooltip(actions.filterByType)
                self._setup_tooltip(actions.search)

                process_list = tab.process_list
                process_list.bind("<Motion>", self._set_tooltip_by_tree, "+")
                self._setup_tooltip(process_list, "", enter=False)

    def _setup_tooltip(self, widget, text: str = None, error: bool = False, leave: bool = True, enter: bool = True):
        if hasattr(widget, 'description') and text is None:
            text = widget.description

        if text is None:
            raise ValueError("text is None")

        if enter:
            def on_enter(_):
                self._tooltip.set(text, error)

            widget.bind("<Enter>", on_enter, '+')

        if leave:
            def on_leave(_):
                self._tooltip.set(self._tabs.get_default_tooltip())

            widget.bind("<Leave>", on_leave, '+')

    def _set_tooltip_by_tree(self, event):
        if not event or not isinstance(event.widget, ttk.Treeview):
            return

        tab: BaseTab = self._tabs.current_tab()
        treeview = None

        if isinstance(tab, BaseRulesTab):
            treeview = tab.rules_list

        if isinstance(tab, ProcessesTab):
            treeview = tab.process_list

        if treeview is None:
            raise ValueError(type(tab))

        cell = treeview.get_cell_info_by_event(event)

        if cell.region == 'heading' and cell.column_name:
            self._tooltip.set(tab.model.model_fields[cell.column_name].description)
        else:
            self._tooltip.set(self._tabs.get_default_tooltip())

    def _setup_tooltip_cell_editor(self, _=None):
        tab = self._tabs.current_tab()

        if not isinstance(tab, BaseRulesTab):
            return

        rules_list = tab.rules_list
        editor = rules_list.editor()

        if not editor or not editor.cell.column_name:
            return

        self._setup_tooltip(
            rules_list.editor(),
            tab.rule_type.clazz.model_fields[editor.cell.column_name].description,
            leave=False
        )

    def _set_tooltip_by_tab(self, event):
        try:
            tab_index = event.widget.index("@%d,%d" % (event.x, event.y))
        except:
            self._tooltip.set(self._tabs.get_default_tooltip())
            return

        tabs = self._tabs
        tab: BaseRulesTab = tabs.nametowidget(tabs.tabs()[tab_index])
        self._tooltip.set(tab.description())

    def _pack(self):
        self._tooltip.pack(fill=X, expand=False, side=TOP, padx=UI_PADDING, pady=(UI_PADDING, 0))
        self._tabs.pack(fill=BOTH, expand=True, padx=UI_PADDING, pady=UI_PADDING)
        self._actions.pack(fill=X, padx=UI_PADDING, pady=(0, UI_PADDING))

    def _history_shift(self, event, is_redo):
        widget = event.widget
        tab = self._tabs.current_tab()
        history: Optional[HistoryManager] = None

        if isinstance(widget, ExtendedEntry):
            history = widget.history
        elif isinstance(tab, BaseRulesTab):
            history = tab.rules_list.history

        if history is None:
            return

        if is_redo:
            history.redo()
        else:
            history.undo()

    def _add_row(self):
        tab = self._tabs.current_tab()

        if not isinstance(tab, BaseRulesTab):
            return

        if not isinstance(self.focus_get(), RulesList):
            return

        tab.rules_list.add_row()

    def _search_focus(self):
        tab = self._tabs.current_tab()

        if not isinstance(tab, ProcessesTab):
            return

        tab.actions.search.focus_set()

    def to_front(self):
        self.deiconify()
        self.lift()
        self.attributes('-topmost', True)
        self.after_idle(self.attributes, '-topmost', False)


__app: Optional[Settings] = None


def open_settings():
    global __app

    if __app is not None:
        __app.after_idle(__app.to_front)
        return

    def settings():
        try:
            global __app

            try:
                __app = Settings()
                __app.after_idle(__app.to_front)
                __app.mainloop()
            finally:
                __app = None
        except:
            LOG.exception(f"An unexpected error occurred in the {SETTINGS_TITLE} of {APP_NAME}.")
            show_settings_error_message()

    TaskScheduler.schedule_task(THREAD_SETTINGS, settings)


def is_opened_settings() -> bool:
    global __app
    return __app is not None


def get_settings() -> Settings:
    global __app
    return __app


def show_settings_error_message():
    message = (
        f"An error has occurred in the {SETTINGS_TITLE} of {APP_NAME}.\n"
        f"To troubleshoot, please check the log file `{LOG_FILE_NAME}` for details.\n\n"
        f"Would you like to open the log file?"
    )

    if yesno_error_box(message):
        os.startfile(LOG_FILE_NAME)


if __name__ == "__main__":
    run_all_migration()
    test_app = Settings()
    test_app.mainloop()
