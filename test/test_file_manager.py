from src.file_manager import copy_and_filter_files
import os

def test_file_manager():
    print("Testing file_manager module...")
    test_folder = "F:\\TestCard\\Photos_2025\\"
    success, backup_folder, media_files = copy_and_filter_files(test_folder)
    if success:
        print(f"Backup folder: {backup_folder}")
        print(f"Media files found: {len(media_files)}")
        if media_files:
            print(f"Sample media files: {[os.path.basename(f) for f in media_files[:5]]}")
    else:
        print("File copy failed or no files found.")

if __name__ == "__main__":
    test_file_manager()