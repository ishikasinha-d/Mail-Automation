"""
subject
from
sent to
msg body
date
no. of attachemts
"""
# import os.path
import sys
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from base64 import urlsafe_b64decode
# pip install beautifulsoup4
from bs4 import BeautifulSoup
# from googleapiclient.errors import HttpError
# from manage_labels import Label
# from manage_downloads import Download
# from manage_message import MessageManager



# utilityfunction to parse the content of an email partition
def get_msg_body(parts):
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
                    get_msg_body(part.get("parts"))
                # when the user wants to download the whole mail
                if mimeType == "text/html":
                    # if the email part is an HTML content
                    # save the HTML file and optionally open it in the browser
                    return urlsafe_b64decode(data)
                
              
    except Exception as e:
        print(e)

def get_clean_string(msg):
    clean_msg = ""
    for idx, msg in enumerate(msg.split(" ")):
        clean_msg = clean_msg +" "+ msg
        if(idx%10 == 0):
            clean_msg = clean_msg + " " + "\n"
        if(idx > 30):
            clean_msg = clean_msg + "......"
            break

    return clean_msg


def get_preview(service, message):
    print("Loading.....")

    try: 
        msg = service.users().messages().get(userId='me', id=message, format='full').execute()
        # parts can be the message body, or attachments
        payload = msg['payload']
        headers = payload.get("headers")
        parts = payload.get("parts")
        msg_body= get_msg_body(parts)
        msg_from=""
        msg_to=""
        date=""
        subject=""
        # folder_name = "email"
        # has_subject = False
        if headers:
            # this section prints email basic info & creates a folder for the email
            for header in headers:
                name = header.get("name")
                value = header.get("value")
                if name.lower() == 'from':
                    # we print the From address
                    msg_from= value
                if name.lower() == "to":
                    # we print the To address
                    msg_to= value
                if name.lower() == "subject":
                    subject= value
                if name.lower() == "date":
                    date= value

        print(f"""
        From: {msg_from}
        To: {msg_to}
        Subject: {subject}
        Date: {date}
        Message(Preview not full message):""")
        # text_maker = html2text.HTML2Text()
        # text_maker.ignore_links = True
        # text_maker.bypass_tables = False
        # text_maker.ignore_images = True
        # text_maker.ignore_anchors = True
        # text_maker.body_width = 0
        soup = BeautifulSoup(msg_body.decode())
        print(get_clean_string(soup.get_text()))
        # print(msg_body.decode())
    except Exception as e:
        # logger.log(e)
        pass

# print("Loading.")
SCOPES = ['https://mail.google.com/']
creds = Credentials.from_authorized_user_file('token.json', SCOPES)
service = build('gmail', 'v1', credentials=creds) 
# print("Loading")
msg_id = sys.argv[1].strip()
print(msg_id)
# logger.log(sys.argv[1])
get_preview(service, msg_id)