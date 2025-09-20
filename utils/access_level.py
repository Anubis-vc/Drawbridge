from enum import Enum


class AccessLevel(Enum):
    ADMIN = "admin"
    FAMILY = "family"
    FRIEND = "friend"
    STRANGER = "stranger"
