from Mail_marking_as_read import mark_as_read
from download_attachments import download_attachment
from settings import gmail_authenticate, token
from threadid import thread
import shutup

shutup.please()
try:
    def extractor():
        """Function to get latest messages and send it to the process accordingly"""

        # get the Gmail API service
        service = gmail_authenticate(token)
        # Getting 50 gmails
        list_of_threads = thread(service,maxResults=50)
        print(list_of_threads)
        for index in list_of_threads[::-1]:
            message = service.users().messages().get(userId='me', id=index['id']).execute()
            print(message)
            if 'attachmentId' in message['payload']['parts'][0]['body'] or 'attachmentId' in \
                    message['payload']['parts'][1]['body']:
                attachments = True
            else:
                attachments = False

            if attachments:
                # Downloading Attachments
                print(download_attachment(message['id'],service))
                mark_as_read(message['id'], service)

except Exception as e:
    print("Error downloading the PDF")

extractor()
