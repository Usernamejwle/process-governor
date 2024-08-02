import enum
import json
import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
from typing import Optional, Any, List

from psutil._pswindows import Priority
from pydantic import ValidationError, BaseModel

from configuration.rule import ServiceRule, ProcessRule
from constants.any import BOTH_SELECTORS_SET
from constants.priority_mappings import str_to_priority, str_to_iopriority
from constants.ui import ERROR_COLOR, ERROR_ROW_COLOR, RulesListEvents, EditableTreeviewEvents, \
    ScrollableTreeviewEvents
from ui.widget.common.label import Image
from ui.widget.common.treeview.editable import EditableTreeview
from util.ui import icon16px, full_visible_bbox
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
                    values += list(str_to_priority.keys() if typ == Priority else str_to_iopriority.keys())
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
                int(self.font.measure(max_width_value_in_column) * 1.5)
                if title else None
            )
            width = width * extra.get('scale_width_ui', 1) if width else None

            self.heading(column_name, text=title)
            self.column(column_name, anchor='center', width=width, minwidth=width, stretch=stretch)

    def _setup_look(self):
        self.font = Font(family="TkDefaultFont")
        self.tag_configure("error", background=ERROR_ROW_COLOR)

        row_height = self.font.metrics("linespace") + 10
        style = ttk.Style()
        style.configure('Treeview', rowheight=row_height)

        self._error_icon = icon16px("exclamation-triangle", ERROR_COLOR)

    def set_raw_data(self, rules_raw: List[Any]):
        self.delete(*self.get_children())
        fields = self["columns"]

        for rule in rules_raw:
            values = [rule.get(field_name, '') or '' for field_name in fields]
            self.insert('', tk.END, values=values)

        self.set_unsaved_changes(False)

    def get_data(self) -> List[Optional[ProcessRule | ServiceRule | tuple[Any, Any]]]:
        return self._to_rules()

    def _to_rule(self, row_id) -> ProcessRule | ServiceRule | tuple[Any, Any]:
        keys = self["columns"]
        values = self.item(row_id, 'values')
        dct = {
            key: value for key, value in zip(keys, values)
            if value and value.strip()
        }

        try:
            # noinspection PyCallingNonCallable
            return self._model(**dct)
        except ValidationError as e:
            return row_id, json.loads(e.json())

    def _to_rules(self) -> List[Optional[ProcessRule | ServiceRule | tuple[Any, Any]]]:
        return [self._to_rule(row_id) for row_id in self.get_children()]

    def _errors(self) -> dict[Any, Any]:
        return {rule[0]: rule[1] for rule in self._to_rules() if
                rule and not isinstance(rule, (ProcessRule, ServiceRule))}

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
                    if column_error["type"] == BOTH_SELECTORS_SET:
                        columns = ["processSelector", "serviceSelector"]
                    else:
                        columns = column_error["loc"]

                    for column in columns:
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
            extra = field_info.json_schema_extra or dict() if field_info else dict()
            default_value = extra.get('default_ui', '')
            result.append(default_value)

        return result

    def add_row(self, values=[]):
        if not values:
            values = self._get_default_values()
        super().add_row(values)
