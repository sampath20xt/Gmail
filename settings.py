import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

environment = 'cloud'
email_api = 'kpranay.imaginnovate@gmail.com'
token = 'token_local.pickle'
if environment == 'cloud':
    email_api = 'kpranay.imaginnovate@gmail.com'
    token = r'token.pickle'


# Request all access (permission to read/send/receive emails, manage the inbox, and more)
SCOPES = ['https://mail.google.com/']
our_email = email_api

def gmail_authenticate(token):
    creds = None

    # the file token_cloud.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time
    if os.path.exists(str(token)):
        with open(token, "rb") as tokenn:
            creds = pickle.load(tokenn)
    # if there are no (valid) credentials availablle, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # save the credentials for the next run
        with open(str(token), "wb") as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)


print(gmail_authenticate(token))
