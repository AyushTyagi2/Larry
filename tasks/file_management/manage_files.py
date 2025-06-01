import os
import shutil

def search_files(directory, filename):
    found_paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if filename.lower() in file.lower():  # flexible partial match
                full_path = os.path.join(root, file)
                found_paths.append((file, full_path, root))  # include directory
    return found_paths


def rename_file(file_path, new_name):
    if os.path.exists(file_path):
        new_path = os.path.join(os.path.dirname(file_path), new_name)
        os.rename(file_path, new_path)
        print("File renamed successfully.")
    else:
        print("File not found.")

def move_file(file_path, target_directory):
    if os.path.exists(file_path) and os.path.isdir(target_directory):
        shutil.move(file_path, target_directory)
        print("File moved successfully.")
    else:
        print("File or directory not found.")

def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        print("File deleted successfully.")
    else:
        print("File not found.")
