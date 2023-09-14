import os
import shutil
import argparse
import time
import hashlib

def get_md5(file_path):
    """Calculating the MD5 hash of an input file."""
    md5 = hashlib.md5()
    with open(file_path, 'rb') as file:
        while chunk_data := file.read(8192):
            md5.update(chunk_data)
    return md5.hexdigest()

def sync_the_folders(source_folder, replica_folder, log_file, interval):
    """Perform the folder synchronization"""
    while True:
        # List all files and folders in the source and replica folders with their MD5 hashes
        source_data_items = {}
        for root, dirs, files in os.walk(source_folder):
            relative_path = os.path.relpath(root, source_folder)
            for dir_name in dirs:
                source_data_items[os.path.join(relative_path, dir_name)] = None
            for file_name in files:
                source_path = os.path.join(root, file_name)
                source_data_items[os.path.join(relative_path, file_name)] = get_md5(source_path)

        replica_items = {}
        for root, dirs, files in os.walk(replica_folder):
            relative_path = os.path.relpath(root, replica_folder)
            for dir_name in dirs:
                replica_items[os.path.join(relative_path, dir_name)] = None
            for file_name in files:
                replica_path = os.path.join(root, file_name)
                replica_items[os.path.join(relative_path, file_name)] = get_md5(replica_path)

        # Copy or update files and folders from source to replica
        for item_path, md5_source in source_data_items.items():
            replica_path = os.path.join(replica_folder, item_path)

            if item_path in replica_items and md5_source == replica_items[item_path]:
                continue

            if md5_source is None:
                # It's a directory, create it in the replica
                os.makedirs(replica_path, exist_ok=True)
                print(f"Created directory: {item_path}")
                with open(log_file, 'a') as log:
                    log.write(f"Created directory: {item_path}\n")
            else:
                # It's a file, copy it to the replica
                shutil.copy2(os.path.join(source_folder, item_path), replica_path)
                print(f"Copied/Updated: {item_path}")
                with open(log_file, 'a') as log:
                    log.write(f"Copied/Updated: {item_path}\n")

        # Delete items from replica that don't exist in source
        for item_path, md5_replica in replica_items.items():
            source_path = os.path.join(source_folder, item_path)
            if not os.path.exists(source_path) or md5_replica != source_data_items.get(item_path):
                item_path_full = os.path.join(replica_folder, item_path)
                if os.path.isdir(item_path_full):
                    shutil.rmtree(item_path_full)
                    print(f"Deleted directory: {item_path}")
                    with open(log_file, 'a') as log:
                        log.write(f"Deleted directory: {item_path}\n")
                else:
                    os.remove(item_path_full)
                    print(f"Deleted file: {item_path}")
                    with open(log_file, 'a') as log:
                        log.write(f"Deleted file: {item_path}\n")

        time.sleep(interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synchronize two folders using MD5 hashes.'")
    parser.add_argument("source_folder", type=str, help="Path to the source folder")
    parser.add_argument("replica_folder", type=str, help="Path to the replica folder")
    parser.add_argument("log_file", type=str, help="Path to the log file")
    parser.add_argument("interval", type=int, help="Synchronization interval in seconds")

    args = parser.parse_args()

    sync_the_folders(args.source_folder, args.replica_folder, args.log_file, args.interval)
    # Arguments example 'C:\Test_Folder_Synch\Eshant_1' 'C:\Test_Folder_Synch\Eshant_2' 'C:\Test_Folder_Synch\logs.log' '2'