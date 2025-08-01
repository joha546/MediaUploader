from src.email_sender import send_email

def test_email_sender():
    print("Testing email_sender module...")
    test_files = [
        ("image1.cr2", "https://drive.google.com/file/d/123/view?usp=sharing"),
        ("image2.nef", "https://drive.google.com/file/d/456/view?usp=sharing"),
        ("video1.mp4", "https://drive.google.com/file/d/789/view?usp=sharing")
    ]
    test_source_folder = "F:\\TestCard\\Photos_2025\\"
    success, message = send_email(test_files, test_source_folder)
    if success:
        print("Email sent successfully:")
        print(message)
    else:
        print(f"Email sending failed: {message}")

if __name__ == "__main__":
    test_email_sender()