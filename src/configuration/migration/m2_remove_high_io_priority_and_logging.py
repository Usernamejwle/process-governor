import itertools
from typing import Optional

from pydantic.config import JsonDict

from configuration.migration.base import BaseMigration


class RemoveHighIoPriorityAndLogging(BaseMigration):
    @staticmethod
    def get_target_version() -> int:
        return 3

    @staticmethod
    def should_migrate(config: JsonDict) -> bool:
        return config['version'] == 2

    @staticmethod
    def migrate(config: JsonDict) -> Optional[JsonDict]:
        for rule in itertools.chain(config.get('processRules', []), config.get('serviceRules', [])):
            if rule.get('ioPriority') == 'High':
                del rule['ioPriority']

        if 'logging' in config:
            del config['logging']

        return config
