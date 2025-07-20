import os
import argparse
import zipfile
import requests

def compress_folder_to_zip(folder_path, zip_file_path):
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, folder_path))

def authenticate_with_nextcloud(username, password, nextcloud_url):
    login_url = f"{nextcloud_url}/login"
    response = requests.post(login_url, auth=(username, password))
    if response.status_code == 200:
        print("Authentication successful")
        return True
    else:
        print("Authentication failed", response.status_code)
        return False

def upload_file_to_nextcloud(username, password, nextcloud_url, local_file_path, remote_file_path, windows=False):
    # For without Minstaller
    """if windows:
        compress_folder_to_zip(local_file_path, local_file_path + ".zip")"""
     # Update the local file path to point to the compressed zip file
    upload_url = f"{nextcloud_url}/remote.php/dav/files/{username}/{remote_file_path}"
    with open(local_file_path, 'rb') as file:
        headers = {'Content-Type': 'application/octet-stream'}
        response = requests.put(upload_url, data=file, auth=(username, password), headers=headers)
    if response.status_code == 201:
        print("File upload successful")
    else:
        print("File upload failed", response.status_code)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload file to Nextcloud")
    parser.add_argument("username", help="Nextcloud username")
    parser.add_argument("password", help="Nextcloud password")
    parser.add_argument("nextcloud_url", help="Nextcloud URL")
    parser.add_argument("local_file_path", help="Local file path")
    parser.add_argument("remote_file_path", help="Remote file path in Nextcloud")
    parser.add_argument("--windows", action="store_true", help="Flag to zip if running on Windows platform")

    args = parser.parse_args()

    if args.username and args.password:
        if authenticate_with_nextcloud(args.username, args.password, args.nextcloud_url):
            upload_file_to_nextcloud(args.username, args.password, args.nextcloud_url, args.local_file_path, args.remote_file_path, args.windows)
    else:
        print("Missing Nextcloud credentials.")
