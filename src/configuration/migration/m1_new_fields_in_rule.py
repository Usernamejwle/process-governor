import itertools
from typing import Optional

from configuration.migration.base import BaseMigration
from enums.bool import BoolStr
from enums.selector import SelectorType


class NewFieldsInRule(BaseMigration):
    @staticmethod
    def get_target_version() -> int:
        return 2

    @staticmethod
    def should_migrate(config: dict) -> bool:
        return config['version'] == 1

    @staticmethod
    def migrate(config: dict) -> Optional[dict]:
        for rule in config.get('processRules', []):
            rule['selectorBy'] = SelectorType.NAME.value
            rule['force'] = BoolStr.NO.value

        for rule in config.get('serviceRules', []):
            rule['force'] = BoolStr.NO.value

        return config
