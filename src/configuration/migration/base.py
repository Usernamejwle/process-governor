from abc import ABC, abstractmethod


class BaseMigration(ABC):
    @staticmethod
    @abstractmethod
    def should_migrate(config: dict) -> bool:
        """
        Checks if migration is necessary.

        :param config: The current configuration dictionary.
        :return: True if migration is required, otherwise False.
        """
        pass

    @staticmethod
    @abstractmethod
    def migrate(config: dict) -> dict:
        """
        Performs the migration and returns the updated configuration.

        :param config: The current configuration dictionary.
        :return: Updated configuration after migration.
        """
        pass

    @staticmethod
    @abstractmethod
    def get_target_version() -> int:
        """
        Returns the target version for the configuration after migration.

        :return: The target version number.
        """
        pass
