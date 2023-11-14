import time
import os
from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
from lwua.helpers import enable_logging, resolve_path

log = logging.getLogger(__name__)

class Watcher:
    def __init__(self, directory_to_watch):
        self.observer = Observer()
        self.directory_to_watch = directory_to_watch

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.directory_to_watch, recursive=True)
        self.observer.start()
        try:
            while True:
                log.debug(f"observer loop {self.directory_to_watch}")
                time.sleep(5)
        except KeyboardInterrupt:
            log.info("Stopping watcher")
            self.observer.stop()
        log.info("Stopping observer")
        self.observer.join()

class Handler(FileSystemEventHandler):
    def on_modified(self, event):
        log.info(f"File {event.src_path} has been modified")

    def on_created(self, event):
        log.info(f"File {event.src_path} has been created")

    def on_deleted(self, event):
        log.info(f"File {event.src_path} has been deleted")

    def on_moved(self, event):
        log.info(f"File {event.src_path} has been moved to {event.dest_path}")

'''
if __name__ == '__main__':
    load_dotenv()
    enable_logging()
    file_to_watch = resolve_path(os.getenv("GDB_DATA_FOLDER", "/root/graphdb-import/data"), "dotenv").absolute()
    log.info(f"env pointing to { file_to_watch }")
    w = Watcher(file_to_watch)
    w.run()
'''
