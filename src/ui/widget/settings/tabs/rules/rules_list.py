from tkinter import Menu, LEFT
from typing import Any

from pydantic import BaseModel
from pydantic.config import JsonDict

from constants.resources import UI_ERROR, UI_DELETE, UI_REDO, UI_UNDO, UI_SELECT_ALL, UI_ADD
from constants.ui import ERROR_ROW_COLOR, ScrollableTreeviewEvents, ExtendedTreeviewEvents
from ui.widget.common.label import Image
from ui.widget.common.treeview.editable import EditableTreeview
from ui.widget.common.treeview.pydantic import PydanticTreeviewLoader
from util.ui import full_visible_bbox, load_img


class RulesList(EditableTreeview):
    def __init__(self, model: type[BaseModel], *args, **kwargs):
        super().__init__(
            *args,
            **kwargs,
            show='headings',
            columns=list(model.model_fields.keys()),
            hand_on_title=True
        )

        self._loader = PydanticTreeviewLoader(self, model)
        self._error_icons: dict[tuple[str, str], Image] = {}

        self.tag_configure("error", background=ERROR_ROW_COLOR)

        self.bind(ExtendedTreeviewEvents.CHANGE, lambda _: self._check_errors(), '+')
        self.bind(ScrollableTreeviewEvents.SCROLL, self._place_icons, '+')
        self.bind("<Configure>", lambda _: self.after(1, self._place_icons), '+')

        self._setup_context_menu()

    def _setup_context_menu(self):
        history = self.history

        self._context_menu_icons = icons = {
            'del': load_img(UI_DELETE),
            'undo': load_img(UI_UNDO),
            'redo': load_img(UI_REDO),
            'select_all': load_img(UI_SELECT_ALL),
            'add': load_img(UI_ADD),
        }
        self._context_menu = menu = Menu(self, tearoff=0)

        menu.add_command(
            label="  Undo",
            command=history.undo,
            image=icons['undo'],
            compound=LEFT,
            accelerator="Ctrl+Z"
        )
        menu.add_command(
            label="  Redo",
            command=history.redo,
            image=icons['redo'],
            compound=LEFT,
            accelerator="Ctrl+Shift+Z"
        )
        menu.add_separator()
        menu.add_command(
            label="  Add",
            command=self.add_row,
            image=icons['add'],
            compound=LEFT,
            accelerator="Ctrl+D"
        )
        menu.add_command(
            label="  Select all",
            command=self.select_all_rows,
            image=icons['select_all'],
            compound=LEFT,
            accelerator="Ctrl+A"
        )
        menu.add_command(
            label="  Delete",
            command=self.delete_selected_rows,
            image=icons['del'],
            compound=LEFT,
            accelerator="Del"
        )

        self.bind("<Button-3>", self._show_context_menu, '+')

    def _show_context_menu(self, event):
        context_menu = self._context_menu
        process_list = self
        row_id = process_list.identify_row(event.y)
        selected_items = process_list.selection()

        if row_id:
            if selected_items and len(selected_items) == 1:
                process_list.selection_set(row_id)
            context_menu.post(event.x_root, event.y_root)

    def _errors(self) -> dict[Any, Any]:
        errors = [
            self._loader.get_error_if_available(row_id)
            for row_id in self.get_children()
        ]

        return {
            error[0]: error[1]
            for error in errors
            if error is not None
        }

    def has_error(self):
        return len(self._errors()) > 0

    def _check_errors(self):
        self._destroy_error_icons()

        errors = self._errors()
        rows = self.get_children()

        for row_id in rows:
            errors_by_columns = errors.get(row_id)
            self._highlights_error(row_id, bool(errors_by_columns))

            if errors_by_columns:
                for column_error in errors_by_columns:
                    for column in column_error["loc"]:
                        self._place_icon(row_id, column, column_error)

    def _destroy_error_icons(self):
        if self._error_icons:
            for icon in self._error_icons.values():
                icon.destroy()

        self._error_icons = {}

    def _place_icons(self, _=None):
        for key, icon in self._error_icons.items():
            self._place_icon(*key)

    def _place_icon(self, row_id, column_id, column_error=None):
        bbox = full_visible_bbox(self, row_id, column_id)
        key = (row_id, column_id)
        icon = self._error_icons.get(key)

        if not icon:
            self._error_icons[key] = icon = Image(
                self,
                image=load_img(file=UI_ERROR),
                background=ERROR_ROW_COLOR,
                cursor="hand2"
            )
            icon.bind("<Double-1>", lambda _: self.edit_cell(column_id, row_id, 'cell'), "+")
            icon.bind("<Button-1>", lambda _: self.selection_set(row_id), '+')

            user_input = ""

            if isinstance(column_error['input'], str):
                user_input = f"**User Input:** `{column_error['input']}`"

            tooltip = (
                    "The value you entered is __incorrect__. Please check and update it.\n\n"
                    f"**Cause:** {column_error['msg']}.\n"
                    + user_input
            )
            self.error_icon_created(icon, tooltip)

        if bbox:
            x, y, _, height = bbox
            icon.place(x=x, y=y, height=height)
        else:
            icon.place_forget()

    def _highlights_error(self, row_id, has_error: bool):
        kwargs = dict()

        if has_error:
            kwargs["tags"] = ("error",)
        else:
            kwargs["tags"] = ("",)

        self.item(row_id, **kwargs)

    def error_icon_created(self, icon, tooltip):
        pass

    def add_row(self, values=None, index=None):
        if not values:
            values = [*self._loader.get_default_row().values()]
        super().add_row(values, index)

    def set_data(self, rules_raw: list[JsonDict]):
        self._loader.set_data(rules_raw)

    def get_data(self) -> list[JsonDict]:
        return self._loader.get_data()

    def has_changes(self) -> bool:
        return self._loader.has_changes()

    def commit_changes(self):
        self._loader.commit_changes()
