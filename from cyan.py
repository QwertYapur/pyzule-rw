from cyan.drive_utils import upload_file_to_drive, download_file_from_drive

# Upload a file to Google Drive
file_path = "test_upload.txt"  # Path to the file you want to upload
file_id = upload_file_to_drive(file_path)
print(f"Uploaded file ID: {file_id}")

# Download the file back from Google Drive
if file_id:
    download_path = "downloaded_test.txt"
    download_file_from_drive(file_id, download_path)
    print(f"Downloaded file to: {download_path}")