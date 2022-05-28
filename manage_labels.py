"""Importing the required modules"""
from googleapiclient.errors import HttpError
from logger import logger

class Label:

    def get_label_id(input_label, labels_list):
        """Function to get label id from label name"""
        for label in labels_list:
            if label['name'] == input_label:
                return label['id']
       
    def get_labels_list(service):
        """Function to get a list of {label name, label id}"""
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
            logger.error(f'An error occurred: {error}')
            logger.debug('In get_labels_list() in manage_labels.py ')
            print(f"An error has occured. Please check the log file: {logger.filename}")
        except Exception as e:
            logger.error(f'An exception occurred: {e}')
            print(f"An error has occured. Please check the log file: {logger.filename}")

    def print_labels(service, only_names):
        """
        Function to 
        1. print a list of label names
        2. return list of label names only
        3. return list of label names with label ids
        """
        try:
            print("Label List: ")
            labels_list= Label.get_labels_list(service)
            label_names=[]
            # printing label names
            for label in labels_list:
                    label_names.append(label['name'])
                    print(label['name'], end="  ")
            print()

            if only_names:
                # just return list of names
                return label_names
            else:
                # otherwise we'll need both names and ids so that 
                # we can retreive id when the user inputs label name
                return labels_list
        except Exception as e:
            logger.error(f'An exception occurred: {e}')
            logger.debug('In print_labels() in manage_labels.py ')
            print(f"An error has occured. Please check the log file: {logger.filename}")
        
            
    def create_label(service, label_name):
        """Function to create a new label"""
        try:
            label={
            "labelListVisibility": "labelShow",
            "messageListVisibility": "show",
            "name": label_name
            }
            results = service.users().labels().create(userId='me',body=label).execute()
            logger.debug(results)
        except HttpError as error:
            logger.error(f'An error occurred: {error}')
            logger.debug('In create_label() in manage_labels.py ')
            print(f"An error has occured. Please check the log file: {logger.filename}")
        except Exception as e:
            logger.error(f'An exception occurred: {e}')
            print(f"An error has occured. Please check the log file: {logger.filename}")

    def add_label(service, label_id_list, message_id_list):
        """Function to add labels to messages"""
        try:
            post_data= {
            "addLabelIds": label_id_list
            }
            for message_id in message_id_list:
                result = service.users().messages().modify(userId='me', id=message_id, body=post_data).execute()
                logger.debug(result)
        except HttpError as error:
            logger.error(f'An error occurred: {error}')
            logger.debug('In add_label() in manage_labels.py ')
            print(f"An error has occured. Please check the log file: {logger.filename}")
        except Exception as e:
            logger.error(f'An exception occurred: {e}')
            print(f"An error has occured. Please check the log file: {logger.filename}")