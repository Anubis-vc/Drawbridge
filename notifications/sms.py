from notifications.notifcation import NotificationService
from utils.access_level import AccessLevel
from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()


class SMSService(NotificationService):
    def __init__(self):
        self.client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN")
        )

    def __create_message(self, message):
        response = self.client.messages.create(
            body=message,
            from_=os.getenv("TWILIO_ORIGIN_NUMBER"),
            to=os.getenv("TWILIO_DESTINATION_NUMBER"),
        )
        return response

    def send_notification(self, name, access_level):
        if access_level == AccessLevel.ADMIN or AccessLevel.FAMILY:
            message = f"{name} is entering the building"
        elif access_level == AccessLevel.FRIEND:
            message = f"{name} is at the door"
        else:
            # TODO: Take picture of unknown person
            message = "An unknown person is attempting to enter the building"

        response = self.__create_message(message)
        return response.error_code if response.error_code else 200


if __name__ == "__main__":
    noti_service = SMSService()
    result = noti_service.send_notification("Ved", AccessLevel.ADMIN)
    print(result)
