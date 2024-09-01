from enum import Enum
from tkinter import END, BOTH, Widget
from typing import Optional, Literal

from constants.ui import EditableTreeviewEvents, ScrollableTreeviewEvents
from ui.widget.common.combobox import EnumCombobox
from ui.widget.common.entry import ExtendedEntry
from ui.widget.common.treeview.extended import CellInfo, ExtendedTreeview, RegionType
from ui.widget.common.treeview.scrollable import ScrollableTreeview
from util.ui import full_visible_bbox
from util.utils import extract_type

ColumnType = Literal["text", "list"]

_justify_mapping = {
    "w": "left",
    "e": "right",
    "center": "center"
}


class CellEditor:
    def __init__(
            self,
            master: ExtendedTreeview,
            cell_info: CellInfo
    ):
        self.cell = cell_info
        self.widget = self._setup_widgets(master)

    def _setup_widgets(self, master):
        def on_change(_):
            self.event_generate(EditableTreeviewEvents.SAVE_CELL)

        def on_escape(_):
            self.event_generate(EditableTreeviewEvents.ESCAPE)

        cell = self.cell
        column_settings = master.column(cell.column_id)
        annotation = column_settings.get('type')
        justify = _justify_mapping[column_settings.get('anchor', 'center')]

        if issubclass(extract_type(annotation), Enum):
            editor = EnumCombobox(
                master,
                annotation,
                justify=justify,
                state="readonly",
                auto_width=False
            )
            editor.set(cell.value)
            editor.bind("<<ComboboxSelected>>", on_change, '+')
        else:
            editor = ExtendedEntry(master, justify=justify)
            editor.insert(0, cell.value)
            editor.select_range(0, END)
            editor.bind("<FocusOut>", on_change, '+')

        editor.bind("<Return>", on_change, '+')
        editor.bind("<Escape>", on_escape, '+')
        editor.pack(fill=BOTH)

        return editor

    def get(self):
        return self.widget.get().strip()

    def __getattr__(self, name):
        return getattr(self.widget, name)


class EditableTreeview(ScrollableTreeview):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._editor: Optional[Widget | CellEditor] = None

        self.bind("<Button-1>", self._save_and_destroy_editor, '+')
        self.bind("<Double-1>", self._on_dbl_click, '+')
        self.bind(ScrollableTreeviewEvents.SCROLL, self._place_editor, '+')
        self.bind("<Configure>", lambda _: self.after(1, self._place_editor), '+')

    def editor(self) -> CellEditor:
        return self._editor

    def _on_dbl_click(self, event):
        self.edit_cell(
            self.identify_column(event.x),
            self.identify_row(event.y),
            self.identify_region(event.x, event.y)
        )

    def _create_editor(self, cell):
        if cell.region != 'cell':
            return

        self._editor = editor = CellEditor(self, cell)

        editor.bind(EditableTreeviewEvents.SAVE_CELL, self._save_and_destroy_editor, '+')
        editor.bind(EditableTreeviewEvents.ESCAPE, self._destroy_editor, '+')
        editor.bind("<Destroy>", self._on_editor_destroy, '+')

        self._place_editor()
        self.event_generate(EditableTreeviewEvents.START_EDIT_CELL)

    def _place_editor(self, _=None):
        editor = self._editor

        if not editor:
            return

        cell = editor.cell
        bbox = full_visible_bbox(self, cell.row_id, cell.column_id)

        if bbox:
            x, y, width, height = bbox
            editor.place(x=x, y=y, width=width, height=height)
            editor.after(0, lambda: editor.focus_force())  # fixing focus_force not working from time to time
        else:
            editor.place_forget()

    def _save_and_destroy_editor(self, _=None):
        self._save_cell_changes()
        self._destroy_editor()

    def _destroy_editor(self, _=None):
        if self._editor:
            self._editor.destroy()

    def _save_cell_changes(self):
        editor = self._editor

        if not editor:
            return

        new_value = editor.get()
        cell = editor.cell

        if cell.value != new_value:
            self.set(cell.row_id, cell.column_id, new_value)

    def _on_editor_destroy(self, _=None):
        self._editor = None

    def edit_cell(self, column_id, row_id, region: RegionType):
        self._destroy_editor()
        self._create_editor(self.get_cell_info_by_ids(column_id, row_id, region))

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

    def add_row(self, values=None, index=None):
        selected_items = self.selection()

        if selected_items and index is None:
            selected_item = selected_items[0]
            index = self.index(selected_item)

            self.insert('', index, values=values or [])
            self.selection_set(self.get_children()[index])
        else:
            self.insert('', index or 0, values=values or [])

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
