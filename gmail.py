from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os

SCOPES = [
    'https://mail.google.com/'
    
    ] # Or gmail.readonly, gmail.compose etc.

'''
so it turns out that service account cannot be used to access gmail api for a user. you either have a workspace account 
with domain-wide delegation enabled or just use oauth2 (as we do here) for personal gmail accounts. in this case the app
is authorized to run only on desktop with no callback stuff


THIS SCRIPT IS MEANT FOR SPARSE USE. it takes time for gmail to get really populated
'''

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        print("Loading credentials from token.json")
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing access token...")
            creds.refresh(Request())
        else: 
            print("Fetching new tokens...")
            flow = InstalledAppFlow.from_client_secrets_file('cred.json', SCOPES)
            creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        
    service = build('gmail', 'v1', credentials=creds)
    print("Gmail service created successfully.")
    
    return service

def get_messages_by_query(service, query: str):
    messages = []
    request = service.users().messages().list(userId='me', q=query)
    while request is not None:
        results = request.execute()
        messages.extend(results.get('messages', []))
        request = service.users().messages().list_next(previous_request=request, previous_response=results)
    
    return messages

# this logic is gonna be the same for selected emails, so we can reuse it
def delete_emails(service ,messages: list):
    for message in messages:
        msg_id = message['id']
        service.users().messages().delete(userId='me', id=msg_id).execute()
        print(f"Message with ID {msg_id} permanently deleted.")

# allowed with gmail.modify scope
def trash_emails(service ,messages: list):
    for message in messages:
        msg_id = message['id']
        service.users().messages().trash(userId='me', id=msg_id).execute()
        print(f"Message with ID {msg_id} moved to trash.")

# needs the https://mail.google.com/ scope -> very permissive
def batch_delete_emails(service, messages: list):
    """Batch deletes up to 1000 messages in one request."""
    if not messages:
        print("No messages to delete.")
        return
    
    ids = [msg['id'] for msg in messages]
    # Gmail API accepts up to 1000 IDs per batch request
    for i in range(0, len(ids), 1000):
        chunk = ids[i:i+1000]
        service.users().messages().batchDelete(
            userId='me',
            body={'ids': chunk}
        ).execute()
        print(f"Batch deleted {len(chunk)} messages.")

# i just feel safer doing this.
def delete_token():
    if os.path.exists('token.json'):
        os.remove('token.json')
        print("Deleted token.json")
    else:
        print("token.json does not exist.")

queries = [
    'label:glassdoor older_than:7d',
    'category:updates older_than:7d',
    'category:social older_than:7d'
]

if __name__ == '__main__':
    gmail_service = get_gmail_service()
    
    for q in queries:
        print(f"\nProcessing query: {q}") 
        messages = get_messages_by_query(gmail_service, q)
        count = len(messages) if messages else 0
        print(f"Found {count} messages matching the query: {q}")
        
        if count > 0:
            choice = input(f"Do you want to batch delete these {count} messages? (y/N): ").strip().lower()
            if choice == 'y':
                batch_delete_emails(gmail_service, messages)
            else:
                print("Skipped deletion.")

    delete_token()