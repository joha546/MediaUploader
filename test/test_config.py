from src.config import DESTINATION_PATH, SUPPORTED_EXTENSIONS, BACKUP_SUBFOLDER, load_email_credentials, validate_config
import os

def test_config():
    print("Testing config module...")
    print(f"DESTINATION_PATH: {DESTINATION_PATH}")
    print(f"SUPPORTED_EXTENSIONS: {SUPPORTED_EXTENSIONS}")
    print(f"BACKUP_SUBFOLDER: {BACKUP_SUBFOLDER}")

    # Test email credentials
    sender_email, app_password = load_email_credentials()
    if sender_email and app_password:
        print(f"Sender email: {sender_email}")
        print("App password: [Hidden for security]")
    else:
        print("Failed to load email credentials")

    # Test configuration validation
    success, message = validate_config()
    print(f"Configuration validation: {message}")

    # Test with invalid DESTINATION_PATH
    import src.config
    src.config.DESTINATION_PATH = "X:/Invalid_Path/"
    success, message = validate_config()
    print(f"Invalid DESTINATION_PATH test: {message}")

    # Reset DESTINATION_PATH
    src.config.DESTINATION_PATH = "C:/Media_Backup/"

if __name__ == "__main__":
    test_config()