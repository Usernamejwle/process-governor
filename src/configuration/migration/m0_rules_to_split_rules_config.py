from typing import Optional

from configuration.migration.base import BaseMigration


class MigrationRules2SplitRulesConfig(BaseMigration):
    @staticmethod
    def get_target_version() -> int:
        return 1

    @staticmethod
    def should_migrate(config: dict) -> bool:
        return 'version' not in config or config['version'] is None

    @staticmethod
    def migrate(config: dict) -> Optional[dict]:
        if 'rules' not in config:
            return config

        process_rules = list(filter(lambda o: 'processSelector' in o, config['rules']))
        service_rules = list(filter(lambda o: 'serviceSelector' in o, config['rules']))

        for processRule in process_rules:
            processRule['selector'] = processRule['processSelector']
            del processRule['processSelector']

        for serviceRule in service_rules:
            serviceRule['selector'] = serviceRule['serviceSelector']
            del serviceRule['serviceSelector']

        del config['rules']
        config['processRules'] = process_rules
        config['serviceRules'] = service_rules

        return config
