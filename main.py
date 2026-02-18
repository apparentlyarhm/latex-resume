import os
import itertools
import threading
import time
import sys
import shutil

from pathlib import Path
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
HDD_PATH = os.getenv('HDD_PATH')

SCOPES = ['https://www.googleapis.com/auth/drive']

# separated this if in case this has to be reused in the future
def name_gen(file_path: str):
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
    base = os.path.splitext(os.path.basename(file_path))[0]
    
    return f"{base}_{timestamp}.pdf"


def gdrive_sync(file_id, file_path, service_account_file, name):
    creds = service_account.Credentials.from_service_account_file(
        service_account_file, 
        scopes=SCOPES
    )

    service = build('drive', 'v3', credentials=creds)
    media = MediaFileUpload(file_path, mimetype='application/pdf', resumable=True)

    updated_file = service.files().update(
        fileId=file_id,
        media_body=media,
        body={'name': name}
    ).execute()

    print(f"File updated: {updated_file['name']} ({updated_file['id']})")

def hdd_sync(hdd_path, pdf_path):
    dest = Path(hdd_path) / pdf_path
    shutil.copy2(pdf_path, dest)

    print(f"HDD mirrored: {dest}")

if __name__ == '__main__':
    if not SERVICE_ACCOUNT_FILE or not FILE_ID or not PDF_PATH or not HDD_PATH:
        raise ValueError("Missing environment variables. Check your .env file.")
    
    loader = LoadingAnimation("Working")
    loader.start()

    ver = name_gen(PDF_PATH)

    time.sleep(2)
    gdrive_sync(FILE_ID, PDF_PATH, SERVICE_ACCOUNT_FILE, ver)
    hdd_sync(HDD_PATH, PDF_PATH)

    loader.stop()