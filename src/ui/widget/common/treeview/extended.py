from dataclasses import dataclass
from functools import lru_cache
from tkinter import ttk, END
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

        self._generate_event_change: bool = True
        self._changed: tuple = tuple()

        self._setup_font()
        self.bind('<Configure>', self._calculate_columns_width, '+')
        self.bind('<Escape>', lambda _: self.clear_selection())

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
        cell_value: str = self.set(row_id, column_id) if column_id and row_id else ''

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

    def begin_changes(self):
        if not self._generate_event_change:
            raise RuntimeError("Has already been called begin_changes")

        self._changed = []
        self._generate_event_change = False

    def end_changes(self):
        if self._generate_event_change:
            raise RuntimeError("begin_changes must be called before end_changes")

        self._generate_event_change = True

        if self._changed:
            sequence, args, kwargs = self._changed
            self._changed = []

            super().event_generate(sequence, *args, **kwargs)

    def event_generate(self, sequence, *args, **kwargs):
        if not self._generate_event_change and sequence == ExtendedTreeviewEvents.CHANGE:
            self._changed = (sequence, args, kwargs)
            return

        super().event_generate(sequence, *args, **kwargs)

    def insert(self, parent, index, iid=None, **kw):
        result = super().insert(parent, index, iid, **kw)
        self.event_generate(ExtendedTreeviewEvents.CHANGE)
        return result

    def delete(self, *args):
        result = super().delete(*args)
        self.event_generate(ExtendedTreeviewEvents.CHANGE)
        return result

    def set(self, item, column=None, value=None):
        result = super().set(item, column, value)

        if value is not None:
            self.event_generate(ExtendedTreeviewEvents.CHANGE)

        return result

    def move(self, item, parent, index):
        result = super().move(item, parent, index)
        self.event_generate(ExtendedTreeviewEvents.CHANGE)
        return result
