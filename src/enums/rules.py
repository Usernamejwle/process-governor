from enum import Enum

from configuration.rule import ProcessRule, ServiceRule


class RuleType(Enum):
    PROCESS = (ProcessRule, "processRules")
    SERVICE = (ServiceRule, "serviceRules")

    def __init__(self, clazz, field_in_config):
        self.clazz = clazz
        self.field_in_config = field_in_config
