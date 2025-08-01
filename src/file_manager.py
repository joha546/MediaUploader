import os
import shutil
import logging
from config import DESTINATION_PATH, SUPPORTED_EXTENSIONS, BACKUP_SUBFOLDER

# Configure logging
logging.basicConfig(level=logging.DEBUG, filename="media_uploader.log", 
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def copy_files(source_folder):
    """
    Copy supported media files from source_folder to DESTINATION_PATH/BACKUP_SUBFOLDER.
    
    Args:
        source_folder (str): Source folder path (e.g., 'F:\\TestCard\\Photos_2025\\').
    
    Returns:
        tuple: (bool, str, list)
            - Success flag (True if copied, False otherwise)
            - Message summarizing the result
            - List of copied file paths
    """
    try:
        if not os.path.exists(source_folder):
            logger.error(f"Source folder does not exist: {source_folder}")
            return False, f"Source folder does not exist: {source_folder}", []

        # Create destination folder
        dest_folder = os.path.join(DESTINATION_PATH, BACKUP_SUBFOLDER)
        os.makedirs(dest_folder, exist_ok=True)
        logger.info(f"Destination folder: {dest_folder}")

        copied_files = []
        for root, _, files in os.walk(source_folder):
            for file in files:
                if os.path.splitext(file)[1].lower() in SUPPORTED_EXTENSIONS:
                    src_path = os.path.join(root, file)
                    dest_path = os.path.join(dest_folder, file)
                    try:
                        shutil.copy2(src_path, dest_path)
                        copied_files.append(dest_path)
                        logger.info(f"Copied {src_path} to {dest_path}")
                    except Exception as e:
                        logger.error(f"Error copying {src_path}: {str(e)}")
                        continue

        if not copied_files:
            logger.warning("No supported files found to copy")
            return False, "No supported files found to copy", []

        message = f"Copied {len(copied_files)} files to {dest_folder}"
        logger.info(message)
        print(message)
        return True, message, copied_files

    except Exception as e:
        logger.error(f"Error in copy_files: {str(e)}")
        return False, f"Error copying files: {str(e)}", []