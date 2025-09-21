from utils import AccessLevel


def build_message(name: str, access_level):
    if access_level == AccessLevel.ADMIN or AccessLevel.FAMILY:
        message = f"{name} is entering the building"
    elif access_level == AccessLevel.FRIEND:
        message = f"{name} is at the door"
    else:
        # TODO: take picture of person and send
        message = "An unknown person is attempting to enter the building"
    return message
