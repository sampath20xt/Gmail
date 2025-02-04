def thread(service,maxResults=None):
    if maxResults is not None:
        try:
            threads = service.users().threads().list(userId='me', labelIds=['UNREAD', 'CATEGORY_PERSONAL'],
                                                     maxResults=maxResults).execute().get(
                'threads')
            return threads
        except Exception as e:
            return "Error in getting the List of thread mails"
