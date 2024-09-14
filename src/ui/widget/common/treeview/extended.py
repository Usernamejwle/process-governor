from dataclasses import dataclass
from functools import lru_cache
from tkinter import ttk
from typing import Optional, Literal, Any

from pydantic.config import JsonDict

from constants.ui import COLUMN_TITLE_PADDING, ExtendedTreeviewEvents
from util.ui import get_default_font
from util.utils import get_values_from_enum

type RegionType = Literal['heading', 'separator', 'tree', 'cell', 'nothing']


@dataclass(frozen=True)
class CellInfo:
    column_id: Optional[str]
    row_id: Optional[str]
    column_name: Optional[str]
    value: str
    region: RegionType


class ExtendedTreeview(ttk.Treeview):
    def __init__(self, *args, hand_on_title: bool = False, **kwargs):
        super().__init__(*args, **kwargs)

        self._font = get_default_font()
        self._types: dict[str, type] = {}
        self._width_set: dict[str, bool] = {}

        self._stop_event_broadcast: bool = False
        self._changed: tuple = tuple()
        self._before_change_sent: bool = False

        self._setup_font()
        self.bind('<Configure>', self._calculate_columns_width, '+')
        self.bind('<Escape>', lambda _: self.clear_selection(), '+')
        self.bind("<FocusIn>", lambda _: self._focus_in(), '+')

        if hand_on_title:
            self.bind("<Motion>", self._on_motion, '+')

    def _setup_font(self):
        ttk.Style().configure('Treeview', rowheight=self._font.metrics("linespace") + 8)

    def _on_motion(self, event):
        region = self.identify_region(event.x, event.y)
        if region == "heading":
            self.configure(cursor="hand2")
        else:
            self.configure(cursor="")

    def clear(self):
        self.delete(*self.get_children())

    def clear_selection(self):
        self.selection_remove(self.selection())

    def get_cell_info_by_event(self, event) -> Optional[CellInfo]:
        # noinspection PyTypeChecker
        return self.get_cell_info_by_ids(
            self.identify_column(event.x),
            self.identify_row(event.y),
            self.identify_region(event.x, event.y)
        )

    def get_cell_info_by_ids(self, column_id, row_id, region: RegionType) -> Optional[CellInfo]:
        if column_id == '':
            column_id = None

        if row_id == '':
            row_id = None

        # noinspection PyTypeChecker
        column_name: Optional[str] = self.column(column_id, 'id') if column_id else None
        cell_value: str = ''

        if column_id and row_id:
            if column_id == '#0':
                cell_value = self.item(row_id, 'text')
            else:
                cell_value = self.set(row_id, column_id)

        if column_name == '':
            column_name = None

        if cell_value is None:
            cell_value = ''

        return CellInfo(
            column_id,
            row_id,
            column_name,
            cell_value,
            region
        )

    def column(self, column_id, option=None, **kw):
        column_name = super().column(column_id, 'id')
        type_field = 'type'

        self._width_set[column_name] = 'width' in kw or 'minwidth' in kw or self._width_set.get(column_name, False)

        if option == type_field:
            return self._types.get(column_name)

        if type_field in kw:
            self._types[column_name] = kw.pop(type_field)

            if not kw:
                return

        result = super().column(column_id, option, **kw)

        if isinstance(result, dict):
            column_type = self._types.get(column_name)

            if column_type:
                result[type_field] = column_type

        return result

    def _calculate_columns_width(self, _=None):
        for column_name in self["columns"]:
            if self._width_set.get(column_name, False):
                continue

            width = self._calculate_max_width(column_name)
            self.column(column_name, width=width, minwidth=width)

    @lru_cache
    def _calculate_max_width(self, column_name):
        column_name = super().column(column_name, 'id')

        values = get_values_from_enum(self._types.get(column_name))
        values.append(self.heading(column_name)['text'])

        return max(map(self._font.measure, values)) + COLUMN_TITLE_PADDING

    def force_update_columns_width(self):
        for column in self["columns"]:
            self.column(column, width=self.column(column, 'width'))

    def configure(self, dct: dict[str, Any] | None = None, *args, **kwargs):
        result = super().configure(dct, *args, **kwargs)

        if dct and 'displaycolumns' in dct:
            self.force_update_columns_width()

        return result

    def as_list(self, row_id):
        return self.item(row_id, 'values')

    def as_list_of_list(self) -> list[list[str]]:
        return [self.as_list(row_id) for row_id in self.get_children()]

    def as_dict(self, row_id) -> JsonDict:
        column_names = self["columns"]
        values = self.as_list(row_id)

        return {
            key: value for key, value in zip(column_names, values)
            if value and value.strip()
        }

    def as_list_of_dict(self) -> list[JsonDict]:
        return [self.as_dict(row_id) for row_id in self.get_children()]

    def begin_changes(self, disable_before_change_event=False):
        if self._stop_event_broadcast:
            raise RuntimeError("Has already been called begin_changes")

        self._stop_event_broadcast = True
        self._before_change_sent = disable_before_change_event
        self._changed = tuple()

    def end_changes(self):
        if not self._stop_event_broadcast:
            raise RuntimeError("begin_changes must be called before end_changes")

        self._stop_event_broadcast = False
        self._before_change_sent = False

        if self._changed:
            sequence, args, kwargs = self._changed
            self._changed = tuple()

            super().event_generate(sequence, *args, **kwargs)

    def event_generate(self, sequence, *args, **kwargs):
        if self._stop_event_broadcast:
            if sequence == ExtendedTreeviewEvents.BEFORE_CHANGE and not self._before_change_sent:
                self._before_change_sent = True
                return super().event_generate(sequence, *args, **kwargs)

            if sequence == ExtendedTreeviewEvents.CHANGE:
                self._changed = (sequence, args, kwargs)

            return

        super().event_generate(sequence, *args, **kwargs)

    def insert(self, parent, index, iid=None, **kw):
        self.event_generate(ExtendedTreeviewEvents.BEFORE_CHANGE)
        result = super().insert(parent, index, iid, **kw)
        self.event_generate(ExtendedTreeviewEvents.CHANGE)
        return result

    def delete(self, *args):
        self.event_generate(ExtendedTreeviewEvents.BEFORE_CHANGE)
        result = super().delete(*args)
        self.event_generate(ExtendedTreeviewEvents.CHANGE)
        return result

    def set(self, item, column=None, value=None):
        if value is not None:
            self.event_generate(ExtendedTreeviewEvents.BEFORE_CHANGE)

        result = super().set(item, column, value)

        if value is not None:
            self.event_generate(ExtendedTreeviewEvents.CHANGE)

        return result

    def move(self, item, parent, index):
        self.event_generate(ExtendedTreeviewEvents.BEFORE_CHANGE)
        result = super().move(item, parent, index)
        self.event_generate(ExtendedTreeviewEvents.CHANGE)
        return result

    def _focus_in(self):
        items = self.get_children()

        if not items:
            return

        selected_items = self.selection()

        if selected_items:
            items = selected_items

        item = items[0]

        if not selected_items:
            self.selection_set(item)

        self.focus(item)

    def focus_set(self):
        super().focus_set()
        self._focus_in()

    def selection_indices(self):
        return [self.index(item) for item in self.selection()]

    def selection_indices_set(self, indices):
        items = self.get_children()
        self.selection_set([items[index] for index in indices])

    def select_all_rows(self):
        items = self.get_children()

        if items:
            self.selection_set(items)

        self.update_focus()

    def move_rows_up(self):
        selected_items = self.selection()

        if selected_items:
            for selected_item in selected_items:
                index = self.index(selected_item)
                next_index = index - 1

                if index <= 0:
                    break

                self.move(selected_item, '', next_index)

        self.update_focus()

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

        self.update_focus()

    def add_row(self, values=None, index=None):
        selected_items = self.selection()

        if selected_items and index is None:
            selected_item = selected_items[0]
            index = self.index(selected_item)

            self.insert('', index, values=values or [])
            self.selection_set(self.get_children()[index])
        else:
            self.insert('', index or 0, values=values or [])

        self.update_focus()

    def delete_selected_rows(self):
        selected_items = self.selection()

        if selected_items:
            index = self.index(selected_items[0])

            self.delete(*selected_items)
            children = self.get_children()

            if len(children) <= index:
                index -= 1

            if children and len(children) > index:
                self.selection_set(children[index])

        self.update_focus()

    def update_focus(self):
        if self.focus_get() != self:
            return

        self.focus_set()
