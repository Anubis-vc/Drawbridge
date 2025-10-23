from abc import ABC, abstractmethod


class ArduinoLike(ABC):
    @abstractmethod
    def send_command(self, command: str):
        pass

    @abstractmethod
    def read_line(self):
        pass

    @abstractmethod
    def close(self):
        pass

    # Support usage as a context manager
    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc, tb):
        pass
