from src.user_prompt import prompt_folder_name

def test_user_prompt():
    print("Testing user prompt module...")
    test_path = "F:\\TestCard\\"
    folder_path = prompt_folder_name(test_path)
    if folder_path:
        print(f"Selected folder path: {folder_path}")
    else:
        print("No folder selected or error occurred.")

if __name__ == "__main__":
    test_user_prompt()