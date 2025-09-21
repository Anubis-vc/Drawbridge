from notifications.notification import NotificationService
from notifications.notification_util import build_message
from twilio.rest import Client
from utils.enums import NotificationStatus
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

    def send_notification(self, name, access_level) -> NotificationStatus:
        try:
            message = build_message(name, access_level)
            response = self.__create_message(message)

            if response.error_code:
                # Map Twilio error codes to our enum
                if response.error_code in [20003, 20005]:  # Authentication errors
                    return NotificationStatus.INVALID_CREDENTIALS
                elif response.error_code in [21610, 21614]:  # Rate limiting
                    return NotificationStatus.RATE_LIMITED
                else:
                    return NotificationStatus.FAILED
            else:
                return NotificationStatus.SUCCESS
        except Exception as e:
            print(f"SMS sending error: {e}")
            return NotificationStatus.UNKNOWN_ERROR
