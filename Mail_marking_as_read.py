def mark_as_read(thread_id, service):

    # marking as email is read
    try:
        service.users().threads().modify(userId='me', id=thread_id, body={'removeLabelIds': ['UNREAD']}).execute()
        return "Mail Marked as Read"
    except:
        return "Error in marking a mail as read"
