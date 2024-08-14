import itertools
from typing import Optional

from configuration.migration.base import BaseMigration


class RemoveHighIoPriority(BaseMigration):
    @staticmethod
    def get_target_version() -> int:
        return 3

    @staticmethod
    def should_migrate(config: dict) -> bool:
        return config['version'] == 2

    @staticmethod
    def migrate(config: dict) -> Optional[dict]:
        for rule in itertools.chain(config.get('processRules', []), config.get('serviceRules', [])):
            if rule.get('ioPriority') == 'High':
                del rule['ioPriority']

        return config
