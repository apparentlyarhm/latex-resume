import os
import itertools
import threading
import time
import sys

from datetime import datetime
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

load_dotenv()

# This is just for animations
class LoadingAnimation:
    def __init__(self, message="Loading"):
        self.message = message
        self.done = False
        self.animation_thread = None

    def animate(self):
        for c in itertools.cycle(['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏']):
            if self.done:
                break
            sys.stdout.write(f'\r{self.message} {c}')
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write('\rDone!       \n')

    def start(self):
        self.animation_thread = threading.Thread(target=self.animate)
        self.animation_thread.start()

    def stop(self):
        self.done = True
        if self.animation_thread:
            self.animation_thread.join()


SERVICE_ACCOUNT_FILE = "credentials.json"

FILE_ID = os.getenv('FILE_ID')
PDF_PATH = os.getenv('PDF_PATH')

SCOPES = ['https://www.googleapis.com/auth/drive']

def update_drive_file(file_id, file_path, service_account_file):
    creds = service_account.Credentials.from_service_account_file(
        service_account_file, 
        scopes=SCOPES
    )

    service = build('drive', 'v3', credentials=creds)

    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
    new_name = f"{os.path.splitext(os.path.basename(file_path))[0]}_{timestamp}.pdf"

    media = MediaFileUpload(file_path, mimetype='application/pdf', resumable=True)

    updated_file = service.files().update(
        fileId=file_id,
        media_body=media,
        body={'name': new_name}
    ).execute()

    print(f"File updated: {updated_file['name']} ({updated_file['id']})")

if __name__ == '__main__':
    if not SERVICE_ACCOUNT_FILE or not FILE_ID or not PDF_PATH:
        raise ValueError("Missing environment variables. Check your .env file.")
    
    loader = LoadingAnimation("Working")
    loader.start()

    time.sleep(2)
    # update_drive_file(FILE_ID, PDF_PATH, SERVICE_ACCOUNT_FILE)

    loader.stop()