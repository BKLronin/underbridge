import argparse
import os
import zipfile

def compress_folder_to_zip(folder_path, zip_file_path):
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, folder_path))

def main():
    parser = argparse.ArgumentParser(description="Compress a folder to a zip file")
    parser.add_argument("folder_path", help="Path to the folder to be compressed")
    parser.add_argument("zip_file_path", help="Path to the zip file to create")
    args = parser.parse_args()

    folder_path = args.folder_path
    zip_file_path = args.zip_file_path

    compress_folder_to_zip(folder_path, zip_file_path)
    print(f"Folder '{folder_path}' compressed to '{zip_file_path}' successfully.")

if __name__ == "__main__":
    main()