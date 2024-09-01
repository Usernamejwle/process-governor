import json
from collections import OrderedDict
from tkinter import END
from typing import Any, Optional, Iterable

from pydantic import BaseModel, ValidationError
from pydantic.config import JsonDict
from pydantic_core import PydanticUndefined

from ui.widget.common.treeview.extended import ExtendedTreeview

_anchor_mapping = {
    "left": "w",
    "center": "center",
    "right": "e"
}


class PydanticTreeviewLoader:
    def \
            __init__(self, treeview: ExtendedTreeview, model: type[BaseModel]):
        self._treeview = treeview
        self._model = model
        self._setup_columns()

    def _setup_columns(self):
        treeview = self._treeview
        model_fields = self._model.model_fields

        for column_name in treeview["columns"]:
            field_info = model_fields.get(column_name)

            if field_info:
                title = field_info.title or column_name
            else:
                raise RuntimeError("field_info is None")

            extra = field_info.json_schema_extra or dict() if field_info else dict()

            if extra.get('default_sort_column_ui', False) and hasattr(treeview, 'sort_column_name'):
                treeview.sort_column_name(column_name)

            kw = {
                'anchor': _anchor_mapping[extra.get('justify_ui', 'center')],
                'stretch': extra.get('stretchable_column_ui', False),
                'type': field_info.annotation
            }

            width = extra.get('width_ui', None)
            if width:
                kw['minwidth'] = kw['width'] = width

            treeview.heading(column_name, text=title)
            treeview.column(column_name, **kw)

    def set_data(self, rules: Iterable[JsonDict | BaseModel]):
        treeview = self._treeview
        treeview.clear()
        column_names = treeview["columns"]

        for rule in rules:
            values = [
                getattr(rule, column_name, '')
                if isinstance(rule, BaseModel)
                else rule.get(column_name, '')
                for column_name in column_names
            ]
            values = list(map(lambda value: '' if value is None or str(value) == '' else str(value), values))
            treeview.insert('', END, values=values)

        if hasattr(treeview, 'sort_column'):
            treeview.sort_column()

    def has_changes(self):
        pass

    def get_data(self) -> list[JsonDict]:
        return self._treeview.as_list_of_dict()

    def get_error_if_available(self, row_id) -> Optional[tuple[Any, Any]]:
        try:
            # noinspection PyCallingNonCallable
            self._model(**self._treeview.as_dict(row_id))
            return None
        except ValidationError as e:
            return row_id, json.loads(e.json())

    def get_default_row(self) -> JsonDict:
        treeview = self._treeview
        result = OrderedDict()
        model_fields = self._model.model_fields

        for column_name in treeview["columns"]:
            field_info = model_fields.get(column_name) or ''
            default_value = '' if field_info.default == PydanticUndefined else field_info.default or ''
            result[column_name] = str(default_value)

        return result
