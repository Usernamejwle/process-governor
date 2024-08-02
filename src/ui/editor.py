import os
import tkinter as tk
from threading import Thread
from tkinter import messagebox, ttk

from constants.any import LOG, LOG_FILE_NAME
from constants.app_info import APP_NAME_WITH_VERSION, APP_NAME
from constants.resources import APP_ICON
from constants.ui import UI_PADDING, RC_WIN_SIZE, ActionEvents, RC_TITLE, RulesListEvents, EditableTreeviewEvents
from enums.rules import RuleType
from ui.widget.editor.buttons import EditorButtons
from ui.widget.editor.rules_tab import RulesTabs
from ui.widget.editor.tooltip import Tooltip
from util.messages import yesno_error_box


class RulesConfigurator(tk.Tk):
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

    def _setup_window(self):
        self._center_window()

        self.protocol("WM_DELETE_WINDOW", self._on_window_closing)
        self.iconbitmap(APP_ICON)
        self.title(f"{RC_TITLE} - {APP_NAME_WITH_VERSION}")
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
        self._tooltip = Tooltip(self, text="")
        self._tooltip.pack(fill=tk.X, expand=False, side=tk.TOP, padx=UI_PADDING, pady=(UI_PADDING, 0))

        self._tooltip.set(self._DEFAULT_TOOLTIP)

    def _setup_tooltip(self, widget, text: str, error: bool = False, leave: bool = True, enter: bool = True):
        if enter:
            def on_enter(_):
                self._tooltip.set(text, error)

            widget.bind("<Enter>", on_enter)

        if leave:
            def on_leave(_):
                self._tooltip.set(self._DEFAULT_TOOLTIP)

            widget.bind("<Leave>", on_leave)

    def _create_callback_for_set_tooltip_by_tree(self, rule_type: RuleType):
        def callback(event):
            if not event or not isinstance(event.widget, ttk.Treeview):
                return

            cell = self._tabs.current_list_of_tab().get_cell_info(event)

            if cell:
                self._tooltip.set(rule_type.clazz.model_fields[cell.column_name].description)

        return callback

    def _create_callback_for_setup_tooltip_cell_editor(self, rule_type: RuleType):
        def callback(_=None):
            lst = self._tabs.current_list_of_tab()
            cell = lst.current_cell()

            if cell:
                self._setup_tooltip(
                    lst.popup(),
                    rule_type.clazz.model_fields[cell.column_name].description,
                    leave=False
                )

        return callback

    def _create_tabs(self):
        self._tabs = tabs = RulesTabs(self)

        tabs.pack(fill=tk.BOTH, expand=True, padx=UI_PADDING, pady=UI_PADDING)
        tabs.load_data()

        tabs.bind(RulesListEvents.UNSAVED_CHANGES_STATE, lambda _: self._update_buttons_state(), "+")

        for rt, lst in tabs.list_by_rt().items():
            lst.bind("<Motion>", self._create_callback_for_set_tooltip_by_tree(rt), "+")
            lst.bind(
                EditableTreeviewEvents.START_EDIT_CELL,
                self._create_callback_for_setup_tooltip_cell_editor(rt),
                "+"
            )

            lst.error_icon_created = lambda icon, tooltip: self._setup_tooltip(icon, tooltip, True, False)
            self._setup_tooltip(lst, "", enter=False)

    def _create_buttons(self):
        self._buttons = buttons = EditorButtons(self)

        buttons.pack(fill=tk.X, padx=UI_PADDING, pady=(0, UI_PADDING))
        buttons.bind(ActionEvents.SAVE, lambda _: self._tabs.save_data(), "+")

        self._setup_tooltip(buttons.save, "__Adds__ a rule after the current")

        for rt, btns in self._tabs.buttons_by_rt().items():
            self._setup_tooltip(btns.add, "__Adds__ a rule after the current")
            self._setup_tooltip(btns.delete, "__Deletes__ the selected rules")
            self._setup_tooltip(btns.move_up, "__Moves__ the current rule __up__")
            self._setup_tooltip(btns.move_down, "__Moves__ the current rule __down__")

        self._update_buttons_state()

    def _on_window_closing(self):
        if self._tabs.has_unsaved_changes():
            if self._tabs.has_error():
                message = ("There are errors in the rules, and they can't be saved. "
                           "Do you want to DISCARD them and exit?")
                result = messagebox.askyesno(f"{RC_TITLE} - {APP_NAME_WITH_VERSION}", message)

                if not result:
                    return
            else:
                message = ("There are unsaved changes. "
                           "Do you want to save them before exiting?")
                result = messagebox.askyesnocancel(f"{RC_TITLE} - {APP_NAME_WITH_VERSION}", message)

                if result is None:
                    return

                if result and not self._tabs.save_data():
                    return

        self.destroy()

    def _update_buttons_state(self, _=None):
        tabs = self._tabs
        buttons = self._buttons

        buttons.save["state"] = tk.NORMAL if tabs.has_unsaved_changes() and not tabs.has_error() else tk.DISABLED


is_editor_open = False


def open_rule_editor():
    global is_editor_open

    def editor():
        global is_editor_open
        try:
            is_editor_open = True

            app = RulesConfigurator()
            app.mainloop()
        except:
            LOG.exception(f"An unexpected error occurred in the {RC_TITLE} of {APP_NAME}.")
            show_rule_editor_error_message()
        finally:
            is_editor_open = False

    if not is_editor_open:
        thread = Thread(target=editor)
        thread.start()


def show_rule_editor_error_message():
    title = f"Error Detected - {APP_NAME_WITH_VERSION}"
    message = (
        f"An error has occurred in the {RC_TITLE} of {APP_NAME}.\n"
        f"To troubleshoot, please check the log file `{LOG_FILE_NAME}` for details.\n\n"
        f"Would you like to open the log file?"
    )

    if yesno_error_box(title, message):
        os.startfile(LOG_FILE_NAME)


if __name__ == "__main__":
    test_app = RulesConfigurator()
    test_app.mainloop()
