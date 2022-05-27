"""Send an email message from the user's account.
"""

import base64
from distutils.command.build import build
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
import os
from email import encoders

from apiclient import errors
from bs4 import BeautifulSoup

class MessageManager:

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

            print (f"Draft id: {draft['id']}\nDraft message: {draft['message']}")

            return draft
        except errors.HttpError as error:
            print (f"An error occurred: {error}")
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
            message = (service.users().messages().send(userId=user_id, body=message)
                       .execute())
            print (f"Message Id: {message['id']}")
            return message
        except errors.HttpError as error:
            print (f"An error occurred: {error}")


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
        message = MIMEText(message_text)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        return {'raw': (base64.urlsafe_b64encode(message.as_bytes())).decode()}
        

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
        
            f = open(attachment, 'rb')
        
            myFile = MIMEBase(main_type, sub_type)
            myFile.set_payload(f.read())
            myFile.add_header('Content-Disposition', 'attachment', filename=file_name)
            encoders.encode_base64(myFile)
        
            f.close()
        
            message.attach(myFile)

        return base64.urlsafe_b64encode(message.as_bytes()).decode()
       
       

def build_file_part(file):
        """Creates a MIME part for a file.

        Args:
        file: The path to the file to be attached.

        Returns:
        A MIME part that can be attached to a message.
        """
        content_type, encoding = mimetypes.guess_type(file)

        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'
        main_type, sub_type = content_type.split('/', 1)
        if main_type == 'text':
            with open(file, 'rb'):
                msg = MIMEText('r', _subtype=sub_type)
        elif main_type == 'image':
            with open(file, 'rb'):
                msg = MIMEImage('r', _subtype=sub_type)
        elif main_type == 'audio':
            with open(file, 'rb'):
                msg = MIMEAudio('r', _subtype=sub_type)
        else:
            with open(file, 'rb'):
                msg = MIMEBase(main_type, sub_type)
                msg.set_payload(file.read())
        filename = os.path.basename(file)
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        return msg