import copy

from configuration.migration.base import BaseMigration
from configuration.migration.m0_rules_to_split_rules_config import MigrationRules2SplitRulesConfig
from constants.app_info import APP_NAME_WITH_VERSION
from constants.log import LOG
from service.config_service import ConfigService
from util.messages import show_error

MIGRATIONS: list[type[BaseMigration]] = [
    MigrationRules2SplitRulesConfig
]
"""
List of migration classes to be executed in order.
"""


def run_all_migration():
    """
    Runs all necessary migrations on the configuration.
    Creates a backup before migration, applies each migration in order,
    logs progress, and saves the updated configuration if successful.
    Shows an error and stops if any migration fails.
    """

    config: dict = ConfigService.load_config_raw()
    need_migrate = any(migration.should_migrate(config) for migration in MIGRATIONS)

    if not need_migrate:
        return

    LOG.info(f"Creating backup of the current configuration before migration")
    ConfigService.backup_config()

    has_error = False

    for migration in MIGRATIONS:
        migration_name = migration.__name__

        try:
            if not migration.should_migrate(copy.deepcopy(config)):
                continue

            LOG.info(f"[{migration_name}] Starting migration")

            migrated_config = migration.migrate(copy.deepcopy(config))
            migrated_config['version'] = migration.get_target_version()

            LOG.info(f"[{migration_name}] Migration completed to version {migrated_config['version']}")
            config = migrated_config
        except Exception as e:
            has_error = True
            LOG.exception(f"[{migration_name}] Migration failed")
            show_error(
                f"Error Detected - {APP_NAME_WITH_VERSION}",
                f"Migration `{migration_name}` failed: \n{str(e)}"
            )
            break

    if not has_error:
        ConfigService.save_config_raw(config)
