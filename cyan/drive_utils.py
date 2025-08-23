# Google Drive upload/download utilities for Telegram bot integration
import os
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError
from typing import Optional

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# These should be set as environment variables on your server
SERVICE_ACCOUNT_FILE = os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE") # Path to your service_account.json
DRIVE_FOLDER_ID = os.environ.get("GOOGLE_DRIVE_FOLDER_ID") # The ID of the folder to upload to
SCOPES = ['https://www.googleapis.com/auth/drive']

# --- Core Functions ---

def get_drive_service():
    """Authenticates with the Google Drive API using a service account."""
    if not SERVICE_ACCOUNT_FILE:
        logging.error("Error: GOOGLE_SERVICE_ACCOUNT_FILE environment variable not set.")
        return None
    
    try:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('drive', 'v3', credentials=creds)
        return service
    except FileNotFoundError:
        logging.error(f"Service account file not found at: {SERVICE_ACCOUNT_FILE}")
        return None
    except Exception as e:
        logging.error(f"Failed to create Drive service: {e}")
        return None
def find_file_by_name(service, filename: str, folder_id: str) -> Optional[str]:
    """Finds a file by name within a specific folder and returns its ID."""
    try:
        query = f"name = '{filename}' and '{folder_id}' in parents and trashed = false"
        response = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        files = response.get('files', [])
        
        if not files:
            logging.warning(f"File '{filename}' not found in Drive folder.")
            return None
        
        # Return the ID of the first matching file
        return files[0].get('id')
    except HttpError as e:
        logging.error(f"An error occurred while searching for file: {e}")
        return None

def _upload_single_file(service, file_path: str, folder_id: str) -> str:
    """
    (Internal function) Uploads a single file using a pre-existing service object.
    Returns a success or error message string.
    """
    if not os.path.exists(file_path):
        return f"Error: File not found at `{file_path}`."

    file_name = os.path.basename(file_path)
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    
    media = MediaFileUpload(file_path, resumable=True)
    
    try:
        logging.info(f"Uploading '{file_name}' to Google Drive...")
        file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        success_message = f"Successfully uploaded `{file_name}`.\nLink: {file.get('webViewLink')}"
        logging.info(success_message)
        return success_message
    except HttpError as e:
        error_message = f"An error occurred during upload: {e}"
        logging.error(error_message)
        return error_message

def upload_file_to_drive(file_path: str) -> str:
    """
    Public-facing function to upload a single file. It handles service creation.
    """
    if not DRIVE_FOLDER_ID:
        return "Error: `GOOGLE_DRIVE_FOLDER_ID` is not configured."

    service = get_drive_service()
    if not service:
        return "Error: Could not authenticate with Google Drive."
    
    return _upload_single_file(service, file_path, DRIVE_FOLDER_ID)
def download_file_from_drive(filename_or_id: str, destination: str) -> Optional[str]:
    """
    Downloads a file from Google Drive by its name or ID.
    If destination is a directory, the original filename is used.
    Returns the final file path on success, None on failure.
    """
    service = get_drive_service()
    if not service:
        logging.error("Download failed: Could not authenticate with Google Drive.")
        return None

    if not DRIVE_FOLDER_ID:
        logging.error("Download failed: GOOGLE_DRIVE_FOLDER_ID is not configured.")
        return None

    try:
        # First, try to find the file by name in the default folder
        file_id = find_file_by_name(service, filename_or_id, DRIVE_FOLDER_ID)
        
        # If not found by name, assume the input was a file ID
        if not file_id:
            file_id = filename_or_id
            logging.info(f"Could not find file by name '{filename_or_id}', assuming it is a file ID.")

        # Get file metadata to confirm existence and get the real name
        file_metadata = service.files().get(fileId=file_id, fields='name').execute()
        filename = file_metadata.get('name')

        # Determine the final destination path
        if os.path.isdir(destination):
            final_path = os.path.join(destination, filename)
        else:
            final_path = destination
        
        os.makedirs(os.path.dirname(final_path), exist_ok=True)

        logging.info(f"Downloading file '{filename}' (ID: {file_id}) to '{final_path}'...")
        request = service.files().get_media(fileId=file_id)
        
        with open(final_path, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    logging.info(f"Download {int(status.progress() * 100)}%.")
        
        logging.info(f"Successfully downloaded file to {final_path}")
        return final_path
    except HttpError as e:
        logging.error(f"An error occurred during download: {e}. Check if the file name or ID is correct.")
        return None
    except IsADirectoryError:
        logging.error(f"Error: The destination path '{destination}' is a directory. Please provide a full file path or a directory to save into.")
        return None

def upload_directory_to_drive(local_dir: str) -> dict[str, list[str]]:
    """
    Recursively uploads files in local_dir to the specified Google Drive folder.
    """
    if not DRIVE_FOLDER_ID:
        return {"success": [], "failed": ["Configuration error: GOOGLE_DRIVE_FOLDER_ID not set."]}

    service = get_drive_service()
    if not service:
        return {"success": [], "failed": ["Authentication error: Could not connect to Google Drive."]}

    exclude_dirs = {'.venv', '.git', '__pycache__', 'cyan/resources'}
    results = {"success": [], "failed": []}

    for root, dirs, files in os.walk(local_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for fname in files:
            fpath = os.path.join(root, fname)
            result_message = _upload_single_file(service, fpath, DRIVE_FOLDER_ID)
            if "Successfully uploaded" in result_message:
                results["success"].append(fpath)
            else:
                results["failed"].append(f"{fpath}: {result_message}")

    logging.info("Directory upload complete.")
    return results

def get_shareable_link(file_id: str) -> str:
    """Generate a shareable link for a Google Drive file."""
    if not file_id:
        logging.error("Cannot generate link: No file ID provided")
        return ""
    
    service = get_drive_service()
    if not service:
        logging.error("Cannot generate link: Drive service unavailable")
        return ""
    
    try:
        # Create a publicly accessible link
        service.permissions().create(
            fileId=file_id,
            body={"role": "reader", "type": "anyone"},
            fields="id"
        ).execute()
        
        # Get the webViewLink
        file = service.files().get(
            fileId=file_id,
            fields="webContentLink"
        ).execute()
        
        return file.get("webContentLink", "")
    except Exception as e:
        logging.error(f"Failed to generate shareable link: {e}")
        return ""

# --- Example Usage ---
if __name__ == "__main__":
    print("This script is intended to be used as a module. See function docstrings for usage details.")
