from gmail.auth import get_credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
from langchain_core.tools import tool


credentials = get_credentials()

gmail = build(
    "gmail",
    "v1",
    credentials=credentials
)


def send_email(to:str,subject:str,body:str):
    """Send an email using Gmail."""
    message = MIMEText(body)

    message["to"] = to
    
    message["subject"] = subject

    # Convert the email into Gmail API format
    raw_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    

    result = gmail.users().messages().send(
        userId="me",
        body={"raw": raw_message}
    ).execute()

    return result

#send_email("nakshatrapande7@gmail.com","Meeting Update","The meeting is postponed to 5 PM")