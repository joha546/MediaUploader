import os
import shutil
import pathlib
import tkinter as tk
from tkinter import messagebox
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, filename="media_uploader.log", 
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Configuration
BACKUP_PATH = "C:/Media_Backup"
RAW_EXTENSIONS = {".raw", ".cr2", ".nef"}
VIDEO_EXTENSIONS = {".mp4", ".mov"}

def copy_and_filter_files(source_folder):
    """
    Copy all files from source_folder to a local backup directory and filter
    raw images and videos for upload.
    
    Args:
        source_folder (str): Path to the source folder (e.g., 'F:\\TestCard\\Photos_2025\\').
    
    Returns:
        tupleconclusion tuple: (bool, str, list)
            - Success flag (True if successful, False otherwise)
            - Path to the backup folder (e.g., 'C:\\Media_Backup\\Photos_2025\\')
            - List of paths to raw image and video files for upload
    """
    root = tk.Tk()
    root.withdraw()  # Hide main window

    try:
        # Validate source folder
        if not source_folder or not os.path.exists(source_folder):
            logger.error(f"Invalid source folder: {source_folder}")
            print(f"Invalid source folder: {source_folder}")
            messagebox.showerror("Error", f"Source folder '{source_folder}' does not exist.")
            root.destroy()
            return False, None, []

        # Extract folder name for backup path
        folder_name = os.path.basename(os.path.normpath(source_folder))
        backup_folder = os.path.join(BACKUP_PATH, folder_name)
        os.makedirs(backup_folder, exist_ok=True)
        logger.info(f"Created backup folder: {backup_folder}")
        print(f"Created backup folder: {backup_folder}")

        # Copy files and filter media
        media_files = []
        file_count = 0
        copied_files = 0

        for root_dir, _, files in os.walk(source_folder):
            for file in files:
                file_count += 1
                src_path = os.path.join(root_dir, file)
                relative_path = os.path.relpath(src_path, source_folder)
                dst_path = os.path.join(backup_folder, relative_path)

                # Create destination subdirectories if needed
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)

                try:
                    shutil.copy2(src_path, dst_path)
                    copied_files += 1
                    logger.info(f"Copied {src_path} to {dst_path}")
                    print(f"Copied {src_path} to {dst_path}")

                    # Filter raw images and videos
                    ext = pathlib.Path(file).suffix.lower()
                    if ext in RAW_EXTENSIONS or ext in VIDEO_EXTENSIONS:
                        media_files.append(dst_path)
                        logger.info(f"Filtered media file: {dst_path}")
                        print(f"Filtered media file: {dst_path}")

                except Exception as e:
                    logger.error(f"Error copying {src_path}: {str(e)}")
                    print(f"Error copying {src_path}: {str(e)}")

        if file_count == 0:
            logger.warning(f"No files found in {source_folder}")
            print(f"No files found in {source_folder}")
            messagebox.showwarning("Warning", f"No files found in '{source_folder}'. Ensure the folder contains files.")
            root.destroy()
            return False, None, []

        if copied_files == 0:
            logger.error(f"No files were copied from {source_folder}")
            print(f"No files were copied from {source_folder}")
            messagebox.showerror("Error", f"Failed to copy files from '{source_folder}'. Check permissions and try again.")
            root.destroy()
            return False, None, []

        # Display summary
        media_count = len(media_files)
        message = (
            f"Copy completed:\n"
            f"- Source: {source_folder}\n"
            f"- Backup: {backup_folder}\n"
            f"- Total files copied: {copied_files}\n"
            f"- Raw images/videos found: {media_count}"
        )
        if media_files:
            message += f"\n- Sample files: {', '.join([os.path.basename(f) for f in media_files[:5]])}{'...' if media_count > 5 else ''}"
        logger.info(message)
        print(message)
        messagebox.showinfo("Copy Completed", message)

        root.destroy()
        return True, backup_folder, media_files

    except Exception as e:
        logger.error(f"Error in copy_and_filter_files: {str(e)}")
        print(f"Error in copy_and_filter_files: {str(e)}")
        messagebox.showerror("Error", f"An error occurred: {str(e)}. Contact support.")
        root.destroy()
        return False, None, []

if __name__ == "__main__":
    # Test with a sample folder
    test_folder = "E:\\Movies\\"
    print(f"Testing file_manager with folder: {test_folder}")
    success, backup_folder, media_files = copy_and_filter_files(test_folder)
    if success:
        print(f"Backup folder: {backup_folder}")
        print(f"Media files for upload: {len(media_files)}")
        if media_files:
            print(f"Sample media files: {[os.path.basename(f) for f in media_files[:5]]}")
    else:
        print("File copy failed or no files found.")