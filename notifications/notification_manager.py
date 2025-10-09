from typing import Any

from utils.enums import AccessLevel
from notifications.notification_util import build_message
from notifications.email import EmailService
from notifications.sms import SMSService


class NotificationManager:
    def __init__(self):
        self.enabled_services: set[str] = set()
        self.noti_objects: dict[str, Any] = {}

    def send(self, name: str, access_level: AccessLevel, message=None):
        if not message:
            message = build_message(name, access_level)
        for service in self.enabled_services:
            self.noti_objects[service].send(message)

    def update_config(self, config: dict[str, Any]):
        enabled_set = set(config["enabled_services"])
        config_objects = config["config_objects"]

        self.enabled_services = enabled_set
        print("new enabled services", self.enabled_services)

        # Create or update enabled services
        for service in self.enabled_services:
            if service not in self.noti_objects:
                service_config = config_objects[service]
                self.noti_objects[service] = self.__creation_router(
                    service, service_config
                )

    def __creation_router(self, service: str, config: dict[str, Any]):
        match service:
            case "email":
                return EmailService(**config)
            case "sms":
                return SMSService(**config)
            case _:
                raise NotImplementedError(
                    f"Notification service '{service}' is not supported"
                )
