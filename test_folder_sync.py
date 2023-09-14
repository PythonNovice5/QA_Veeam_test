import os
import shutil
import argparse
import time
import hashlib
import sys

def check_paths(source_folder, replica_folder, log_file):
    if not os.path.exists(source_folder) or not os.path.exists(replica_folder):
        raise FileNotFoundError("Source or replica folder does not exist.")
    
    if log_file:
        if not os.path.isdir(os.path.dirname(log_file)):
            raise FileNotFoundError("Log file directory does not exist. Please provide a valid absolute log file path")  
                    
        try:
            with open(log_file, 'a') as log:
                print(f"log file is created",flush=True)
        except Exception as e:
            raise Exception(f"Failed to create log file: {e}")

def check_permissions(source_folder, replica_folder):
    # Check if the source directory has read permission
    if not os.access(source_folder, os.R_OK):
        print(f"Source directory '{source_folder}' does not have read permission.")
        sys.exit(1)

    print(f"Source folder: '{source_folder}' has read permission.")

    # Check if the target directory has write permission
    if not os.access(replica_folder, os.W_OK):
        print(f"Replica directory '{replica_folder}' does not have write permission.")
        sys.exit(1)
    print(f"Replica directory '{replica_folder}' has write permission.")


def get_md5(file_path):
    """Calculating the MD5 hash of an input file."""
    md5 = hashlib.md5()
    with open(file_path, 'rb') as file:
        while chunk_data := file.read(8192):
            md5.update(chunk_data)
    return md5.hexdigest()

def get_timestamp():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def get_source_data(source_folder):
    source_data_items = {}
    for root, dirs, files in os.walk(source_folder):
        relative_path = os.path.relpath(root, source_folder)
        for dir_name in dirs:
            source_data_items[os.path.join(relative_path, dir_name)] = None
        for file_name in files:
            source_path = os.path.join(root, file_name)
            source_data_items[os.path.join(relative_path, file_name)] = get_md5(source_path)
    return source_data_items        

def get_replica_data(replica_folder):
    replica_items = {}
    for root, dirs, files in os.walk(replica_folder):
        relative_path = os.path.relpath(root, replica_folder)
        for dir_name in dirs:
            replica_items[os.path.join(relative_path, dir_name)] = None
        for file_name in files:
            replica_path = os.path.join(root, file_name)
            replica_items[os.path.join(relative_path, file_name)] = get_md5(replica_path)
    return replica_items             

def copy_update_data(source_folder, replica_folder, source_data_items, replica_items, log_file):
    for item_path, md5_source in source_data_items.items():
        replica_path = os.path.join(replica_folder, item_path)

        if item_path in replica_items and md5_source == replica_items[item_path]:
            continue

        if md5_source is None:
            # It's a directory, create it in the replica
            os.makedirs(replica_path, exist_ok=True)
            print(f"Created directory: {item_path}",flush=True)
            with open(log_file, 'a') as log:
                log.write(f"[{get_timestamp()}] Created directory: {item_path}\n")
        else:
            # It's a file, copy it to the replica
            shutil.copy2(os.path.join(source_folder, item_path), replica_path)
            print(f"Copied/Updated: {item_path}",flush=True)
            with open(log_file, 'a') as log:
                log.write(f"[{get_timestamp()}] Copied/Updated: {item_path}\n")   


def delete_data(source_folder, replica_folder, source_data_items, replica_items, log_file):
    for item_path, md5_replica in replica_items.items():
        source_path = os.path.join(source_folder, item_path)
        if not os.path.exists(source_path) or md5_replica != source_data_items.get(item_path):
            item_path_full = os.path.join(replica_folder, item_path)
            if os.path.isdir(item_path_full):
                shutil.rmtree(item_path_full)
                print(f"Deleted directory: {item_path}",flush=True)
                with open(log_file, 'a') as log:
                    log.write(f"[{get_timestamp()}] Deleted directory: {item_path}\n")
            else:
                os.remove(item_path_full)
                print(f"Deleted file: {item_path}",flush=True)
                with open(log_file, 'a') as log:
                    log.write(f"[{get_timestamp()}] Deleted file: {item_path}\n")


def sync_the_folders(source_folder, replica_folder, log_file, interval):
    """Perform the folder synchronization"""
    try:
        # Checking source, replica & log file paths
        check_paths(source_folder, replica_folder, log_file)

        # Checking permissions
        check_permissions(source_folder, replica_folder)

        # Now starting synchronization
        print(f"Folders Synchronization Started with an interval of {interval} seconds",flush=True)
        while True:
            # List all files and folders in the source and replica folders with their MD5 hashes            
            source_data_items = get_source_data(source_folder)
            replica_items = get_replica_data(replica_folder)

            # Copy or update files and folders from source to replica
            copy_update_data(source_folder, replica_folder, source_data_items, replica_items, log_file)

            # Delete items from replica that don't exist in source
            delete_data(source_folder, replica_folder, source_data_items, replica_items, log_file)

            # Sleeping as per given time interval
            time.sleep(interval)
    
    except FileNotFoundError as e:
         print(f"Error: {e}",flush=True)
         with open(log_file, 'a') as log:
            log.write(f"[{get_timestamp()}] Error: {e}\n")
            log.write(f"[{get_timestamp()}] Please make sure the source and replica folders exist.\n")

    except Exception as e:
        print(f"An unexpected error occurred: {e}",flush=True)
        with open(log_file, 'a') as log:
            log.write(f"[{get_timestamp()}] An unexpected error occurred: {e}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synchronize two folders using MD5 hashes.'")
    parser.add_argument("source_folder", type=str, help="Path to the source folder")
    parser.add_argument("replica_folder", type=str, help="Path to the replica folder")
    parser.add_argument("log_file", type=str, help="Path to the log file")
    parser.add_argument("interval", type=int, help="Synchronization interval in seconds")
    args = parser.parse_args()

    sync_the_folders(args.source_folder, args.replica_folder, args.log_file, args.interval)