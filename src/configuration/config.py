from typing import List, Optional

from pydantic import BaseModel, Field

from configuration.rule import ProcessRule, ServiceRule


class Config(BaseModel):
    """
    The Config class represents a configuration object for application.

    It defines the structure of the configuration, including rule application interval, logging settings, and rules.
    """

    version: Optional[int] = Field(default=None)
    """
    The version of the configuration.
    This field can be None if the version is not set.
    """

    ruleApplyIntervalSeconds: int = Field(default=1)
    """
    The time interval (in seconds) at which rules are applied to processes and services.
    Default is 1 second.
    """

    processRules: List[ProcessRule] = Field(default_factory=list)
    """
    A list of Rule objects that specify how application manages processes based on user-defined rules.
    """

    serviceRules: List[ServiceRule] = Field(default_factory=list)
    """
    A list of Rule objects that specify how application manages services based on user-defined rules.
    """
