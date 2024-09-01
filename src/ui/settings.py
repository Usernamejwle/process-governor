import os
from tkinter import messagebox, ttk, Tk, X, TOP, BOTH, NORMAL, DISABLED

from constants.app_info import APP_NAME_WITH_VERSION, APP_NAME
from constants.files import LOG_FILE_NAME
from constants.log import LOG
from constants.resources import APP_ICON, UI_SAVE, UI_LOG, UI_CONFIG
from constants.threads import THREAD_SETTINGS
from constants.ui import UI_PADDING, RC_WIN_SIZE, ActionEvents, SETTINGS_TITLE, EditableTreeviewEvents, \
    RIGHT_PACK, LEFT_PACK, OPEN_CONFIG_LABEL, OPEN_LOG_LABEL, ExtendedTreeviewEvents
from ui.widget.common.button import ExtendedButton
from ui.widget.settings.settings_tabs import SettingsTabs
from ui.widget.settings.tabs.base_tab import BaseTab
from ui.widget.settings.tabs.process_list import ProcessListTab
from ui.widget.settings.tabs.rules.base_rules_tab import BaseRulesTab
from ui.widget.settings.tooltip import Tooltip
from util.files import open_config_file, open_log_file
from util.messages import yesno_error_box
from util.scheduler import TaskScheduler
from util.ui import load_img


class Settings(Tk):
    def __init__(self):
        super().__init__()

        self._tabs: SettingsTabs
        self._tooltip: Tooltip
        self._actions: SettingsActions

        self._setup_window()
        self._create_widgets()
        self._pack()
        self._setup_tooltips()

    def _setup_window(self):
        self._center_window()

        self.protocol("WM_DELETE_WINDOW", self._on_window_closing)
        self.iconbitmap(APP_ICON)
        self.title(APP_NAME_WITH_VERSION)
        self.minsize(*RC_WIN_SIZE)

        self.bind_all("<Key>", self._on_key_release, "+")

    def _on_key_release(self, event):
        ctrl = (event.state & 0x4) != 0
        shift = (event.state & 0x1) != 0

        keycode = event.keycode
        widget = event.widget
        keysym = event.keysym.upper()

        key_actions = {
            ord('X'): "<<Cut>>",
            ord('V'): "<<Paste>>",
            ord('C'): "<<Copy>>",
            ord('A'): "<<SelectAll>>",
            # ord('Z'): "<<Undo>>" if not shift else "<<Redo>>",
            # ord('Y'): "<<Redo>>",
        }

        if ctrl and keycode in key_actions and keysym == '??':
            self.after(0, lambda: widget.event_generate(key_actions[keycode]))
            # return 'break'

    def _center_window(self):
        x = (self.winfo_screenwidth() // 2) - (RC_WIN_SIZE[0] // 2)
        y = (self.winfo_screenheight() // 2) - (RC_WIN_SIZE[1] // 2)

        self.geometry(f"{RC_WIN_SIZE[0]}x{RC_WIN_SIZE[1]}+{x}+{y}")

    def _create_widgets(self):
        self._create_tabs()
        self._create_tooltips()
        self._create_actions()

    def _create_tooltips(self):
        self._tooltip = Tooltip(self, text=self._tabs.get_default_tooltip())

    def _create_tabs(self):
        self._tabs = tabs = SettingsTabs(self)
        tabs.load_data()
        tabs.bind(ExtendedTreeviewEvents.CHANGE, lambda _: self._update_actions_state(), "+")

    def _create_actions(self):
        self._actions = actions = SettingsActions(self)

        actions.bind(ActionEvents.APPLY, lambda _: self._tabs.save_data(), "+")
        actions.bind(ActionEvents.APPLY_N_CLOSE, lambda _: self._apply_and_save(), "+")
        actions.bind(ActionEvents.CONFIG, lambda _: open_config_file(), "+")
        actions.bind(ActionEvents.LOG, lambda _: open_log_file(), "+")

        self._update_actions_state()

    def _apply_and_save(self):
        self._tabs.save_data()
        self._on_window_closing()

    def _on_window_closing(self):
        has_error = self._tabs.has_error()

        if self._tabs.has_unsaved_changes():
            if has_error:
                message = ("There are errors in the rules, and they can't be saved. "
                           "Do you want to DISCARD them and exit?")
                result = messagebox.askyesno(f"{APP_NAME_WITH_VERSION}", message)

                if not result:
                    return
            else:
                message = ("There are unsaved changes. "
                           "Do you want to save them before exiting?")
                result = messagebox.askyesnocancel(f"{APP_NAME_WITH_VERSION}", message)

                if result is None:
                    return

                if result and not self._tabs.save_data():
                    return
        else:
            if has_error:
                message = (
                    f"There are errors in the rules, and they must be corrected before the application can work properly. "
                    f"Do you still want to close the {SETTINGS_TITLE}?")
                result = messagebox.askyesno(f"{APP_NAME_WITH_VERSION}", message)

                if not result:
                    return

        self.destroy()

    def _update_actions_state(self, _=None):
        tabs = self._tabs
        actions = self._actions

        actions.apply["state"] = NORMAL if tabs.has_unsaved_changes() and not tabs.has_error() else DISABLED
        actions.apply_n_close["state"] = actions.apply["state"]

    def _setup_tooltips(self):
        self._setup_tooltip(self._actions.open_config)
        self._setup_tooltip(self._actions.open_log)
        self._setup_tooltip(self._actions.apply)
        self._setup_tooltip(self._actions.apply_n_close)

        tabs = self._tabs
        tabs.bind("<Motion>", self._set_tooltip_by_tab, "+")
        tabs.bind("<Leave>", lambda _: self._tooltip.set(self._tabs.get_default_tooltip()), "+")

        for tab in tabs.frames():
            tab: BaseRulesTab | ProcessListTab
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

            if isinstance(tab, ProcessListTab):
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

        if isinstance(tab, ProcessListTab):
            treeview = tab.process_list

        if treeview is None:
            raise ValueError(type(tab))

        cell = treeview.get_cell_info_by_event(event)

        if cell.region == 'heading':
            self._tooltip.set(tab.model.model_fields[cell.column_name].description)
        else:
            self._tooltip.set(self._tabs.get_default_tooltip())

    def _setup_tooltip_cell_editor(self, _=None):
        tab = self._tabs.current_tab()

        if not isinstance(tab, BaseRulesTab):
            return

        rules_list = tab.rules_list
        editor = rules_list.editor()

        if not editor:
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


class SettingsActions(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup_btn()

    def _setup_btn(self):
        self.open_config = open_config = ExtendedButton(
            self,
            text=f"{OPEN_CONFIG_LABEL}",
            event=ActionEvents.CONFIG,
            image=load_img(file=UI_CONFIG),
            description="**Opens** the __config file__."
        )

        self.open_log = open_log = ExtendedButton(
            self,
            text=f"{OPEN_LOG_LABEL}",
            event=ActionEvents.LOG,
            image=load_img(file=UI_LOG),
            description="**Opens** the __log file__."
        )

        self.apply = apply = ExtendedButton(
            self,
            text="Apply",
            event=ActionEvents.APPLY,
            image=load_img(file=UI_SAVE),
            description="**Applies** the __settings__."
        )

        self.apply_n_close = apply_n_close = ExtendedButton(
            self,
            text="Apply & Close",
            event=ActionEvents.APPLY_N_CLOSE,
            image=load_img(file=UI_SAVE),
            description="**Applies and Сloses** the __settings__."
        )

        open_config.pack(**LEFT_PACK)
        open_log.pack(**LEFT_PACK)
        apply_n_close.pack(**RIGHT_PACK)
        apply.pack(**RIGHT_PACK)


def open_settings():
    def settings():
        try:
            app = Settings()
            app.mainloop()
        except:
            LOG.exception(f"An unexpected error occurred in the {SETTINGS_TITLE} of {APP_NAME}.")
            show_settings_error_message()

    TaskScheduler.schedule_task(THREAD_SETTINGS, settings)


def show_settings_error_message():
    title = f"Error Detected - {APP_NAME_WITH_VERSION}"
    message = (
        f"An error has occurred in the {SETTINGS_TITLE} of {APP_NAME}.\n"
        f"To troubleshoot, please check the log file `{LOG_FILE_NAME}` for details.\n\n"
        f"Would you like to open the log file?"
    )

    if yesno_error_box(title, message):
        os.startfile(LOG_FILE_NAME)


if __name__ == "__main__":
    test_app = Settings()
    test_app.mainloop()
