from notifications.notification import NotificationService
from utils.enums import NotificationStatus

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.message import EmailMessage

import os.path
import base64


class EmailService(NotificationService):
    def __init__(self, user_id="me", owner="vchughcodes@gmail.com", recipients=[]):
        self.SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
        self.user_id = user_id
        self.owner = owner
        self.recipients = recipients
        self.cc_string = ','.join(recipients) if recipients else None
        self.subject = "Facial Recognition Doorway"

    def __get_credentials(self):
        """Gets oauth credentials for gmail api"""

        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time.
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            print("Storing credentials to token.json ")
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        # print(f"Current token scopes: {creds.scopes}")
        return creds

    def __create_email(self, message_content):
        """Build and send the email using preconfigured credentials"""
        service = build("gmail", "v1", credentials=self.__get_credentials())

        message = EmailMessage()
        message.set_content(message_content)
        message["To"] = self.owner
        message["From"] = "gduser1@workspacesamples.dev"
        message["Subject"] = self.subject
        if self.cc_string:
            message["cc"] = self.cc_string

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"raw": encoded_message}
        send_message = (
            service.users()
            .messages()
            .send(userId=self.user_id, body=create_message)
            .execute()
        )
        print(f"Message ID: {send_message['id']}")

    def send(self, message: str) -> NotificationStatus:
        try:
            self.__create_email(message)
            return NotificationStatus.SUCCESS
        except HttpError as e:
            print(f"Gmail API error: {e}")
            if e.resp.status == 401:
                return NotificationStatus.INVALID_CREDENTIALS
            elif e.resp.status == 429:
                return NotificationStatus.RATE_LIMITED
            else:
                return NotificationStatus.FAILED
        except Exception as e:
            print(f"Email sending error: {e}")
            return NotificationStatus.UNKNOWN_ERROR
        
    def update_config(self, owner: str, recipients: list):
        if self.recipients != recipients:
            self.recipients = recipients
            self.cc_string = ','.join(recipients) if recipients else None
            print("updated cc recipients")
