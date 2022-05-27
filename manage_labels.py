from __future__ import print_function
from googleapiclient.errors import HttpError


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

    def print_labels(service, only_names):
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