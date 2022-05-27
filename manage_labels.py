from __future__ import print_function
from email import message
from encodings import search_function

import os.path
from venv import create
from base64 import urlsafe_b64decode

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from difflib import get_close_matches as close_matches
from pprint import pprint

class Label:

    def get_label_id(input_label, labels_list):
        for label in labels_list:
            if label['name'] == input_label:
                return label['id']
       

    def get_labels_list(service):
        try:
            results = service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])

            if not labels:
                print('No labels found.')
                return
            
            labels_list=[]
            for label in labels:
                labels_list.append({'name':label['name'], 'id': label['id']}) 
            return labels_list

        except HttpError as error:
            print(f'An error occurred: {error}')


    def create_label(service, label_name):
        label={
        "labelListVisibility": "labelShow",
        "messageListVisibility": "show",
        "name": label_name
        }
        results = service.users().labels().create(userId='me',body=label).execute()
        print(results)

    def add_label(service, label_id_list, message_id_list):
        post_data= {
        "addLabelIds": label_id_list
        }
   
        for message_id in message_id_list:
            result = service.users().messages().modify(userId='me', id=message_id, body=post_data).execute()
            print(result)