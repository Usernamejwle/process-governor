from tkinter import PhotoImage
from tkinter.ttk import Notebook

from constants.resources import UI_PROCESS_RULES, UI_SERVICE_RULES
from enums.rules import RuleType
from ui.widget.settings.tabs.rules.base_rules_tab import BaseRulesTab
from util.ui import load_img


class ProcessRulesTab(BaseRulesTab):
    def __init__(self, master: Notebook):
        super().__init__(master, RuleType.PROCESS)

    @staticmethod
    def icon() -> PhotoImage:
        return load_img(file=UI_PROCESS_RULES)

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
        return load_img(file=UI_SERVICE_RULES)

    @staticmethod
    def title() -> str:
        return "Service Rules"

    @staticmethod
    def description() -> str:
        return "Settings for defining **priority**, **I/O priority**, and **core affinity** for __services__."
