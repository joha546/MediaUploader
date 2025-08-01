from src.cloud_uploader import upload_to_drive

def test_cloud_uploader():
    print("Testing cloud_uploader module...")
    test_files = [
        "C:\\Media_Backup\\Photos_2025\\image1.cr2",
        "C:\\Media_Backup\\Photos_2025\\image2.nef",
        "C:\\Media_Backup\\Photos_2025\\video1.mp4"
    ]
    test_source_folder = "F:\\TestCard\\Photos_2025\\"
    success, uploaded_files = upload_to_drive(test_files, test_source_folder)
    if success:
        print(f"Uploaded files: {len(uploaded_files)}")
        for file_name, link in uploaded_files:
            print(f"{file_name}: {link}")
    else:
        print("Upload failed or no files uploaded.")

if __name__ == "__main__":
    test_cloud_uploader()