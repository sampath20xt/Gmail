def download_attachment(thread_id,service):
    import base64
    import os

    if not os.path.exists("Base_Folder"):
        os.makedirs("Base_Folder")

    output_path = os.getcwd() + '/Base_Folder'
    message = service.users().messages().get(userId='me', id=thread_id).execute()
    print(message)
    pdflist = []
    for part in message['payload']['parts']:
        filename = f"{thread_id}_{part['filename']}"
        if part['filename']:
            pdflist.append(part['filename'])
            attachment = service.users().messages().attachments().get(userId='me', messageId=message['id'],
                                                                      id=part['body']['attachmentId']).execute()
            file_data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
            import os
            full_output_path = os.path.join(output_path, filename)

            with open(full_output_path, 'wb') as f:
                f.write(file_data)

    return pdflist
