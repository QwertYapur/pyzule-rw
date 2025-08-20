#!/usr/bin/env python3

from cyan.drive_utils import upload_file_to_drive, download_file_from_drive

if __name__ == "__main__":
    # Create a test file to upload
    test_filename = "test_upload.txt"
    with open(test_filename, "w") as f:
        f.write("This is a test file for Google Drive upload.")

    print(f"Uploading {test_filename} to Google Drive...")
    file_id = upload_file_to_drive(test_filename)
    print(f"Uploaded file ID: {file_id}")

    if file_id:
        download_path = "downloaded_test.txt"
        print(f"Downloading file with ID {file_id} to {download_path}...")
        download_file_from_drive(file_id, download_path)
        print(f"Downloaded file to: {download_path}")
    else:
        print("Upload failed; skipping download.")
