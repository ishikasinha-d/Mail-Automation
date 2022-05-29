"""Importing the required modules"""
import base64
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
import os
from email import encoders
from logger import logger
from apiclient import errors

class MessageManager:

    def create_message(sender, to, subject, message_text):
        """Create a message for an email.

        Args:
            sender: Email address of the sender.
            to: Email address of the receiver.
            subject: The subject of the email message.
            message_text: The text of the email message.

        Returns:
            An object containing a base64url encoded email object.
        """
        try:
            message = MIMEText(message_text)
            message['to'] = to
            message['from'] = sender
            message['subject'] = subject
            return {'raw': (base64.urlsafe_b64encode(message.as_bytes())).decode()}
        except Exception as e:
            logger.error(f'An exception occurred: {e}')
            logger.debug('In create_message() in manage_message.py ')
            print(f"An error has occured. Please check the log file: {logger.filename}")

    def create_message_with_attachment(sender, to, subject, message_text, files):
        """Create a message for an email.

        Args:
            sender: Email address of the sender.
            to: Email address of the receiver.
            subject: The subject of the email message.
            message_text: The text of the email message.
            file: The path to the file to be attached.

        Returns:
            An object containing a base64url encoded email object.
        """
        try:
            message = MIMEMultipart()
            message['to'] = to
            message['from'] = sender
            message['subject'] = subject

            emailMsg = f" {message_text} \n {len(files)} Files Attached"
            message.attach(MIMEText(emailMsg, 'plain'))
            
            for attachment in files:
                content_type, encoding = mimetypes.guess_type(attachment)
                main_type, sub_type = content_type.split('/', 1)
                file_name = os.path.basename(attachment)
            
                with open(attachment, 'rb') as f:        
                    myFile = MIMEBase(main_type, sub_type)
                    myFile.set_payload(f.read())
                    myFile.add_header('Content-Disposition', 'attachment', filename=file_name)
                    encoders.encode_base64(myFile)
            
                message.attach(myFile)
            return base64.urlsafe_b64encode(message.as_bytes()).decode()

        except Exception as e:
            logger.error(f'An exception occurred: {e}')
            logger.debug('In create_message_with_attachment() in manage_message.py ')
            print(f"An error has occured. Please check the log file: {logger.filename}")

    def create_draft(service, user_id, message_body):
        """Create and insert a draft email. Print the returned draft's message and id.

        Args:
            service: Authorized Gmail API service instance.
            user_id: User's email address. The special value "me"
            can be used to indicate the authenticated user.
            message_body: The body of the email message, including headers.

        Returns:
            Draft object, including draft id and message meta data.
        """
        try:
            message = {'message': message_body}
            draft = service.users().drafts().create(userId=user_id, body=message).execute()
            logger.debug(f"Draft id: {draft['id']}")
            logger.debug(f"Draft message: {draft['message']}")
            return draft
        except errors.HttpError as error:
            logger.error(f"An error occurred: {error}")
            logger.debug('In create_draft() in manage_message.py ')
            print(f"An error has occured. Please check the log file: {logger.filename}")
            return None
        except Exception as e:
            logger.error(f'An exception occurred: {e}')
            print(f"An error has occured. Please check the log file: {logger.filename}")
            return None

    def send_message(service, user_id, message):
        """Send an email message.

        Args:
            service: Authorized Gmail API service instance.
            user_id: User's email address. The special value "me"
            can be used to indicate the authenticated user.
            message: Message to be sent.

        Returns:
            Sent Message.
        """
        try:
            message = (service.users().messages().send(userId=user_id, body=message).execute())
            logger.debug(f"Message Id: {message['id']}")
            return message
        except errors.HttpError as error:
            logger.error(f"An error occurred: {error}")
            logger.debug('In send_message() in manage_message.py ')
            print(f"An error has occured. Please check the log file: {logger.filename}")
        except Exception as e:
            logger.error(f'An exception occurred: {e}')
            print(f"An error has occured. Please check the log file: {logger.filename}")

