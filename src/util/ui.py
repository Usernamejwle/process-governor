import tkinter
from tkinter import font, Widget, Entry, PhotoImage
from tkinter.font import Font
from tkinter.ttk import Treeview


def state(widget: Widget) -> str:
    return str(widget["state"])


def full_visible_bbox(tree: Treeview, row_id: str, column_id: str):
    bbox = tree.bbox(row_id, column_id)

    if bbox:
        x, y, width, height = bbox
        y_bottom = y + height
        tree_height = tree.winfo_height()

        if y_bottom <= tree_height:
            return bbox

    return None


def get_parent_with_bg(widget: Widget):
    while widget:
        cfg = widget.configure()

        if cfg and "bg" in cfg:
            return widget

        widget = widget.master
    return None


def get_label_font():
    temp_widget = tkinter.Label()
    default_font = font.nametofont(temp_widget.cget("font"))
    temp_widget.destroy()
    return default_font


def get_default_font():
    return Font(family="TkDefaultFont")


def single_font_width():
    return get_default_font().measure('0')


def get_button_font():
    temp_widget = tkinter.Button()
    default_font = font.nametofont(temp_widget.cget("font"))
    temp_widget.destroy()
    return default_font


def get_combobox_font():
    temp_widget = tkinter.Button()
    default_font = font.nametofont(temp_widget.cget("font"))
    temp_widget.destroy()
    return default_font


def get_entry_font():
    temp_entry = Entry()
    default_font = temp_entry.cget("font")
    temp_entry.destroy()
    return default_font


def load_img(file) -> PhotoImage:
    return PhotoImage(file=file)
