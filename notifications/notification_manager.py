from typing import Any
import time

from utils.enums import AccessLevel
from notifications.notification_util import build_message
from notifications.email import EmailService
from notifications.sms import SMSService


class NotificationManager:
    def __init__(self):
        self.enabled_services: set[str] = set()
        self.noti_objects: dict[str, Any] = {}

        # vars to control notification send
        self.sent_notifications: dict[str, float] = {}
        self.unknown_time: float | None = None

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

        # remove services that are no longer enabled
        disabled = set(self.noti_objects.keys()) - self.enabled_services
        for service in disabled:
            self.noti_objects.pop(service)

        # create any newly enabled services
        for service in self.enabled_services:
            if service not in self.noti_objects:
                service_config = config_objects[service]
                self.noti_objects[service] = self.__creation_router(
                    service, service_config
                )

    def check_and_send(
        self, recognized: bool, live: bool, name: str, access_level: AccessLevel
    ):
        if recognized and live:
            last_sent = self.sent_notifications.get(name)
            if last_sent is None or time.time() - last_sent > 300:
                self.sent_notifications[name] = time.time()
                self.send(name, access_level)
        # handle unknown visitors
        elif not recognized:
            now = time.time()
            if self.unknown_time is None:
                self.unknown_time = now
            elif now - self.unknown_time > 10:
                self.send(name, AccessLevel.STRANGER)
                self.unknown_time = now

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
