"""Importing required modules"""
from os import path
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from logger import logger


try:

    # Restricted Scope with Full access to the account’s mailboxes
    SCOPES = ['https://mail.google.com/']
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            # while the flow establishement is in process, the PORT will be busy
            # so another connection cannot be established on the same PORT
            # once the connection has been established, the port will be exported and can be 
            # reused to establish another connection
            PORT= 8080
            while True:
                try:
                    creds = flow.run_local_server(port=PORT)
                    break
                except OSError as oe:
                    print(f"Port {PORT} is busy.", end=" ")
                    PORT= PORT+1
                    print(f" Trying Port {PORT}......")
            logger.log("API Connection established")
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

except HttpError as error:
    logger.error(f'An error occurred: {error}')
    logger.debug("API Connection not established")
    print(f"An error has occured. Please check the log file: {logger.filename}")

except Exception as e:
    logger.error(f'An exception occurred: {e}')
    print(f"An error has occured. Please check the log file: {logger.filename}")

from mail_manager import MailManager
ob= MailManager(creds)
while True:
    ob.print_menu()
    if not ob.make_choice():
        break

