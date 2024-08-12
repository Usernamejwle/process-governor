import os
import tkinter as tk
from threading import Thread
from tkinter import messagebox, ttk

from constants.app_info import APP_NAME_WITH_VERSION, APP_NAME
from constants.files import LOG_FILE_NAME
from constants.log import LOG
from constants.resources import APP_ICON
from constants.ui import UI_PADDING, RC_WIN_SIZE, ActionEvents, SETTINGS_TITLE, RulesListEvents, EditableTreeviewEvents
from ui.widget.common.button import IconedButton
from ui.widget.settings.settings_tabs import SettingsTabs
from ui.widget.settings.tabs.rules.base_rules_tab import BaseRulesTab
from ui.widget.settings.tooltip import Tooltip
from util.messages import yesno_error_box
from util.ui import icon16px


class SettingsButtons(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup_btn()

    def _setup_btn(self):
        self.save = save = IconedButton(
            self,
            text=" Apply",
            command=lambda: self.event_generate(ActionEvents.SAVE),
            image=icon16px("check", fill="cornflowerblue")
        )
        right_btn_pack = dict(side=tk.RIGHT, padx=(UI_PADDING, 0))
        save.pack(**right_btn_pack)


class Settings(tk.Tk):
    _DEFAULT_TOOLTIP = (
        "To add a new rule, click the **Add** button.\n"
        "To edit a rule, **double-click** on the corresponding cell."
    )

    _tabs = None
    _tooltip = None
    _buttons = None

    def __init__(self):
        super().__init__()
        self._setup_window()
        self._create_widgets()
        self._setup_tooltips()

    def _setup_window(self):
        self._center_window()

        self.protocol("WM_DELETE_WINDOW", self._on_window_closing)
        self.iconbitmap(APP_ICON)
        self.title(f"{SETTINGS_TITLE} - {APP_NAME_WITH_VERSION}")
        self.minsize(*RC_WIN_SIZE)

        self.bind_all("<Key>", self._on_key_release, "+")

    @staticmethod
    def _on_key_release(event):
        ctrl = (event.state & 0x4) != 0

        if event.keycode == ord('X') and ctrl and event.keysym.lower() != "x":
            event.widget.event_generate("<<Cut>>")

        if event.keycode == ord('V') and ctrl and event.keysym.lower() != "v":
            event.widget.event_generate("<<Paste>>")

        if event.keycode == ord('C') and ctrl and event.keysym.lower() != "c":
            event.widget.event_generate("<<Copy>>")

        if event.keycode == ord('A') and ctrl and event.keysym.lower() != "c":
            event.widget.event_generate("<<SelectAll>>")

    def _center_window(self):
        x = (self.winfo_screenwidth() // 2) - (RC_WIN_SIZE[0] // 2)
        y = (self.winfo_screenheight() // 2) - (RC_WIN_SIZE[1] // 2)

        self.geometry(f"{RC_WIN_SIZE[0]}x{RC_WIN_SIZE[1]}+{x}+{y}")

    def _create_widgets(self):
        self._create_tooltips()
        self._create_tabs()
        self._create_buttons()

    def _create_tooltips(self):
        self._tooltip = Tooltip(self, text=self._DEFAULT_TOOLTIP)
        self._tooltip.pack(fill=tk.X, expand=False, side=tk.TOP, padx=UI_PADDING, pady=(UI_PADDING, 0))

    def _create_tabs(self):
        self._tabs = tabs = SettingsTabs(self)
        tabs.load_data()
        tabs.bind(RulesListEvents.UNSAVED_CHANGES_STATE, lambda _: self._update_buttons_state(), "+")
        tabs.pack(fill=tk.BOTH, expand=True, padx=UI_PADDING, pady=UI_PADDING)

    def _create_buttons(self):
        self._buttons = buttons = SettingsButtons(self)

        buttons.pack(fill=tk.X, padx=UI_PADDING, pady=(0, UI_PADDING))
        buttons.bind(ActionEvents.SAVE, lambda _: self._tabs.save_data(), "+")

        self._update_buttons_state()

    def _on_window_closing(self):
        has_error = self._tabs.has_error()

        if self._tabs.has_unsaved_changes():
            if has_error:
                message = ("There are errors in the rules, and they can't be saved. "
                           "Do you want to DISCARD them and exit?")
                result = messagebox.askyesno(f"{SETTINGS_TITLE} - {APP_NAME_WITH_VERSION}", message)

                if not result:
                    return
            else:
                message = ("There are unsaved changes. "
                           "Do you want to save them before exiting?")
                result = messagebox.askyesnocancel(f"{SETTINGS_TITLE} - {APP_NAME_WITH_VERSION}", message)

                if result is None:
                    return

                if result and not self._tabs.save_data():
                    return
        else:
            if has_error:
                message = (
                    f"There are errors in the rules, and they must be corrected before the application can work properly. "
                    f"Do you still want to close the {SETTINGS_TITLE}?")
                result = messagebox.askyesno(f"{SETTINGS_TITLE} - {APP_NAME_WITH_VERSION}", message)

                if not result:
                    return

        self.destroy()

    def _update_buttons_state(self, _=None):
        tabs = self._tabs
        buttons = self._buttons

        buttons.save["state"] = tk.NORMAL if tabs.has_unsaved_changes() and not tabs.has_error() else tk.DISABLED

    def _setup_tooltips(self):
        self._setup_tooltip(self._buttons.save, "__Adds__ a rule after the current")

        tabs = self._tabs
        tabs.bind("<Motion>", self._set_tooltip_by_tab, "+")
        tabs.bind("<Leave>", lambda _: self._tooltip.set(self._DEFAULT_TOOLTIP), "+")

        for tab in tabs.frames():
            btns = tab.buttons
            self._setup_tooltip(btns.add, "__Adds__ a rule after the current")
            self._setup_tooltip(btns.delete, "__Deletes__ the selected rules")
            self._setup_tooltip(btns.move_up, "__Moves__ the current rule __up__")
            self._setup_tooltip(btns.move_down, "__Moves__ the current rule __down__")

            rules_list = tab.rules_list
            rules_list.bind("<Motion>", self._set_tooltip_by_tree, "+")
            rules_list.bind(EditableTreeviewEvents.START_EDIT_CELL, self._setup_tooltip_cell_editor, "+")
            rules_list.error_icon_created = lambda icon, tooltip: self._setup_tooltip(icon, tooltip, True, False)
            self._setup_tooltip(rules_list, "", enter=False)

    def _setup_tooltip(self, widget, text: str, error: bool = False, leave: bool = True, enter: bool = True):
        if enter:
            def on_enter(_):
                self._tooltip.set(text, error)

            widget.bind("<Enter>", on_enter)

        if leave:
            def on_leave(_):
                self._tooltip.set(self._DEFAULT_TOOLTIP)

            widget.bind("<Leave>", on_leave)

    def _set_tooltip_by_tree(self, event):
        if not event or not isinstance(event.widget, ttk.Treeview):
            return

        tab = self._tabs.current_tab()
        cell = tab.rules_list.get_cell_info(event)

        if cell:
            self._tooltip.set(tab.rule_type.clazz.model_fields[cell.column_name].description)

    def _setup_tooltip_cell_editor(self, _=None):
        tab = self._tabs.current_tab()
        rules_list = tab.rules_list
        cell = rules_list.current_cell()

        if not cell:
            return

        self._setup_tooltip(
            rules_list.popup(),
            tab.rule_type.clazz.model_fields[cell.column_name].description,
            leave=False
        )

    def _set_tooltip_by_tab(self, event):
        try:
            tab_index = event.widget.index("@%d,%d" % (event.x, event.y))
        except:
            self._tooltip.set(self._DEFAULT_TOOLTIP)
            return

        tabs = self._tabs
        tab: BaseRulesTab = tabs.nametowidget(tabs.tabs()[tab_index])
        self._tooltip.set(tab.description())


is_settings_open = False


def open_settings():
    global is_settings_open

    def settings():
        global is_settings_open
        try:
            is_settings_open = True

            app = Settings()
            app.mainloop()
        except:
            LOG.exception(f"An unexpected error occurred in the {SETTINGS_TITLE} of {APP_NAME}.")
            show_settings_error_message()
        finally:
            is_settings_open = False

    if not is_settings_open:
        thread = Thread(target=settings)
        thread.start()


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
