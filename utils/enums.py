from enum import Enum, StrEnum


class AccessLevel(Enum):
    ADMIN = "admin"
    FAMILY = "family"
    FRIEND = "friend"
    STRANGER = "stranger"


class DoorControls(StrEnum):
    OPEN = "OPEN"
    CLOSE = "CLOSE"


class NotificationStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    INVALID_CREDENTIALS = "invalid_credentials"
    RATE_LIMITED = "rate_limited"
    NETWORK_ERROR = "network_error"
    UNKNOWN_ERROR = "unknown_error"


class OpenCvColors(Enum):
    GREEN = (0, 255, 0)
    RED = (0, 0, 255)
    YELLOW = (0, 255, 255)


class MpColors(Enum):
    CYAN = (255, 255, 0)
    WHITE = (255, 255, 255)
    RED = (0, 0, 255)
    YELLOW = (0, 255, 255)
    BLUE = (255, 0, 0)
    GREEN = (0, 255, 0)


class ConfigSections(Enum):
    RECOGNITION = "face_recognition"
    NOTIFICATIONS = "notifications"
    BLINK = "blink_config"
    OVERLAY = "overlay"
