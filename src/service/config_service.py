import json
import os.path
from abc import ABC
from datetime import datetime
from os.path import exists
from typing import Optional, List, Any

from configuration.config import Config
from configuration.logs import Logs
from configuration.rule import ProcessRule, ServiceRule
from constants.files import CONFIG_FILE_NAME, CONFIG_FILE_ENCODING
from enums.rules import RuleType
from util.decorators import cached


class ConfigService(ABC):
    """
    ConfigService is responsible for managing the application's configuration data.

    This class provides methods for saving, loading, and accessing the configuration.
    """

    @classmethod
    def save_config(cls, config: Config):
        """
        Save the provided configuration object to a JSON file.

        If the configuration is not initialized, it creates a new one.

        Args:
            config (Config): The configuration object to be saved.
        """
        if config is None:
            raise ValueError("config is None")

        with open(CONFIG_FILE_NAME, 'w', encoding=CONFIG_FILE_ENCODING) as file:
            json_data = config.model_dump_json(indent=4, exclude_none=True, warnings=False)
            file.write(json_data)

    @classmethod
    @cached(1)
    def load_config(cls, validate=True) -> Config:
        """
        Load the configuration from a JSON file or create a new one if the file doesn't exist.

        Args:
            validate (bool): Whether to validate the configuration upon loading. Defaults to True.

        Returns:
            Config: The loaded or newly created configuration object.
        """
        if not exists(CONFIG_FILE_NAME):
            cls.save_config(config := Config())
            return config

        with open(CONFIG_FILE_NAME, 'r', encoding=CONFIG_FILE_ENCODING) as file:
            if validate:
                return Config(**json.load(file))

            return Config.model_construct(**json.load(file))

    __prev_mtime = 0

    @classmethod
    def reload_if_changed(cls, prev_config: Optional[Config]) -> tuple[Config, bool]:
        """
        Reloads the configuration if it has changed since the last reload and returns the updated configuration and a flag indicating whether the configuration has changed.

        Args:
            prev_config (Optional[Config]): The previous configuration object. Can be None if there is no previous configuration.

        Returns:
            tuple[Config, bool]: A tuple containing the updated configuration object and a boolean flag indicating whether the configuration has changed. If the configuration has changed or there is no previous configuration, the updated configuration is loaded from the file. Otherwise, the previous configuration is returned.
        """
        current_mtime = os.path.getmtime(CONFIG_FILE_NAME)
        is_changed = current_mtime > cls.__prev_mtime

        cls.__prev_mtime = current_mtime

        if is_changed or prev_config is None:
            return cls.load_config(), True

        return prev_config, False

    @classmethod
    def load_rules_raw(cls, rule_type: RuleType) -> List[Any]:
        """
        Loads raw rules of a specific type from the configuration file.

        Args:
            rule_type (RuleType): The type of rules to load.

        Returns:
            List[Any]: A list of raw rule data.
        """
        if not exists(CONFIG_FILE_NAME):
            cls.save_config(Config())

        with open(CONFIG_FILE_NAME, 'r', encoding=CONFIG_FILE_ENCODING) as file:
            json_data = json.load(file)
            return json_data.get(rule_type.field_in_config, [])

    @classmethod
    def load_logs(cls) -> Logs:
        """
        Loads the logging configuration from the configuration file.

        Returns:
            Logs: The logging configuration.
        """
        if not exists(CONFIG_FILE_NAME):
            cls.save_config(config := Config())
            return config.logging

        with open(CONFIG_FILE_NAME, 'r', encoding=CONFIG_FILE_ENCODING) as file:
            json_data = json.load(file)
            return Logs(**json_data['logging'])

    @classmethod
    def save_rules(cls, rule_type: RuleType, rules: List[ProcessRule | ServiceRule]):
        """
        Save the rules of a specific type to the configuration file.

        Args:
            rule_type (RuleType): The type of rules to save.
            rules (List[ProcessRule | ServiceRule]): The list of rules to be saved.
        """
        if rules is None:
            raise ValueError("rules is None")

        config = cls.load_config(False)
        setattr(config, rule_type.field_in_config, rules)

        cls.save_config(config)

    @classmethod
    def rules_has_error(cls) -> bool:
        """
        Checks if there are any errors in the rules defined in the configuration.

        Returns:
            bool: True if there are errors in the rules, otherwise False.
        """
        try:
            for rule_type in RuleType:
                rules: List[Any] = cls.load_rules_raw(rule_type)

                try:
                    for rule in rules:
                        rule_type.clazz(**rule)
                except:
                    return True
        except:
            pass  # Yes, this is indeed a pass.

        return False

    @classmethod
    def load_config_raw(cls) -> dict:
        """
        Loads the raw configuration as a dictionary from the configuration file.

        Returns:
            dict: The raw configuration data.
        """
        if not exists(CONFIG_FILE_NAME):
            cls.save_config(Config())

        with open(CONFIG_FILE_NAME, 'r', encoding=CONFIG_FILE_ENCODING) as file:
            return json.load(file)

    @classmethod
    def save_config_raw(cls, config: dict):
        """
        Saves the raw configuration dictionary to the configuration file.

        Args:
            config (dict): The configuration data to be saved.
        """
        if config is None:
            raise ValueError("config is None")

        with open(CONFIG_FILE_NAME, 'w', encoding=CONFIG_FILE_ENCODING) as file:
            json.dump(config, file, indent=4)

    @classmethod
    def backup_config(cls):
        """
        Creates a backup of the current configuration file in the same directory where the original configuration file is located.

        If the configuration file does not exist, no backup is created.

        Raises:
            IOError: If the backup process fails.
        """
        if not exists(CONFIG_FILE_NAME):
            return

        base_name, ext = os.path.splitext(CONFIG_FILE_NAME)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"{base_name}_backup_{timestamp}.{ext}"

        try:
            with open(CONFIG_FILE_NAME, 'r', encoding=CONFIG_FILE_ENCODING) as src_file:
                with open(backup_filename, 'w', encoding=CONFIG_FILE_ENCODING) as dst_file:
                    dst_file.write(src_file.read())
        except IOError as e:
            raise IOError(f"Failed to create backup: {e}")

if __name__ == '__main__':
    print(ConfigService.rules_has_error())
