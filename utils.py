from base64 import urlsafe_b64decode
from bs4 import BeautifulSoup
from logger import logger


def clean_statusbar_prev(msg, length):
    """
    Function to show status of item selected by user in clean format
    ex. Message-0 is converted to Message 1 of 100 
    where 100 is total no. of messages on a page
    """
    msg_list = msg.split('-')
    if(len(msg_list) < 2):
        return "Go to next page"
    else:
        return f"Message {int(msg_list[1].strip())+1} of {length}"

def get_msg_body(parts):
    """Function to parse the content of an email partition"""
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
                # if the email part is an HTML content
                if mimeType == "text/html":
                    return urlsafe_b64decode(data)
                    
    except Exception as e:
        logger.error(f'An exception occurred: {e}')
        logger.debug('In get_msg_body() in utils.py ')
        return (f"An error has occured. Please check the log file: {logger.filename}")

def get_clean_string(msg):
    """
    Function to 
    1. clean message body to display in preview
    2. get 10 words in a line
    3. and total 30 words only to preview 
    """
    clean_msg = ""
    for idx, msg in enumerate(msg.split(" ")):
        clean_msg = clean_msg +" "+ msg
        if(idx%10 == 0):
            clean_msg = clean_msg + " " + "\n"
        if(idx > 30):
            clean_msg = clean_msg + "......"
            break
    return clean_msg


def get_preview(service, messageId):
    """Function to display preview in interactive menu of mails"""
    if messageId == "next":
        return "\nNext Page"
    try:
        msg = service.users().messages().get(userId='me', id=messageId, format='full').execute()
        payload = msg['payload']
        headers = payload.get("headers")
        parts = payload.get("parts")
        msg_body= get_msg_body(parts)
        msg_from=""
        msg_to=""
        date=""
        subject=""

        if headers:
            # this section to get email basic info 
            for header in headers:
                name = header.get("name")
                value = header.get("value")
                if name.lower() == 'from':
                    msg_from= value
                if name.lower() == "to":
                    msg_to= value
                if name.lower() == "subject":
                    subject= value
                if name.lower() == "date":
                    date= value

        # creating beautiful soup oject to convert html to text
        if msg_body != None:
            soup = BeautifulSoup(msg_body.decode(), features="html.parser")
            msg_body = get_clean_string(soup.get_text())
        else:
            msg_body = "\nNo text found in message body"
        prev_string =  (f"""
        From: {msg_from}
        To: {msg_to}
        Subject: {subject}
        Date: {date}
        Message(Preview not full message)s:
{msg_body}
        """)
        
        return prev_string

    except Exception as e:
        logger.error(f'An exception occurred: {e}')
        logger.debug('In get_msg_body() in utils.py ')
        return (f"An error has occured. Please check the log file: {logger.filename}")
