from typing import Any, Callable


class _ConfigManager:
    def __init__(self, initial_config: dict[str, Any]):
        self.config = initial_config
        self._listeners: dict[str, Callable] = {}

    def register_listener(self, section: str, listener: Callable) -> None:
        self._listeners[section] = listener
        listener(self.config[section])  # push the current config on registration

    def get_section(self, section: str) -> Any:
        return self.config[section]

    def replace_section(self, section: str, data: dict[str, Any]) -> dict[str, Any]:
        self.config[section] = data
        if section in self._listeners:
            self._listeners[section](data)  # call the listener for this change
        return self.config[section]


# TODO: add logging at some point for all these changes

# create singleton instance so same config used across multiple files
initial_config = {
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
config_manager = _ConfigManager(initial_config)
