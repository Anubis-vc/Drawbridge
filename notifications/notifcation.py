from abc import ABC, abstractmethod


class NotificationService(ABC):
    @abstractmethod
    def send_notification(self, name: str, access_level: str):
        pass
