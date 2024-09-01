from abc import ABC, abstractmethod
from tkinter import PhotoImage, ttk
from tkinter.ttk import Notebook


class BaseTab(ttk.Frame, ABC):
    def __init__(self, master: Notebook):
        super().__init__(master)

        self.master: Notebook = master

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
    def has_changes(self) -> bool:
        pass

    @abstractmethod
    def has_error(self) -> bool:
        pass


