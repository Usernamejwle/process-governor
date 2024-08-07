from tkinter import PhotoImage
from tkinter.ttk import Notebook

from enums.rules import RuleType
from ui.widget.settings.tabs.rules.base_rules_tab import BaseRulesTab
from util.ui import icon16px


class ProcessRulesTab(BaseRulesTab):
    def __init__(self, master: Notebook):
        super().__init__(master, RuleType.PROCESS)

    @staticmethod
    def icon() -> PhotoImage:
        return icon16px("list", fill="#3F888F")

    @staticmethod
    def title() -> str:
        return "Process Rules"

    @staticmethod
    def description() -> str:
        return "Settings for defining **priority**, **I/O priority**, and **core affinity** for __processes__."


class ServiceRulesTab(BaseRulesTab):
    def __init__(self, master: Notebook):
        super().__init__(master, RuleType.SERVICE)

    @staticmethod
    def icon() -> PhotoImage:
        return icon16px("cogs", fill="#6495ED")

    @staticmethod
    def title() -> str:
        return "Service Rules"

    @staticmethod
    def description() -> str:
        return "Settings for defining **priority**, **I/O priority**, and **core affinity** for __services__."


