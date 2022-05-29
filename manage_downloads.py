"""Importing required modules"""
from email import message
import os.path
from base64 import urlsafe_b64decode
from googleapiclient.errors import HttpError
from tabulate import tabulate
from logger import logger
from simple_term_menu import TerminalMenu

class Download:

    def search_messages(service, query):
        """Function to search messages matching to the query"""
        try:
            result = service.users().messages().list(userId='me',q=query).execute()
            messages = []
            if 'messages' in result:
                messages.extend(result['messages'])
            # searching on each page as the messages are paginated
            while 'nextPageToken' in result:
                page_token = result['nextPageToken']
                result = service.users().messages().list(userId='me',q=query, pageToken=page_token).execute()
                if 'messages' in result:
                    messages.extend(result['messages'])
            return messages
        except HttpError as error:
            logger.error(f'An error occurred: {error}')
            logger.debug('In create_message_with_attachment() in manage_message.py ')
            print(f"An error has occured. Please check the log file: {logger.filename}")
        except Exception as e:
            logger.error(f'An exception occurred: {e}')
            print(f"An error has occured. Please check the log file: {logger.filename}")

    def get_mails_on_page(service):
         """Function to get mails in paginated manner"""
         try:
             result = service.users().messages().list(userId='me').execute()
             if 'messages' in result:
                 yield result['messages']
             # searching on each page as the messages are paginated
             while 'nextPageToken' in result:
                 page_token = result['nextPageToken']
                 result = service.users().messages().list(userId='me', pageToken=page_token).execute()
                 if 'messages' in result:
                     yield result['messages']
         except HttpError as error:
                 logger.error(f'An error occurred: {error}')
                 logger.debug('In create_message_with_attachment() in manage_message.py ')
                 print(f"An error has occured. Please check the log file: {logger.filename}")
         except Exception as e:
                 logger.error(f'An exception occurred: {e}')
                 print(f"An error has occured. Please check the log file: {logger.filename}")

    def select_mail(service):
        page =1 
        # mails_on_page is a generator object
        mails_on_page= Download.get_mails_on_page(service)
        while True:
            print(f"Printing mails on page {page}: ")
            page= page+1
        
            message_id_list = []
            try:
                message_id_list = next(mails_on_page)
            except StopIteration:
                print("All pages over, exiting....")
                break
            
            msg_sub_list= []
            for indx,msg in enumerate(message_id_list):
                msg_sub_list.append(f"Message - {indx}|{msg['id']} ")
            msg_sub_list.append('next')

            terminal_menu = TerminalMenu(msg_sub_list, preview_command="python3 ./utils.py {}", preview_size=0.75)
            menu_entry_index = terminal_menu.show()

            if menu_entry_index == None:
                break

            if msg_sub_list[menu_entry_index]=='next':
                continue
            else:
                print(msg_sub_list[menu_entry_index])
                return message_id_list[menu_entry_index]
                break


    # utility function print bytes in a nice format
    def get_size_format(b, factor=1024, suffix="B"):
        """
        Scale bytes to its proper byte format
        e.g:
            1253656 => '1.20MB'
            1253656678 => '1.17GB'
        """
        for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
            if b < factor:
                return f"{b:.2f}{unit}{suffix}"
            b /= factor
        return f"{b:.2f}Y{suffix}"

    # utility fucntion to make a folder name
    def clean(text):
        """Function to clean text for creating a folder"""
        return "".join(c if c.isalnum() else "_" for c in text)


    def get_attachement_choice(attachment_list):
        """
        Function to 
        1. print matching attachements with details in a tabular format
        2. input user choice and return it
        """
        try:
            attachment_choice_list=[]
            headers= ['S. No.', 'Filename', 'Filesize']
            for indx, attachment in enumerate(attachment_list):
                attachment_choice_list.append([indx+1, attachment['filename'], attachment['file_size']])
            print(tabulate(attachment_choice_list, headers, tablefmt="github"))
            return int(input("Enter S. No. of the attachment you want to download: "))-1
        except Exception as e:
            logger.error(f'An exception occurred: {e}')
            logger.debug('In get_attachement_choice() in manage_downloads.py ')
            print(f"An error has occured. Please check the log file: {logger.filename}")


    def write_in_file(filepath, data, mode= "ab"):
        """Function to download data"""
        try:
            with open(filepath, mode) as f:
                f.write(urlsafe_b64decode(data))
        except Exception as e:
            logger.error(f'An exception occurred: {e}')
            logger.debug('In write_in_file() in manage_downloads.py ')
            print(f"An error has occured. Please check the log file: {logger.filename}")

    def get_attachement(service, body, message, folder_name, filename, file_size):
        """
        Function to
        1. get the attachment ID and make another request to get the attachment itself
        2. download the attachment
        """
        try:
            print("Saving the file:", filename, "size:", Download.get_size_format(file_size), "in ", folder_name)
            attachment_id = body.get("attachmentId")
            attachment = service.users().messages().attachments().get(id=attachment_id, userId='me', messageId=message['id']).execute()
            data = attachment.get("data")
            if not os.path.isdir(folder_name):
                os.mkdir(folder_name)
            filepath = os.path.join(folder_name, filename)
            if data:
                Download.write_in_file(filepath, data)
        except Exception as e:
            logger.error(f'An exception occurred: {e}')
            logger.debug('In get_attachement() in manage_downloads.py ')
            print(f"An error has occured. Please check the log file: {logger.filename}")
   
    # utilityfunction to parse the content of an email partition
    def parse_parts(service, parts, folder_name, message, only_attachement, attachment_list):
        """
        Function to 
        1. parse the content of an email partition
        2. Download text/html content (if available) and save it under the folder created as index.html
        3. Download any file that is attached to the email and save it in the folder created
        4. Download an attachement from a mail
        """
        try:
            if parts:
                for part in parts:
                    filename = part.get("filename")
                    mimeType = part.get("mimeType")
                    body = part.get("body")
                    data = body.get("data")
                    file_size = body.get("size")
                    part_headers = part.get("headers")
                    if part.get("parts"):
                        # recursively call this function when we see that a part
                        # has parts inside
                        Download.parse_parts(service, part.get("parts"), folder_name, message, only_attachement, attachment_list)
                    # when the user wants to download the whole mail
                    if only_attachement == 'N' and mimeType == "text/plain":
                        # if the email part is text plain
                        if data:
                            text = urlsafe_b64decode(data).decode()
                            print(text)
                    # when the user wants to download the whole mail
                    elif only_attachement == 'N' and mimeType == "text/html":
                        # if the email part is an HTML content
                        # save the HTML file and optionally open it in the browser
                        if not filename:
                            filename = "index.html"
                        os.mkdir(folder_name)
                        filepath = os.path.join(folder_name, filename)
                        print("Saving HTML to", filepath)
                        Download.write_in_file(filepath, data)
                    
                    # attachment other than a plain text or HTML
                    for part_header in part_headers:
                        part_header_name = part_header.get("name")
                        part_header_value = part_header.get("value")
                        if part_header_name == "Content-Disposition":
                            if "attachment" in part_header_value:
                                if only_attachement=='N':
                                    Download.get_attachement(service, body, message, folder_name, filename, file_size)
                                else:
                                    attachment_list.append({'folder_name': folder_name, 'filename':filename, 'body': body, 'message': message, 'file_size': file_size})
        except Exception as e:
            logger.error(f'An exception occurred: {e}')
            logger.debug('In get_attachement() in manage_downloads.py ')
            print(f"An error has occured. Please check the log file: {logger.filename}")
                            

    # main function for reading an email
    def download_message(service, message, only_attachement, attachment_list):
        """
        Function to
        1. Print email basic information (To, From, Subject & Date) and plain/text parts
        2. Creates a folder for each email based on the subject
        3. Download the content of the email
        """
        try:
            msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
            # parts can be the message body, or attachments
            payload = msg['payload']
            headers = payload.get("headers")
            parts = payload.get("parts")
            folder_name = "email"
            has_subject = False
            if headers:
                # this section prints email basic info & creates a folder for the email
                for header in headers:
                    name = header.get("name")
                    value = header.get("value")
                    if only_attachement == 'N':
                        if name.lower() == 'from':
                            # we print the From address
                            print("From:", value)
                        if name.lower() == "to":
                            # we print the To address
                            print("To:", value)
                    if name.lower() == "subject":
                        # make our boolean True, the email has "subject"
                        has_subject = True
                        # make a directory with the name of the subject
                        folder_name = Download.clean(value)
                        # to download within downloads folder
                        folder_name= f"Downloads/{folder_name}"
                        # we will also handle emails with the same subject name
                        folder_counter = 0
                        while os.path.isdir(folder_name):
                            folder_counter += 1
                            # we have the same folder name, add a number next to it
                            if folder_name[-1].isdigit() and folder_name[-2] == "_":
                                folder_name = f"{folder_name[:-2]}_{folder_counter}"
                            elif folder_name[-2:].isdigit() and folder_name[-3] == "_":
                                folder_name = f"{folder_name[:-3]}_{folder_counter}"
                            else:
                                folder_name = f"{folder_name}_{folder_counter}"
                        if only_attachement == 'N':
                            print("Subject:", value)      
                    if only_attachement == 'N' and name.lower() == "date":
                        # we print the date when the message was sent
                        print("Date:", value)

            Download.parse_parts(service, parts, folder_name, message, only_attachement, attachment_list)
            if only_attachement == 'N':
                print("="*100)
        
        except Exception as e:
            logger.error(f'An exception occurred: {e}')
            logger.debug('In download_message() in manage_downloads.py ')
            print(f"An error has occured. Please check the log file: {logger.filename}")
                            
