import os
import tkinter as tk
from tkinter import messagebox, simpledialog
import logging
import re

# Configure logging
logging.basicConfig(level=logging.DEBUG, filename="media_uploader.log", 
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def prompt_folder_name(detected_path):
    """
    Prompt user for a folder name on the detected path (e.g., 'F:\\TestCard\\').
    Validates the folder exists and contains files, then returns the full path.
    
    Args:
        detected_path (str): Path from card_detector (e.g., 'F:\\TestCard\\').
    
    Returns:
        str: Full path to the selected folder (e.g., 'F:\\TestCard\\Photos_2025\\'),
             or None if invalid or cancelled.
    """
    root = tk.Tk()
    root.withdraw()  # Hide main window

    try:
        # Validate detected_path
        if not detected_path or not os.path.exists(detected_path):
            logger.error(f"Invalid detected path: {detected_path}")
            messagebox.showerror("Error", f"Invalid path: {detected_path}. Please try again.")
            root.destroy()
            return None

        logger.info(f"Prompting for folder name on path: {detected_path}")
        print(f"Prompting for folder name on path: {detected_path}")

        # Prompt for folder name
        folder_name = simpledialog.askstring(
            "Folder Name",
            f"Enter the folder name on {detected_path}\n(e.g., 'Photos_2025' or 'DCIM'):",
            parent=root
        )

        if not folder_name:
            logger.warning("Folder name prompt cancelled or empty")
            print("Folder name prompt cancelled or empty")
            messagebox.showerror("Error", "No folder name entered. Please try again.")
            root.destroy()
            return None

        # Validate folder name (no invalid characters, non-empty)
        invalid_chars = r'[<>:"/\\|?*]'
        if re.search(invalid_chars, folder_name):
            logger.error(f"Invalid folder name: {folder_name} (contains invalid characters)")
            print(f"Invalid folder name: {folder_name}")
            messagebox.showerror("Error", f"Folder name '{folder_name}' contains invalid characters. Use letters, numbers, or underscores.")
            root.destroy()
            return None

        # Construct full folder path
        folder_path = os.path.join(detected_path, folder_name)
        if not folder_path.endswith("\\"):
            folder_path += "\\"

        # Check if folder exists
        if not os.path.exists(folder_path):
            logger.error(f"Folder does not exist: {folder_path}")
            print(f"Folder does not exist: {folder_path}")
            messagebox.showerror("Error", f"Folder '{folder_name}' not found on {detected_path}. Please check the name and try again.")
            root.destroy()
            return None

        # List files in the folder
        try:
            files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            if not files:
                logger.warning(f"No files found in folder: {folder_path}")
                print(f"No files found in folder: {folder_path}")
                messagebox.showwarning(
                    "Warning",
                    f"Folder '{folder_name}' is empty.\nEnsure it contains images or videos, then try again."
                )
                root.destroy()
                return None

            # Filter for images/videos (for display only)
            image_video_extensions = {'.jpg', '.jpeg', '.png', '.raw', '.cr2', '.nef', '.mp4', '.mov'}
            media_files = [f for f in files if os.path.splitext(f)[1].lower() in image_video_extensions]
            file_message = f"Selected folder: {folder_path}\nFiles found: {len(files)}\n"
            if media_files:
                file_message += f"Images/Videos: {', '.join(media_files[:5])}{'...' if len(media_files) > 5 else ''}"
            else:
                file_message += "No images or videos found."

            logger.info(f"Folder selected: {folder_path} with {len(files)} files ({len(media_files)} images/videos)")
            print(f"Folder selected: {folder_path}")
            print(f"Files found: {len(files)}")
            print(f"Images/Videos: {len(media_files)}")
            if media_files:
                print(f"Sample media files: {media_files[:5]}")

            # Show confirmation
            messagebox.showinfo("Folder Selected", file_message)
            root.destroy()
            return folder_path

        except Exception as e:
            logger.error(f"Error accessing folder {folder_path}: {str(e)}")
            print(f"Error accessing folder: {str(e)}")
            messagebox.showerror("Error", f"Cannot access folder '{folder_name}': {str(e)}")
            root.destroy()
            return None

    except Exception as e:
        logger.error(f"Error in prompt_folder_name: {str(e)}")
        print(f"Error in prompt_folder_name: {str(e)}")
        messagebox.showerror("Error", f"An error occurred: {str(e)}. Contact support.")
        root.destroy()
        return None

if __name__ == "__main__":
    # Test with a sample path
    test_path = "F:\\MediaUploader\\"
    print(f"Testing user_prompt with path: {test_path}")
    folder_path = prompt_folder_name(test_path)
    if folder_path:
        print(f"Selected folder path: {folder_path}")
    else:
        print("No folder selected")