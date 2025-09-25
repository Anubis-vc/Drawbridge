from abc import ABC, abstractmethod
from utils.enums import NotificationStatus


class NotificationService(ABC):
    @abstractmethod
    def send(self, message) -> NotificationStatus:
        pass
