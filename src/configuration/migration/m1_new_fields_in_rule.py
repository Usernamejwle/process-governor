from typing import Optional

from configuration.migration.base import BaseMigration


class NewFieldsInRule(BaseMigration):
    @staticmethod
    def get_target_version() -> int:
        return 2

    @staticmethod
    def should_migrate(config: dict) -> bool:
        return config['version'] == 1

    @staticmethod
    def migrate(config: dict) -> Optional[dict]:
        for rule in config.get('processRules', []) + config.get('serviceRules', []):
            rule['selectorBy'] = 'Name'
            rule['force'] = 'N'

        return config
