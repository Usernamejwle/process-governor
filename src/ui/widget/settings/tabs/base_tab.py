from abc import ABC, abstractmethod
from tkinter import PhotoImage, ttk, LEFT
from tkinter.ttk import Notebook


class BaseTab(ttk.Frame, ABC):
    def __init__(self, master: Notebook):
        super().__init__(master)

        self.master: Notebook = master

    def add_tab_to_master(self):
        self.master.add(self, text=f" {self.title()} ", image=self.icon(), compound=LEFT)

    @staticmethod
    @abstractmethod
    def icon() -> PhotoImage:
        pass

    @staticmethod
    @abstractmethod
    def title() -> str:
        pass

    @staticmethod
    @abstractmethod
    def description() -> str:
        pass

    @staticmethod
    @abstractmethod
    def default_tooltip() -> str:
        pass

    @abstractmethod
    def load_from_config(self, config: dict):
        pass

    @abstractmethod
    def save_to_config(self, config: dict):
        pass

    @abstractmethod
    def has_unsaved_changes(self) -> bool:
        pass

    @abstractmethod
    def has_error(self) -> bool:
        pass


