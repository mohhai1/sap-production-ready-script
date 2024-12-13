import os
import time
import threading
import logging
from typing import Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from termcolor import colored

# Constants
DEFAULT_PERIODICITY = 5  # Default monitoring periodicity in seconds

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [Thread ID: %(thread)d] %(message)s')

def log_message(level: int, message: str, color: Optional[str] = None) -> None:
    """Log a message with the specified level and optional color for the level."""
    level_name = logging.getLevelName(level)
    if color:
        level_name = colored(level_name, color)
    logging.log(level, f"[{level_name}] {message}")

def get_folder_id(folder_path: str) -> str:
    """Generate a unique ID for a folder based on its creation time."""
    try:
        stats = os.stat(folder_path)
        return f"{int(stats.st_ctime)}"
    except FileNotFoundError:
        return ""

def monitor_folder(folder_path: str, folder_id: str) -> None:
    """Monitor a specific folder for events like creation, renaming, and deletion."""
    class FolderEventHandler(FileSystemEventHandler):
        def on_created(self, event):
            if "content-banned" in os.path.basename(event.src_path):
                log_message(logging.INFO, f"File created: {event.src_path}", color="green")

        def on_deleted(self, event):
            if "content-banned" in os.path.basename(event.src_path):
                log_message(logging.INFO, f"File deleted: {event.src_path}", color="green")

        def on_moved(self, event):
            nonlocal folder_path
            if os.path.abspath(folder_path) == os.path.abspath(event.src_path):
                log_message(logging.WARNING, f"Folder renamed from {event.src_path} to {event.dest_path}", color="yellow")
                folder_path = event.dest_path
                observer.stop()

    event_handler = FolderEventHandler()
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=False)
    observer.start()

    try:
        while os.path.exists(folder_path):
            log_message(logging.INFO, f"Monitoring folder {folder_path} (ID: {folder_id})", color="green")
            time.sleep(int(os.getenv('PERIODICITY', DEFAULT_PERIODICITY)))
    except Exception as e:
        log_message(logging.CRITICAL, f"Error monitoring folder {folder_path}: {e}", color="red")
    finally:
        observer.stop()
        observer.join()
        log_message(logging.CRITICAL, f"Folder {folder_path} (ID: {folder_id}) monitoring terminated.", color="red")

def wait_for_folder(folder_path: str) -> None:
    """Wait for the folder to be created, then start monitoring it."""
    log_message(logging.INFO, f"Waiting for folder {folder_path} to be created...", color="green")
    while not os.path.exists(folder_path):
        time.sleep(1)

def main() -> None:
    """Main function to initialize folder monitoring."""
    folder_path = os.getenv('MONITORED_FOLDER', './watched_folder')

    while True:
        wait_for_folder(folder_path)

        folder_id = get_folder_id(folder_path)
        if folder_id:
            log_message(logging.INFO, f"Folder {folder_path} of ID {folder_id} is created with Thread ID {threading.get_ident()}", color="green")

            monitor_thread = threading.Thread(target=monitor_folder, args=(folder_path, folder_id), daemon=True)
            monitor_thread.start()
            monitor_thread.join()
        else:
            log_message(logging.CRITICAL, f"Failed to get folder ID for {folder_path}.", color="red")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log_message(logging.INFO, "Monitoring script terminated by user.", color="green")
