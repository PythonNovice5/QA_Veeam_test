# Folder Synchronization Program
This Python program synchronizes two folders (source_folder and replica_folder) using MD5 hashes. It maintains an identical copy of the source folder at the replica folder.

## Requirements
- Python 3.x
- Operating System: Windows, macOS, or Linux

## Usage
1.  **Clone the Repository** 
   ```
    git clone https://github.com/PythonNovice5/QA_Veeam_test.git
    cd QA_Veeam_test
  ```
2. **Run the program**
   
`    python test_folder_sync.py source_folder replica_folder sync_log.txt 60
`

   Replace the arguments with the actual paths and interval as needed.

- 'source_folder': Path to the source folder.
- 'replica_folder': Path to the replica folder.
- 'sync_log.txt': Path to the log file.
- '60': Synchronization interval in seconds (e.g., sync every 60 seconds).

3. **Monitoring**
   
      The program will run indefinitely, synchronizing the folders at the specified interval. You can monitor the console output for updates on file operations. Also, you can see the logs written in the log file       provided in the argument by the user    

4. **Terminating the Program**

      To stop the program, press `Ctrl + C` in the terminal.

## Notes
  - Make sure the source and replica folders exist before running the program otherwise you an expect an exception
  - Ensure that you have the necessary permissions for reading and writing files in both folders.
