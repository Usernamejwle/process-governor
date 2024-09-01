from tkinter import Tk, BOTH

from ui.widget.common.treeview.scrollable import ScrollableTreeview


class SortableTreeview(ScrollableTreeview):
    def __init__(self, master=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs, hand_on_title=True)
        self._sort_column_name = None
        self._sort_reverse = False
        self._setup_sorting()

    def _setup_sorting(self):
        for column_name in self["columns"]:
            self.heading(column_name, command=lambda c=column_name: self._on_heading_click(c))

    def _on_heading_click(self, column):
        if self._sort_column_name == column:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_column_name = column
            self._sort_reverse = False

        self.sort_column()

    def sort_column(self):
        if not self._sort_column_name:
            return

        column = self._sort_column_name
        reverse = self._sort_reverse

        items = [(self._get_value_as_type(self.set(k, column)), k) for k in self.get_children()]
        items.sort(key=lambda x: (isinstance(x[0], str), x[0]), reverse=reverse)

        for index, (_, k) in enumerate(items):
            self.move(k, '', index)

        self._update_heading_text()

    @staticmethod
    def _get_value_as_type(value):
        if value.replace('.', '', 1).isdigit():
            return float(value) if '.' in value else int(value)
        return value

    def _update_heading_text(self):
        up = '⭡'
        down = '⭣'
        sort_symbol = up if self._sort_reverse else down

        for column_name in self["columns"]:
            title = self.heading(column_name, 'text')
            title = (title
                     .replace(up, '')
                     .replace(down, '')
                     .strip())

            if column_name == self._sort_column_name:
                title = f"  {title} {sort_symbol}"

            self.heading(column_name, text=title)

    def sort_column_name(self, column_name):
        self._sort_column_name = column_name


if __name__ == "__main__":
    root = Tk()
    treeview = SortableTreeview(root, columns=('Column1', 'Column2', 'Column3'), show='headings')

    data = [
        ('Apple', 3, 50),
        ('1', 3, 50),
        ('2', 3, 50),
        ('Banana', 1, 30),
        ('Cherry', 2, 40),
        ('Date', 5, 25),
        ('Elderberry', 10, 100),
        ('Fig', 7, 45),
        ('Grape', 12, 20),
        ('Honeydew', 4, 60),
        ('Indian Fig', 8, 70),
        ('Jackfruit', 6, 150),
        ('Kiwi', 9, 85),
        ('Lemon', 13, 10),
        ('Mango', 14, 200),
        ('Nectarine', 11, 90),
        ('Orange', 2, 40),
        ('Papaya', 16, 120),
        ('Quince', 15, 110),
        ('Raspberry', 18, 35),
        ('Strawberry', 19, 95),
        ('Tangerine', 17, 55),
        ('Ugli Fruit', 21, 130),
        ('Vanilla', 22, 300),
        ('Watermelon', 20, 40),
        ('Xigua', 23, 80),
        ('Yellow Passion Fruit', 24, 75),
        ('Zucchini', 25, 15)
    ]

    for item in data:
        treeview.insert('', 'end', values=item)

    treeview.heading('Column1', text='Fruit Name')
    treeview.heading('Column2', text='Quantity')
    treeview.heading('Column3', text='Price')

    treeview.pack(fill=BOTH, expand=True)
    root.mainloop()
