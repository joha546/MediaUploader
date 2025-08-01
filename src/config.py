import os
import json
import re
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, filename="media_uploader.log", 
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Configuration file for email credentials
EMAIL_CREDENTIALS_FILE = "email_credentials.json"

# Default configurations
DESTINATION_PATH = "C:/Media_Backup/"
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".cr2", ".nef", ".mp4", ".mov"}
BACKUP_SUBFOLDER = "Photos_2025"  # Example subfolder, can be overridden
LOG_FILE = "media_uploader.log"

def is_valid_email(email):
    """
    Validate email address format.
    
    Args:
        email (str): Email address to validate.
    
    Returns:
        bool: True if format is valid, False otherwise.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def load_email_credentials():
    """
    Load sender email and app-specific password from email_credentials.json.
    
    Returns:
        tuple: (sender_email, app_password), or (None, None) if error.
    """
    try:
        if not os.path.exists(EMAIL_CREDENTIALS_FILE):
            logger.error(f"Email credentials file not found: {EMAIL_CREDENTIALS_FILE}")
            return None, None
        with open(EMAIL_CREDENTIALS_FILE, "r") as f:
            creds = json.load(f)
            sender_email = creds.get("sender_email")
            app_password = creds.get("app_password")
            if not sender_email or not app_password:
                logger.error("Missing sender_email or app_password in email_credentials.json")
                return None, None
            if not is_valid_email(sender_email):
                logger.error(f"Invalid sender email format: {sender_email}")
                return None, None
            logger.info("Loaded email credentials successfully")
            return sender_email, app_password
    except Exception as e:
        logger.error(f"Error loading email credentials: {str(e)}")
        return None, None

def validate_config():
    """
    Validate configuration settings.
    
    Returns:
        tuple: (bool, str)
            - Success flag (True if valid, False otherwise)
            - Error message if invalid
    """
    try:
        # Validate DESTINATION_PATH
        if not os.path.isdir(os.path.dirname(DESTINATION_PATH)):
            logger.error(f"Invalid DESTINATION_PATH directory: {DESTINATION_PATH}")
            return False, f"Invalid DESTINATION_PATH directory: {DESTINATION_PATH}"
        
        # Validate SUPPORTED_EXTENSIONS
        if not SUPPORTED_EXTENSIONS or not all(ext.startswith(".") for ext in SUPPORTED_EXTENSIONS):
            logger.error("SUPPORTED_EXTENSIONS must be non-empty and start with '.'")
            return False, "SUPPORTED_EXTENSIONS must be non-empty and start with '.'"
        
        # Validate email credentials
        sender_email, app_password = load_email_credentials()
        if not sender_email or not app_password:
            logger.error("Invalid or missing email credentials")
            return False, f"Invalid or missing email credentials in {EMAIL_CREDENTIALS_FILE}"
        
        logger.info("Configuration validated successfully")
        return True, "Configuration validated successfully"
    except Exception as e:
        logger.error(f"Error validating configuration: {str(e)}")
        return False, f"Error validating configuration: {str(e)}"