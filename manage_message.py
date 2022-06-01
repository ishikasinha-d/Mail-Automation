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
from googleapiclient.errors import HttpError
from simple_term_menu import TerminalMenu
from utils import get_preview, clean_statusbar_prev

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

    def get_drafts_on_page(service):
            """Function to get drafts in paginated manner"""
            try:
                result = service.users().drafts().list(userId='me').execute()
                if 'drafts' in result:
                    yield result['drafts']
                # searching on each page as the messages are paginated
                while 'nextPageToken' in result:
                    page_token = result['nextPageToken']
                    result = service.users().drafts().list(userId='me', pageToken=page_token).execute()
                    if 'drafts' in result:
                        yield result['drafts']
            except HttpError as error:
                    logger.error(f'An error occurred: {error}')
                    logger.debug('In get_drafts_on_page() in manage_message.py ')
                    print(f"An error has occured. Please check the log file: {logger.filename}")
            except Exception as e:
                    logger.error(f'An exception occurred: {e}')
                    logger.debug('In get_drafts_on_page() in manage_message.py ')
                    print(f"An error has occured. Please check the log file: {logger.filename}")

    def select_draft(service):
        try:
            page =1 
            # drafts_on_page is a generator object
            drafts_on_page= MessageManager.get_drafts_on_page(service)
            
            while True:
                print(f"Printing drafts on page {page}: ")
                page= page+1
            
                draft_id_list = []
                try:
                    draft_id_list = next(drafts_on_page)
                except StopIteration:
                    print("All pages over, exiting....")
                    break
                
                msg_sub_list= []
                for indx,msg in enumerate(draft_id_list):
                    # If a menu entry has an additional data component (separated by |), it is passed instead to the preview command ex 180fab35397e3119 
                    # however the first data component is passed in the status bar ex. Message 0
                    msg_sub_list.append(f"Message - {indx}|{msg['id']}")
                msg_sub_list.append('next')

                # preview_size is used to control the height of the preview window. It is given as fraction of the complete terminal height (default: 0.25).
                # The width cannot be set, it is always the complete width of the terminal window.
                # menu_highlight_style: The style of the selected menu entry
                # status_bar: places a status bar below the menu
        
                # for color of the selected item in the menu, bg= background, fg= foreground, standout= default
                main_menu_style = ("bg_blue", "fg_green", "standout", )

                terminal_menu = TerminalMenu(
                    msg_sub_list, 
                    preview_command=lambda id : get_preview(service, id), 
                    preview_size=0.75, 
                    title="Choose Email",
                    menu_highlight_style = main_menu_style,
                    status_bar= lambda mssg_num : clean_statusbar_prev(mssg_num, len(draft_id_list))
                    )
                # show returns the selected menu entry index or None if the menu was canceled
                menu_entry_index = terminal_menu.show()

                # when user enters q
                if menu_entry_index == None:
                    return None

                if msg_sub_list[menu_entry_index]=='next':
                    continue
                else:
                    return draft_id_list[menu_entry_index]
        except Exception as e:
            logger.error(f'An exception occurred: {e}')
            logger.debug('In get_drafts_on_page() in manage_message.py ')
            print(f"An error has occured. Please check the log file: {logger.filename}")

    def send_draft(service, draft_id):
        try:
            service.users().drafts().send(userId='me', body={ 'id': draft_id }).execute()
            print("Draft sent")
            logger.info("Draft Id: {draft_id} has been sent")
        except HttpError as error:
            logger.error(f'An error occurred: {error}')
            logger.debug('In send_draft() in manage_message.py ')
            print(f"An error has occured. Please check the log file: {logger.filename}")
        except Exception as e:
            logger.error(f'An exception occurred: {e}')
            logger.debug('In send_draft() in manage_message.py ')
            print(f"An error has occured. Please check the log file: {logger.filename}")