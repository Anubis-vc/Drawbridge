from enum import Enum


class AccessLevel(Enum):
    ADMIN = "admin"
    FAMILY = "family"
    FRIEND = "friend"
    STRANGER = "stranger"


class NotificationStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    INVALID_CREDENTIALS = "invalid_credentials"
    RATE_LIMITED = "rate_limited"
    NETWORK_ERROR = "network_error"
    UNKNOWN_ERROR = "unknown_error"
