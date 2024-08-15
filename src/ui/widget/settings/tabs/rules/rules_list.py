import enum
import json
import tkinter as tk
from enum import Enum
from tkinter import ttk, PhotoImage
from tkinter.font import Font
from typing import Optional, Any, List

from pydantic import ValidationError, BaseModel

from constants.resources import UI_ERROR
from constants.ui import ERROR_ROW_COLOR, RulesListEvents, EditableTreeviewEvents, \
    ScrollableTreeviewEvents
from ui.widget.common.label import Image
from ui.widget.common.treeview.editable import EditableTreeview
from util.ui import full_visible_bbox
from util.utils import extract_type, is_optional_type


class RulesList(EditableTreeview):
    def __init__(self, model: BaseModel, *args, **kwargs):
        self.has_unsaved_changes = False

        self._model = model
        self._error_icons: dict[tuple[str, str], Image] = {}

        super().__init__(*args, columns=list(self._model.model_fields.keys()), **kwargs, show='headings')
        self._setup_look()

        self.bind(EditableTreeviewEvents.CHANGE, lambda _: self._changed(), '+')
        self.bind(ScrollableTreeviewEvents.SCROLL, self._place_icons, '+')
        self.bind("<Button-1>", self._handle_click, '+')
        self.bind("<Double-1>", self._handle_click, '+')
        self.bind("<Configure>", lambda _: self.after(1, self._place_icons), '+')
        self.bind("<Control-Key>", self._on_key_press_tree, "+")
        self.bind("<Delete>", lambda _: self.delete_selected_rows(), "+")

        self._setup_columns()

    def _handle_click(self, event):
        row_id = self.identify_row(event.y)
        region = self.identify_region(event.x, event.y)

        if region == "separator" and not row_id:
            return "break"

    def _setup_columns(self):
        model_fields = self._model.model_fields

        for column_name in self["columns"]:
            field_info = model_fields.get(column_name)

            if field_info:
                title = field_info.title
                max_width_value_in_column = title
                typ = extract_type(field_info.annotation)
                values = []

                if is_optional_type(field_info.annotation):
                    values.append("")

                if issubclass(typ, enum.Enum):
                    values += [str(e) for e in typ]
                    max_width_value_in_column = max(values + [max_width_value_in_column], key=len)

                    self.column_type(column_name, "list")
                    self.column_values(column_name, values)
            else:
                title = "?"
                max_width_value_in_column = title

            extra = field_info.json_schema_extra or dict() if field_info else dict()
            stretch = extra.get('stretchable_column_ui', False)
            width = extra.get(
                'width_ui',
                int(self.font.measure(max_width_value_in_column) * 1.35)
                if title else None
            )
            width = width * extra.get('scale_width_ui', 1) if width else None
            anchor = {"left": "w", "center": "center", "right": "e"}[extra.get('justify_ui', 'center')]

            self.heading(column_name, text=title)
            self.column(column_name, anchor=anchor, width=width, minwidth=width, stretch=stretch)

    def _setup_look(self):
        self.font = Font(family="TkDefaultFont")
        self.tag_configure("error", background=ERROR_ROW_COLOR)

        row_height = self.font.metrics("linespace") + 10
        style = ttk.Style()
        style.configure('Treeview', rowheight=row_height)

        self._error_icon = PhotoImage(file=UI_ERROR)

    def set_data(self, rules_raw: List[dict]):
        self.delete(*self.get_children())
        fields = self["columns"]

        for rule in rules_raw:
            values = [rule.get(field_name, '') or '' for field_name in fields]
            self.insert('', tk.END, values=values)

        self.set_unsaved_changes(False)

    def get_data(self) -> List[dict]:
        return [self._to_rule_raw(row_id) for row_id in self.get_children()]

    def _to_rule_raw(self, row_id):
        keys = self["columns"]
        values = self.item(row_id, 'values')
        return {
            key: value for key, value in zip(keys, values)
            if value and value.strip()
        }

    def get_error_if_available(self, row_id) -> Optional[tuple[Any, Any]]:
        try:
            # noinspection PyCallingNonCallable
            self._model(**self._to_rule_raw(row_id))
            return None
        except ValidationError as e:
            return row_id, json.loads(e.json())

    def _errors(self) -> dict[Any, Any]:
        errors = [
            self.get_error_if_available(row_id)
            for row_id in self.get_children()
        ]

        return {
            error[0]: error[1]
            for error in errors
            if error is not None
        }

    def has_error(self):
        return len(self._errors()) > 0

    def set_unsaved_changes(self, state: bool):
        self.has_unsaved_changes = state
        self.event_generate(RulesListEvents.UNSAVED_CHANGES_STATE)

    def _changed(self):
        self.set_unsaved_changes(True)
        self._handle_errors()

    def _handle_errors(self):
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
                image=self._error_icon,
                background=ERROR_ROW_COLOR,
                cursor="hand2"
            )
            icon.bind("<Double-1>", lambda _: self.edit_cell(row_id, column_id), "+")
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
            kwargs["image"] = self._error_icon
        else:
            kwargs["tags"] = ("",)

        self.item(row_id, **kwargs)

    def error_icon_created(self, icon, tooltip):
        pass

    def _on_key_press_tree(self, event):
        ctrl = (event.state & 0x4) != 0

        if ctrl and event.keycode == ord('A'):
            self.select_all_rows()

    def _get_default_values(self) -> List[Any]:
        result = []
        model_fields = self._model.model_fields

        for column_name in self["columns"]:
            field_info = model_fields.get(column_name)
            default_value = field_info.default

            if isinstance(default_value, Enum):
                default_value = str(default_value)

            result.append(default_value or '')

        return result

    def add_row(self, values=[]):
        if not values:
            values = self._get_default_values()
        super().add_row(values)
