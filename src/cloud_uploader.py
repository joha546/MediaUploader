import os
import tkinter as tk
from tkinter import messagebox
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, filename="media_uploader.log", 
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Google Drive API configuration
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"

def authenticate_drive():
    """
    Authenticate with Google Drive API using OAuth 2.0.
    
    Returns:
        googleapiclient.discovery.Resource: Authenticated Drive API service, or None if failed.
    """
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials

        creds = None
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(TOKEN_FILE, "w") as token:
                token.write(creds.to_json())
        
        service = build("drive", "v3", credentials=creds)
        logger.info("Authenticated with Google Drive API")
        print("Authenticated with Google Drive API")
        return service
    
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        print(f"Authentication error: {str(e)}")
        return None

def create_drive_folder(service, folder_name):
    """
    Create a folder in Google Drive if it doesn't exist.
    
    Args:
        service: Authenticated Drive API service.
        folder_name (str): Name of the folder (e.g., 'Photos_2025').
    
    Returns:
        str: Google Drive folder ID, or None if failed.
    """
    try:
        # Check if folder exists
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = service.files().list(q=query, spaces="drive", fields="files(id, name)").execute()
        folders = results.get("files", [])

        if folders:
            folder_id = folders[0]["id"]
            logger.info(f"Found existing Google Drive folder: {folder_name} (ID: {folder_id})")
            print(f"Found existing Google Drive folder: {folder_name}")
            return folder_id

        # Create new folder
        file_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder"
        }
        folder = service.files().create(body=file_metadata, fields="id").execute()
        folder_id = folder.get("id")
        logger.info(f"Created Google Drive folder: {folder_name} (ID: {folder_id})")
        print(f"Created Google Drive folder: {folder_name}")
        return folder_id
    
    except Exception as e:
        logger.error(f"Error creating folder {folder_name}: {str(e)}")
        print(f"Error creating folder {folder_name}: {str(e)}")
        return None

def upload_to_drive(unique_files, source_folder):
    """
    Upload unique files to Google Drive and generate shareable links.
    
    Args:
        unique_files (list): List of file paths to upload (e.g., ['C:/Media_Backup/Photos_2025/image1.cr2']).
        source_folder (str): Source folder path (e.g., 'F:\\TestCard\\Photos_2025\\') to extract folder name.
    
    Returns:
        tuple: (bool, list)
            - Success flag (True if all files uploaded, False otherwise)
            - List of tuples (file_name, shareable_link) for uploaded files
    """
    root = tk.Tk()
    root.withdraw()  # Hide main window

    try:
        # Authenticate
        service = authenticate_drive()
        if not service:
            messagebox.showerror("Error", "Failed to authenticate with Google Drive. Check credentials.json and try again.")
            root.destroy()
            return False, []

        # Extract folder name from source_folder
        folder_name = os.path.basename(os.path.normpath(source_folder))
        folder_id = create_drive_folder(service, folder_name)
        if not folder_id:
            messagebox.showerror("Error", f"Failed to create Google Drive folder '{folder_name}'.")
            root.destroy()
            return False, []

        uploaded_files = []
        upload_count = 0
        total_files = len(unique_files)

        for file_path in unique_files:
            if not os.path.exists(file_path):
                logger.warning(f"File not found: {file_path}")
                print(f"File not found: {file_path}")
                continue

            file_name = os.path.basename(file_path)
            try:
                # Upload file
                file_metadata = {
                    "name": file_name,
                    "parents": [folder_id]
                }
                media = MediaFileUpload(file_path)
                file = service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields="id"
                ).execute()
                file_id = file.get("id")

                # Generate shareable link
                service.permissions().create(
                    fileId=file_id,
                    body={"role": "reader", "type": "anyone"}
                ).execute()
                link = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
                
                uploaded_files.append((file_name, link))
                upload_count += 1
                logger.info(f"Uploaded {file_name} to Google Drive (ID: {file_id}, Link: {link})")
                print(f"Uploaded {file_name} to Google Drive: {link}")

            except Exception as e:
                logger.error(f"Error uploading {file_name}: {str(e)}")
                print(f"Error uploading {file_name}: {str(e)}")

        if upload_count == 0 and total_files > 0:
            logger.error("No files were uploaded")
            print("No files were uploaded")
            messagebox.showerror("Error", "Failed to upload any files. Check files and try again.")
            root.destroy()
            return False, []

        # Display summary
        message = (
            f"Upload completed:\n"
            f"- Total files processed: {total_files}\n"
            f"- Files uploaded: {upload_count}\n"
            f"- Files skipped: {total_files - upload_count}"
        )
        if uploaded_files:
            message += f"\n- Sample file links:\n"
            for file_name, link in uploaded_files[:3]:  # Show up to 3 links
                message += f"  {file_name}: {link}\n"
            if len(uploaded_files) > 3:
                message += "..."
        logger.info(message)
        print(message)
        messagebox.showinfo("Upload Completed", message)

        root.destroy()
        return True, uploaded_files

    except Exception as e:
        logger.error(f"Error in upload_to_drive: {str(e)}")
        print(f"Error in upload_to_drive: {str(e)}")
        messagebox.showerror("Error", f"An error occurred: {str(e)}. Contact support.")
        root.destroy()
        return False, []

if __name__ == "__main__":
    # Test with sample files
    test_files = [
        "C:\\Media_Backup\\Goku.jpg"
    ]
    test_source_folder = "C:\\Media_Backup\\"
    print("Testing cloud_uploader module...")
    success, uploaded_files = upload_to_drive(test_files, test_source_folder)
    if success:
        print(f"Uploaded files: {len(uploaded_files)}")
        for file_name, link in uploaded_files:
            print(f"{file_name}: {link}")
    else:
        print("Upload failed or no files uploaded.")