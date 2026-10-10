
import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Gmail permissions: read messages only.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Keep authentication files beside this Python file.
BASE_DIR = Path(__file__).resolve().parent
TOKEN_FILE = BASE_DIR / "token.json"
CREDENTIALS_FILE = BASE_DIR / "credentials.json"


def get_gmail_service():
    """Authenticate with Google and return a Gmail API service."""

    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(
            str(TOKEN_FILE), SCOPES
        )

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)
    return service


def mainـone():
    """List Gmail labels."""

    try:
        service = get_gmail_service()

        results = (
            service.users()
            .labels()
            .list(userId="me")
            .execute()
        )

        labels = results.get("labels", [])

        if not labels:
            print("No labels found.")
            return

        print("Labels:")
        for label in labels:
            print(label["name"])

    except (HttpError, OSError, ValueError) as error:
        print(f"An error occurred: {error}")


def main():
    """List messages in the Gmail inbox."""

    try:
        service = get_gmail_service()

        results = (
            service.users()
            .messages()
            .list(userId="me", labelIds=["INBOX"])
            .execute()
        )

        messages = results.get("messages", [])

        if not messages:
            print("No messages found.")
            return

        print("Messages:")

        for message in messages:
            msg = (
                service.users()
                .messages()
                .get(
                    userId="me",
                    id=message["id"],
                    format="metadata",
                    metadataHeaders=["Subject", "From", "Date"],
                )
                .execute()
            )

            headers = msg.get("payload", {}).get("headers", [])
            header_values = {
                header["name"].lower(): header["value"]
                for header in headers
            }

            print(f'Message ID: {message["id"]}')
            print(f'Subject: {header_values.get("subject", "(No subject)")}')
            print(f'From: {header_values.get("from", "(Unknown sender)")}')
            print(f'Date: {header_values.get("date", "(Unknown date)")}')
            print("-" * 40)

    except (HttpError, OSError, ValueError) as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
