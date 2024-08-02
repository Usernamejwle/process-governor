from enum import Enum

from configuration.rule import ProcessRule, ServiceRule
from util.ui import icon16px


class RuleType(Enum):
    PROCESS = ProcessRule, "processRules", "Process Rules", lambda:icon16px("list", fill="#3F888F")
    SERVICE = ServiceRule, "serviceRules", "Service Rules", lambda:icon16px("cogs", fill="#6495ED")

    def __init__(self, clazz, field_in_config, title, get_icon):
        self.clazz = clazz
        self.field_in_config = field_in_config
        self.title = title
        self.get_icon = get_icon
