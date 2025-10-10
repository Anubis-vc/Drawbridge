from typing import Any, Callable
import copy
import json
from pathlib import Path


CONFIG_PATH = Path(__file__).with_name("config.json")
DEFAULT_CONFIG: dict[str, Any] = {
    "face_recognition": {"model": "buffalo_s", "similarity_threshold": 0.6},
    "notifications": {
        "enabled_services": ["email"],
        "config_objects": {
            "email": {"owner": "testing.code.ved@gmail.com", "recipients": []},
            "sms": {"recipients": ["+9873453"]},
        },
    },
    "blink_config": {
        "ear_threshold": 0.21,
        "blink_consec_frames": 2,
        "blinks_to_verify": 2,
    },
    "overlay": {"font_scale": 2, "font_thickness": 2, "mesh": False},
}


class _ConfigManager:
    def __init__(self):
        self._config_path = CONFIG_PATH
        self.config = self._load_initial_config()
        self._listeners: dict[str, Callable] = {}

    def _load_initial_config(self) -> dict[str, Any]:
        if not self._config_path.exists():
            self._config_path.parent.mkdir(parents=True, exist_ok=True)
            return copy.deepcopy(DEFAULT_CONFIG)

        try:
            return json.loads(self._config_path.read_text())
        except (json.JSONDecodeError, OSError) as exc:
            # TODO: swap to structured logging once logger is wired
            raise RuntimeError(f"Failed to load config at {self._config_path}") from exc

    def _persist_config(self) -> None:
        tmp_path = self._config_path.with_suffix(".tmp")
        try:
            payload = json.dumps(self.config, indent=4)
            tmp_path.write_text(payload)
            tmp_path.replace(self._config_path)
        except OSError as exc:
            tmp_path.unlink(missing_ok=True)
            raise RuntimeError(
                f"Failed to write config to {self._config_path}"
            ) from exc

    def register_listener(self, section: str, listener: Callable) -> None:
        self._listeners[section] = listener
        listener(self.config[section])  # push the current config on registration

    def get_section(self, section: str) -> dict[str, Any]:
        return self.config[section]

    def replace_section(self, section: str, data: dict[str, Any]) -> dict[str, Any]:
        self.config[section] = data
        if section in self._listeners:
            self._listeners[section](data)  # call the listener for this change
        self._persist_config()
        return self.config[section]


# create singleton instance so same config used across multiple files
config_manager = _ConfigManager()
