import os

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def get_credentials():

    credentials = None

    # Load saved credentials
    if os.path.exists("token.json"):
        credentials = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )

    # Refresh expired credentials
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

    # Authorize if no valid credentials exist
    if not credentials or not credentials.valid:

        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json",
            SCOPES
        )

        credentials = flow.run_local_server(port=0)

        # Save credentials
        with open("token.json", "w") as token:
            token.write(credentials.to_json())

    return credentials