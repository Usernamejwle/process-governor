import tkinter as tk
import traceback
from dataclasses import dataclass
from tkinter import ttk
from typing import Optional, Literal, List

from constants.ui import EditableTreeviewEvents, ScrollableTreeviewEvents
from ui.widget.common.treeview.scrollable import ScrollableTreeview
from util.ui import full_visible_bbox

ColumnType = Literal["text", "list"]


@dataclass(frozen=True)
class CellInfo:
    column_id: str
    row_id: str
    column_name: str
    value: str
    values: List[str]
    type: ColumnType


class CellEditor:
    def __init__(
            self,
            master,
            cell_info: CellInfo,
            *args,
            **kwargs
    ):
        self._cell = cell_info
        self._input = self._setup_widgets(master, *args, **kwargs)

    def _setup_widgets(self, master, *args, **kwargs):
        def on_change(_):
            self.event_generate(EditableTreeviewEvents.SAVE_CELL)

        def on_escape(_):
            self.event_generate(EditableTreeviewEvents.ESCAPE)

        if self._cell.type == "text":
            entry_popup = ttk.Entry(master, *args, justify='center', **kwargs)
            entry_popup.insert(0, self._cell.value)
            entry_popup.select_range(0, tk.END)
            entry_popup.bind("<FocusOut>", on_change, '+')
        else:
            entry_popup = ttk.Combobox(
                master,
                *args,
                values=self._cell.values,
                justify='center',
                state="readonly",
                **kwargs
            )
            entry_popup.set(self._cell.value)
            entry_popup.bind("<<ComboboxSelected>>", on_change, '+')

        entry_popup.bind("<Return>", on_change, '+')
        entry_popup.bind("<Escape>", on_escape, '+')
        entry_popup.pack(fill=tk.BOTH)
        entry_popup.focus_force()

        return entry_popup

    def get(self):
        return self._input.get().strip()

    def __getattr__(self, name):
        return getattr(self._input, name)


class EditableTreeview(ScrollableTreeview):
    _types: dict[str, ColumnType] = {}
    _values: dict[str, List[str]] = {}
    _popup: Optional[CellEditor] = None
    _cell: Optional[CellInfo] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bind("<Button-1>", self._save_and_destroy_popup, '+')
        self.bind("<Double-1>", self._on_dbl_click, '+')
        self.bind(ScrollableTreeviewEvents.SCROLL, self._place_popup, '+')
        self.bind("<Configure>", lambda _: self.after(1, self._place_popup), '+')

    def insert(self, parent, index, iid=None, **kw):
        result = super().insert(parent, index, iid, **kw)
        self.event_generate(EditableTreeviewEvents.CHANGE)
        return result

    def delete(self, *args):
        result = super().delete(*args)
        self.event_generate(EditableTreeviewEvents.CHANGE)
        return result

    def set(self, item, column=None, value=None):
        result = super().set(item, column, value)

        if value is not None:
            self.event_generate(EditableTreeviewEvents.CHANGE)

        return result

    def move(self, item, parent, index):
        result = super().move(item, parent, index)
        self.event_generate(EditableTreeviewEvents.CHANGE)
        return result

    def column_type(self, column: str, ctype: ColumnType):
        self._types[column] = ctype

    def column_values(self, column: str, values: List[str]):
        self._values[column] = values

    def get_cell_info(self, event):
        row_id, column_id = self.identify_row(event.y), self.identify_column(event.x)
        return self._get_cell_info(row_id, column_id)

    def _get_cell_info(self, row_id, column_id):
        if not row_id or not column_id or column_id == "#0":
            return None

        column_name = self.column(column_id)["id"]
        cell_value = self.set(row_id, column_id)
        values = self._values.get(column_name, [])
        cell_type = self._types.get(column_name, "text")

        return CellInfo(
            column_id,
            row_id,
            column_name,
            cell_value,
            values,
            cell_type
        )

    def current_cell(self):
        return self._cell

    def popup(self):
        return self._popup

    def _on_dbl_click(self, event):
        self._destroy_editor()
        self._cell = self.get_cell_info(event)
        self._create_editor()

    def _create_editor(self):
        if not self._cell:
            return

        self._popup = entry_popup = CellEditor(self, self._cell)

        entry_popup.bind(EditableTreeviewEvents.SAVE_CELL, self._save_and_destroy_popup, '+')
        entry_popup.bind(EditableTreeviewEvents.ESCAPE, self._destroy_editor, '+')
        entry_popup.bind("<Destroy>", self._on_popup_destroy, '+')

        self._place_popup()
        self.event_generate(EditableTreeviewEvents.START_EDIT_CELL)

    def _place_popup(self, _=None):
        if not self._popup:
            return

        bbox = full_visible_bbox(self, self._cell.row_id, self._cell.column_id)

        if bbox:
            x, y, width, height = bbox
            self._popup.place(x=x, y=y, width=width, height=height)
        else:
            self._popup.place_forget()

    def _save_and_destroy_popup(self, _=None):
        if self._popup:
            self._save_cell_changes()
            self._destroy_editor()

    def _destroy_editor(self, _=None):
        if self._popup:
            print("sadfsdfasdfsd")
            traceback.print_stack()
            self._popup.destroy()

    def _save_cell_changes(self):
        new_value = self._popup.get()

        if self._cell.value != new_value:
            self.set(self._cell.row_id, self._cell.column_id, new_value)

    def _on_popup_destroy(self, _=None):
        self._popup = None
        self._cell = None

    def edit_cell(self, row_id, column_id):
        self._destroy_editor()
        self._cell = self._get_cell_info(row_id, column_id)
        self._create_editor()

    def select_all_rows(self):
        items = self.get_children()

        if items:
            self.selection_set(items)

    def move_rows_up(self):
        selected_items = self.selection()

        if selected_items:
            for selected_item in selected_items:
                index = self.index(selected_item)
                next_index = index - 1

                if index <= 0:
                    break

                self.move(selected_item, '', next_index)

            self.selection_set(selected_items)

    def move_rows_down(self):
        selected_items = self.selection()
        count_items = len(self.get_children())

        if selected_items:
            for selected_item in reversed(selected_items):
                index = self.index(selected_item)
                next_index = index + 1

                if next_index >= count_items:
                    break

                self.move(selected_item, '', next_index)

            self.selection_set(selected_items)

    def add_row(self, values=[]):
        selected_items = self.selection()

        if selected_items:
            selected_item = selected_items[-1]
            index = self.index(selected_item)

            self.insert('', index + 1, values=values)
            self.selection_set(self.get_children()[index + 1])
        else:
            self.insert('', tk.END, values=values)

    def delete_selected_rows(self):
        selected_items = self.selection()

        if selected_items:
            index = self.index(selected_items[0])

            for item in selected_items:
                self.delete(item)

            children = self.get_children()

            if len(children) <= index:
                index -= 1

            if children and len(children) > index:
                self.selection_set(children[index])
