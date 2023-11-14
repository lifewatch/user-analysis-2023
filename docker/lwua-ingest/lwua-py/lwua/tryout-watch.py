import time
import os
from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
from lwua.helpers import enable_logging, resolve_path

log = logging.getLogger(__name__)


class Watcher:
    def __init__(self, folder_to_watch):
        self.observer = Observer()
        self._folder_to_watch = folder_to_watch

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self._folder_to_watch, recursive=True)
        log.info(f"observer started @{ self._folder_to_watch }")
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except Exception as e:
            self.observer.stop()
            log.exception("observer stopped", e)

        log.info("ended observer-loop")
        self.observer.join()


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            log.info(f"Received created event - { event.src_path }.")

        elif event.event_type == 'modified':
            # Taken any action here when a file is modified.
            log.info(f"Received modified event - { event.src_path }.")


if __name__ == '__main__':
    load_dotenv()
    enable_logging()
    file_to_watch = resolve_path(os.getenv("GDB_DATA_FOLDER", "/root/graphdb-import/data"), "dotenv").absolute()
    log.info(f"env pointing to { file_to_watch }")
    w = Watcher(file_to_watch)
    w.run()
