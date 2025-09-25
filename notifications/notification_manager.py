from utils.enums import AccessLevel
from notifications.notification_util import build_message
from notifications.email import EmailService
from notifications.sms import SMSService


class NotificationManager:
    def __init__(self, enabled_services: list[str], config_objects: dict):
        self.enabled_services = set(enabled_services)
        self.noti_objects = self.__create_noti_objects(config_objects)

    def send(self, name: str, access_level: AccessLevel, message=None):
        if not message:
            message = build_message(name, access_level)
        for service in self.enabled_services:
            self.noti_objects[service].send(message)

    def update_config(self, enabled_services: list[str], config_objects: dict):
        enabled_services = set(enabled_services)
        if self.enabled_services != enabled_services:
            # get symmetric difference of the two sets
            for service in (self.enabled_services ^ enabled_services):
                if service not in self.enabled_services:
                    self.enabled_services.add(service)
                else:
                    self.enabled_services.remove(service)
        print("new enabled services", enabled_services)

        for service, config in config_objects.items():
            if service not in self.noti_objects:
                self.noti_objects[service] = self.__creation_router(service, config)
            else:
                self.noti_objects[service].update_config(**config)

    def __create_noti_objects(self, config_objects: dict):
        result = {}
        for service, config in config_objects.items():
            if service == "email":
                result[service] = self.__creation_router(service, config)
        return result

    def __creation_router(self, service, config):
        match service:
            case "email":
                return EmailService(**config)
            case "sms":
                return SMSService(**config)
            case _:
                raise NotImplementedError
