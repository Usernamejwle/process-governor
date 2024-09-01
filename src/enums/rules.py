from enum import Enum

from pydantic import BaseModel

from configuration.rule import ProcessRule, ServiceRule


class RuleType(Enum):
    PROCESS = (ProcessRule, "processRules")
    SERVICE = (ServiceRule, "serviceRules")

    def __init__(self, clazz, field_in_config):
        self.clazz: type[BaseModel] = clazz
        self.field_in_config: str = field_in_config
