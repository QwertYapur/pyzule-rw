# Google Drive upload/download utilities for Telegram bot integration
import os
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/drive.file']
CREDENTIALS_FILE = 'client_secret_1072365080709-s89qg1q79978phe3cehdqi3nirkb5ptu.apps.googleusercontent.com.json'
TOKEN_FILE = 'token_drive.pickle'

def get_drive_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    return build('drive', 'v3', credentials=creds)

def upload_file_to_drive(filepath, drive_folder_id=None):
    service = get_drive_service()
    file_metadata = {'name': os.path.basename(filepath)}
    if drive_folder_id:
        file_metadata['parents'] = [drive_folder_id]
    media = MediaFileUpload(filepath, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id,webViewLink').execute()
    return file.get('id'), file.get('webViewLink')

def download_file_from_drive(file_id, destination):
    service = get_drive_service()
    request = service.files().get_media(fileId=file_id)
    with open(destination, 'wb') as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
    return destination
