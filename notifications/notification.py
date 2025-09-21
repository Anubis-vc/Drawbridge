from abc import ABC, abstractmethod
from utils.enums import NotificationStatus


class NotificationService(ABC):
    @abstractmethod
    def send_notification(self, name: str, access_level: str) -> NotificationStatus:
        pass
