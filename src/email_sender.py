import tkinter as tk
from tkinter import messagebox, simpledialog
import smtplib
from email.mime.text import MIMEText
import re
import dns.resolver
import logging
from config import load_email_credentials, is_valid_email

# Configure logging
logging.basicConfig(level=logging.DEBUG, filename="media_uploader.log", 
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def check_mx_records(email):
    """
    Check if the email domain has valid MX records.
    
    Args:
        email (str): Email address to check.
    
    Returns:
        bool: True if domain has MX records, False otherwise.
    """
    try:
        domain = email.split('@')[1]
        dns.resolver.resolve(domain, 'MX')
        logger.info(f"MX records found for domain: {domain}")
        return True
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout) as e:
        logger.warning(f"No MX records for domain in {email}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error checking MX records for {email}: {str(e)}")
        return False

def prompt_recipient_email():
    """
    Prompt user for recipient email using tkinter and validate format and MX records.
    
    Returns:
        str: Recipient email, or None if cancelled or invalid.
    """
    root = tk.Tk()
    root.withdraw()  # Hide main window

    try:
        recipient_email = simpledialog.askstring("Input", "Enter recipient email address:", parent=root)
        if not recipient_email:
            logger.info("Recipient email prompt cancelled by user")
            root.destroy()
            return None
        if not is_valid_email(recipient_email):
            logger.warning(f"Invalid recipient email format: {recipient_email}")
            messagebox.showerror("Error", "Invalid recipient email address format.")
            root.destroy()
            return None
        if not check_mx_records(recipient_email):
            logger.warning(f"No MX records for recipient email domain: {recipient_email}")
            messagebox.showwarning("Warning", 
                f"The email domain for {recipient_email} may not exist. The email may not be delivered. Continue anyway?",
                type=messagebox.YESNO)
            response = messagebox.askyesno("Confirm", "Send email despite potential delivery issue?")
            if not response:
                logger.info("Email sending cancelled due to invalid domain")
                root.destroy()
                return None
        root.destroy()
        return recipient_email
    except Exception as e:
        logger.error(f"Error prompting recipient email: {str(e)}")
        messagebox.showerror("Error", f"Error prompting recipient email: {str(e)}")
        root.destroy()
        return None

def send_email(uploaded_files, source_folder):
    """
    Send an email with shareable Google Drive links to the recipient.
    
    Args:
        uploaded_files (list): List of tuples (file_name, shareable_link) from cloud_uploader.
        source_folder (str): Source folder path (e.g., 'F:\\TestCard\\Photos_2025\\') for context.
    
    Returns:
        tuple: (bool, str)
            - Success flag (True if email sent, False otherwise)
            - Message summarizing the result
    """
    root = tk.Tk()
    root.withdraw()  # Hide main window

    try:
        if not uploaded_files:
            logger.warning("No files to email")
            messagebox.showwarning("Warning", "No files to email.")
            root.destroy()
            return False, "No files to email"

        # Load sender credentials from config
        sender_email, app_password = load_email_credentials()
        if not sender_email or not app_password:
            logger.warning("Email sending cancelled due to invalid or missing credentials")
            messagebox.showerror("Error", "Invalid or missing credentials in email_credentials.json.")
            root.destroy()
            return False, "Invalid or missing credentials"

        # Prompt for recipient email
        recipient_email = prompt_recipient_email()
        if not recipient_email:
            logger.warning("Email sending cancelled due to missing or invalid recipient email")
            messagebox.showwarning("Warning", "Email sending cancelled.")
            root.destroy()
            return False, "Email sending cancelled"

        # Prepare email content
        folder_name = os.path.basename(os.path.normpath(source_folder))
        subject = f"Media Upload: Shareable Links for {folder_name}"
        body = (
            f"Dear Recipient,\n\n"
            f"The following files from {folder_name} have been uploaded to Google Drive:\n\n"
        )
        for file_name, link in uploaded_files:
            body += f"- {file_name}: {link}\n"
        body += (
            "\nClick the links to access the files.\n\n"
            "Note: If you cannot receive this email, it may be due to an invalid email address.\n"
            "Best regards,\nMediaCardUploader"
        )

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient_email

        # Send email via Gmail SMTP
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, app_password)
                server.send_message(msg)
                logger.info(f"Email sent to {recipient_email} with {len(uploaded_files)} links")
                print(f"Email sent to {recipient_email}")

            # Display summary
            message = (
                f"Email sent successfully:\n"
                f"- Recipient: {recipient_email}\n"
                f"- Files: {len(uploaded_files)}\n"
                f"- Sample links:\n"
            )
            for file_name, link in uploaded_files[:3]:
                message += f"  {file_name}: {link}\n"
            if len(uploaded_files) > 3:
                message += "...\n"
            message += "Note: If the recipient email does not exist, you may receive a bounce-back notification."
            logger.info(message)
            print(message)
            messagebox.showinfo("Email Sent", message)

            root.destroy()
            return True, message

        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed: Invalid Gmail email or app-specific password")
            messagebox.showerror("Error", "Invalid Gmail email or app-specific password in email_credentials.json.")
            root.destroy()
            return False, "Authentication failed"
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {str(e)}")
            messagebox.showerror("Error", f"Failed to send email: {str(e)}. Check internet and try again.")
            root.destroy()
            return False, f"SMTP error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error sending email: {str(e)}")
            messagebox.showerror("Error", f"Unexpected error: {str(e)}. Contact support.")
            root.destroy()
            return False, f"Unexpected error: {str(e)}"

    except Exception as e:
        logger.error(f"Error in send_email: {str(e)}")
        messagebox.showerror("Error", f"An error occurred: {str(e)}. Contact support.")
        root.destroy()
        return False, f"Error: {str(e)}"

if __name__ == "__main__":
    # Test with sample uploaded files
    test_files = [
        ("image1.cr2", "https://drive.google.com/file/d/123/view?usp=sharing"),
        ("image2.nef", "https://drive.google.com/file/d/456/view?usp=sharing"),
        ("video1.mp4", "https://drive.google.com/file/d/789/view?usp=sharing")
    ]
    test_source_folder = "F:\\TestCard\\Photos_2025\\"
    print("Testing email_sender module...")
    success, message = send_email(test_files, test_source_folder)
    if success:
        print("Email sent successfully:")
        print(message)
    else:
        print(f"Email sending failed: {message}")