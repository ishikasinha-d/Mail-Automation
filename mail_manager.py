"""Importing the required modules"""
import os.path
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from difflib import get_close_matches as close_matches
from pprint import pprint

from manage_labels import Label
from manage_downloads import Download
from manage_message import MessageManager

class MailManager:

    def __init__(self, creds):

        # taking sender name and mail as input and
        # initializing the object 
        self.sender_name= input("Enter sender name: ")
        self.sender_mail= input("Enter sender mail: ")
        
        self.messages= []

        try:
            # service object to call the Gmail API
            global service
            service = build('gmail', 'v1', credentials=creds)      

        except HttpError as error:
            print(f'An error occurred: {error}')

    def print_menu(self):
        """Function to print menu options"""
        print("="*100)
        print( """            Menu Options:
                1.Create Draft
                    a. without attachment
                    b. along with attachment
                2.Send an email 
                    a. without attachment
                    b. along with attachment
                3.Download an attachment from mail
                4.Download email
                5.Create Label
                6.Add an email to label
                7.Exit
    """
    )


    def send_message(self):
        """Function to send the message"""
        try:
            message_sent= MessageManager.send_message(service, 'me', self.new_message)
            print(message_sent)
        except HttpError as error:
                print(f'An error occurred: {error}')

    def create_draft(self):
        """Function to create draft"""
        try:
            draft= MessageManager.create_draft(service, self.sender_mail, self.new_message)
            print("DRAFT CREATED")
        
        except HttpError as error:
                print(f'An error occurred: {error}')

    def create_message(self, attachment='n'):
        """
        Function to create a message. This includes the text part and attachement part(if any)
        """
        receiver= input("Enter receiver's mail: ")
        subject= input("Enter email subject: ")
        message_body= input("Enter message body: ")

        if attachment=='y':
            # take list of file paths as input
            file_attachements = []
            paths = input("Enter comma seperated file paths: ")
            file_attachements = paths.split(",")
            
            # checking if the files entered by user exists or not
            # and moving on with the existing files
            for file in file_attachements:
                if not os.path.exists(file):
                    print(f"Cannot find {file}. Moving on without attaching this file..")
                    file_attachements.remove(file)

            if(len(file_attachements) != 0):
                # when one or more attachement files provided exists
                self.new_message = {'raw':MessageManager.create_message_with_attachment(self.sender_mail, receiver, subject , message_body, file_attachements)}
            else:
                # when none of the attachement files provided are found existing
                print("File paths not provided, continuing to next step...") 
                self.new_message= MessageManager.create_message(self.sender_mail, receiver, subject , message_body)
        else:
            # when the user doesn't provide any list of attachements
            self.new_message= MessageManager.create_message(self.sender_mail, receiver, subject , message_body)
        self.messages.append([receiver,self.new_message])
        
        
    def download(self, msg, only_attachement, attachment_list=[]):
        """
        Function to 
        1. search query and print matching results
        2. download the mail and attachement
        """
        print("Searching...")
        # get emails that match the query you specify
        searched_messages= Download.search_messages(service, msg)
        print("Matching results:- \n")
        # when the user wants to download the whole mail 
        if only_attachement=='N':
            pprint(searched_messages)
        # when user wants to download the whole mail then only_attachement=='N'
        # therefore for each email matched, download plain/text (HTML) and attachments
        # when user wants to download only attachments then only_attachement=='Y'
        # therefore for each email matched, print the attachement choices
        for msg in searched_messages:
            Download.download_message(service, msg, only_attachement, attachment_list)

    def create_label(self, service):
        """Function to create a label"""
        while True:
            # print existing label names 
            labels_list= Label.print_labels(service, True)
            # take the new label user wants to create as input
            label_name= input("Enter the name of label you want to create: ").upper()
            # check if the input label name provided already exists or not
            # if it doesn't, create a new label
            # else ask for the input again
            if label_name not in labels_list:
                Label.create_label(service, label_name)
                break
            else:
                print("This label is already present, no need to create it!")

    def add_label(self, service):
        """Function to add email to label"""
        # input the message to which you want to add labels to
        query= input("Enter the message you want to add label to: ")
        # search the message and print the results
        messages= Download.search_messages(service, query)
        pprint(messages)
        # creating list of message ids
        message_id_list=[]
        for message in messages:
            print(message['id'], end= "  ")
            message_id_list.append(message['id'])
        # input list of labels to add to this message
        input_label=[]
        labels_list= Label.print_labels(service, False)
        input_label= input("Enter comma seperated name of labels you want to add: ")
        label_names_list= input_label.split(",")
        # creating list of label ids
        label_id_list=[]
        for label_name in label_names_list:
            label_name= label_name.upper()
            label_id= Label.get_label_id(label_name,labels_list)
            label_id_list.append(label_id)
            print(f"{label_name}: {label_id}")
        # adding all the labels provided to all the email essages found
        print("\nAdding label...")
        Label.add_label(service, label_id_list, message_id_list)
        print("DONE")

    def make_choice(self):
        """
        Function to take user choice as input and perform the operations according to the menu options
        """
        # taking user choice as input 
        print("What option do you want to choose? ")
        choice= input() 
        op1= ['1', 'one', 'option one', 'op1', 'option 1', 'create draft']
        op2= ['2', 'two', 'option two', 'op2', 'option 2', 'send message', 'send mssg', 'send msg']
        op3= ['3', 'three', 'option three', 'op3', 'option 3', 'download attachement']
        op4= ['4', 'four', 'option four', 'op4', 'option 4', 'download mail']
        op5= ['5', 'five', 'option five', 'op5', 'option 5', 'create label']
        op6= ['6', 'six', 'option six', 'op6', 'option 6', 'add label']
        op7= ['7', 'seven', 'option seven', 'op7', 'option 7', 'exit', 'quit']
        
        # user chooses to create draft
        if close_matches(choice, op1, 1, 0.9):
            user_response= input("Do you want to attach any file ? Y/N: ")
            if user_response in ['y', 'yes','Y', 'Yes', 'YES']:
                self.create_message('y')
            else:
                self.create_message()
            self.create_draft()

        # user chooses to send email
        elif close_matches(choice, op2, 1, 0.9):
            user_response= input("Do you want to attach any file ? Y/N: ")
            if user_response in ['y', 'yes','Y', 'Yes', 'YES']:
                self.create_message('y')
            else:
                self.create_message()
            self.send_message()
        
        # user chooses to download attachment
        elif close_matches(choice, op3, 1, 0.9):
            msg = input("Enter the attachement you want to download: ")
            # searching the attachments matching the query
            attachment_list=[]
            self.download(msg, 'Y',attachment_list)
            # printing the attachments in a tabular format and taking user choice as input
            response= Download.get_attachement_choice(attachment_list)
            chosen_attachment= attachment_list[response]
            # downloading the attachment chosen by the user
            Download.get_attachement(service, chosen_attachment['body'], chosen_attachment['message'],\
                             chosen_attachment['folder_name'], chosen_attachment['filename'], chosen_attachment['file_size'] )
        
        # user chooses to download email
        elif close_matches(choice, op4, 1, 0.9):
            msg = input("Enter the mail you want to download: ")
            self.download(msg, 'N')

        # user choses to create label
        elif close_matches(choice, op5, 1, 0.9):
            self.create_label(service)

        # user choses to add label to message
        elif close_matches(choice, op6, 1, 0.9):
            self.add_label(service)

        # user chooses to exit
        elif close_matches(choice, op7, 1, 0.9):
            print("Exiting...")
            return False

        else:
            print("Your choice doesn't match any of the options")

        return True