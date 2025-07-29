import hashlib
import sqlite3
import os
import tkinter as tk
from tkinter import messagebox
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, filename="media_uploader.log", 
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Database configuration
DB_PATH = "file_hashes.db"

def compute_file_hash(file_path):
    """
    Compute SHA-256 hash of a file.
    
    Args:
        file_path (str): Path to the file.
    
    Returns:
        str: SHA-256 hash of the file, or None if error.
    """
    try:
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        file_hash = sha256.hexdigest()
        logger.debug(f"Computed hash for {file_path}: {file_hash}")
        return file_hash
    except Exception as e:
        logger.error(f"Error computing hash for {file_path}: {str(e)}")
        print(f"Error computing hash for {file_path}: {str(e)}")
        return None

def init_database():
    """
    Initialize SQLite database with a table for file hashes.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS file_hashes (
                    file_path TEXT PRIMARY KEY,
                    hash TEXT NOT NULL
                )
            """)
            conn.commit()
            logger.info("Initialized database: file_hashes.db")
    except sqlite3.Error as e:
        logger.error(f"Error initializing database: {str(e)}")
        print(f"Error initializing database: {str(e)}")

def check_duplicates(media_files):
    """
    Check for duplicate files using a SQLite database.
    
    Args:
        media_files (list): List of file paths to check (e.g., ['C:/Media_Backup/Photos_2025/image1.cr2']).
    
    Returns:
        tuple: (bool, list, list)
            - Success flag (True if successful, False otherwise)
            - List of unique file paths for upload
            - List of duplicate file paths (for reporting)
    """
    root = tk.Tk()
    root.withdraw()  # Hide main window

    try:
        # Initialize database
        init_database()

        unique_files = []
        duplicate_files = []

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            for file_path in media_files:
                if not os.path.exists(file_path):
                    logger.warning(f"File not found: {file_path}")
                    print(f"File not found: {file_path}")
                    continue

                file_hash = compute_file_hash(file_path)
                if not file_hash:
                    logger.warning(f"Skipping {file_path} due to hash computation error")
                    print(f"Skipping {file_path} due to hash computation error")
                    continue

                # Check if hash exists in database
                cursor.execute("SELECT file_path FROM file_hashes WHERE hash = ?", (file_hash,))
                result = cursor.fetchone()

                if result:
                    logger.info(f"Duplicate found: {file_path} (matches {result[0]})")
                    print(f"Duplicate found: {file_path}")
                    duplicate_files.append(file_path)
                else:
                    # Add to database and unique files
                    cursor.execute("INSERT INTO file_hashes (file_path, hash) VALUES (?, ?)", 
                                 (file_path, file_hash))
                    unique_files.append(file_path)
                    logger.info(f"Added unique file: {file_path}")
                    print(f"Added unique file: {file_path}")

            conn.commit()

        # Display summary
        total_files = len(media_files)
        unique_count = len(unique_files)
        duplicate_count = len(duplicate_files)

        if total_files == 0:
            logger.warning("No media files provided for duplicate checking")
            print("No media files provided")
            messagebox.showwarning("Warning", "No media files to check for duplicates.")
            root.destroy()
            return False, [], []

        message = (
            f"Duplicate check completed:\n"
            f"- Total files checked: {total_files}\n"
            f"- Unique files: {unique_count}\n"
            f"- Duplicates skipped: {duplicate_count}"
        )
        if duplicate_files:
            message += f"\n- Sample duplicates: {', '.join([os.path.basename(f) for f in duplicate_files[:5]])}{'...' if duplicate_count > 5 else ''}"
        logger.info(message)
        print(message)
        messagebox.showinfo("Duplicate Check", message)

        root.destroy()
        return True, unique_files, duplicate_files

    except sqlite3.Error as e:
        logger.error(f"Database error: {str(e)}")
        print(f"Database error: {str(e)}")
        messagebox.showerror("Error", f"Database error: {str(e)}. Contact support.")
        root.destroy()
        return False, [], []
    except Exception as e:
        logger.error(f"Error in check_duplicates: {str(e)}")
        print(f"Error in check_duplicates: {str(e)}")
        messagebox.showerror("Error", f"An error occurred: {str(e)}. Contact support.")
        root.destroy()
        return False, [], []

if __name__ == "__main__":
    # Test with sample files
    test_files = [
        "C:\\Media_Backup\\Photos_2025\\image1.cr2",
        "C:\\Media_Backup\\Photos_2025\\image2.nef",
        "C:\\Media_Backup\\Photos_2025\\video1.mp4",
        "C:\\Media_Backup\\Photos_2025\\image1.cr2"  # Duplicate
    ]
    print("Testing duplicate_checker module...")
    success, unique_files, duplicate_files = check_duplicates(test_files)
    if success:
        print(f"Unique files: {len(unique_files)}")
        if unique_files:
            print(f"Sample unique files: {[os.path.basename(f) for f in unique_files[:5]]}")
        print(f"Duplicate files: {len(duplicate_files)}")
        if duplicate_files:
            print(f"Sample duplicate files: {[os.path.basename(f) for f in duplicate_files[:5]]}")
    else:
        print("Duplicate check failed or no files provided.")