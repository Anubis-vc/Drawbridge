import json
import os
from datetime import datetime
from typing import Any


class _ConfigManager:
    def __init__(self, config_file: str = "./config/config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.has_changed = False

    # Fails if config not found, this is desired behavior or else it will fail later
    def load_config(self) -> dict[str, Any]:
        with open(self.config_file, "r") as f:
            return json.load(f)

    def log_config_change(self, old_config, new_config):
        print(f"[{datetime.now()}] Configuration reloaded")
        # TODO: could find out what has changed, though maybe pass that on to objects?

    def _save(self) -> None:
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=4)
        self.last_modified = os.path.getmtime(self.config_file)

    def get_section(self, section: str) -> Any:
        if section not in self.config:
            raise KeyError(f"Section '{section}' not found in configuration")
        return self.config[section]

    def replace_section(self, section: str, data: Any) -> Any:
        if section not in self.config:
            raise KeyError(f"Section '{section}' not found in configuration")
        self.config[section] = data
        # TODO: probably good to log the changes here
        self._save()
        self.has_changed = True
        return self.config[section]


# introducing singleton so same ConfigManager used across multiple files
config_manager = _ConfigManager()
