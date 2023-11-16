import time
import os
from pathlib import Path
from dotenv import load_dotenv
import logging
from lwua.helpers import enable_logging, resolve_path
from lwua.graph_functions import delete_graph, ingest_data_file

log = logging.getLogger(__name__)

### Cedric Decruw - 2023-11-16 ###
# ! watchdog was not used due to the fact that the docker container was not able to access the host filesystem
# ! this is a simple file watcher that will be used to trigger the ingest process
class FileStore:
    def __init__(self, directory):
        self.directory = directory
        self.files = self.get_all_files()
        self.last_files = None

    def get_all_files(self):
        return {f: [os.path.getmtime(f)] for f in Path(self.directory).glob('**/*') if f.is_file()}

    def update(self):
        new_files = self.get_all_files()
        added = {f: new_files[f] for f in new_files if f not in self.files}
        deleted = {f: self.files[f] for f in self.files if f not in new_files}
        modified = {}
        for f in new_files:
            if f in self.files and new_files[f][0] != self.files[f][-1]:
                if len(self.files[f]) == 2:
                    self.files[f].pop(0)
                self.files[f].append(new_files[f][0])
                modified[f] = self.files[f]
        self.last_files = self.files
        self.files = new_files
        return added, deleted, modified, self.last_files

class Watcher:
    def __init__(self, directory_to_watch):
        self.directory_to_watch = resolve_path(os.getenv("GDB_DATA_FOLDER", os.path.join("/root/graphdb-import",directory_to_watch)), "dotenv").absolute()
        log.info(f"env pointing to { self.directory_to_watch }")
        self.file_store = FileStore(self.directory_to_watch)

    def run(self):
        try:
            while True:
                if self.file_store.last_files is None:
                    log.info("First time loop")
                    #do stuff for first time loop here like checking for existinf context in graphdb

                log.info("Checking for updates")
                added, deleted, modified, previous_filestore = self.file_store.update()
                for f in added:
                    log.info(f"File {f} has been added at {time.ctime(added[f][0])}")
                    context = f"{f}_{format_time(added[f][0])}"
                    log.info(f"context to be used to add: {context}")
                    #ingest_data_file(f,context)
                for f in deleted:
                    log.info(f"File {f} has been deleted")
                    #find the file in the previous filestore and use the last modified time to delete the graph
                    context = f"{f}_{format_time(previous_filestore[f][-1])}"
                    log.info(f"context to be used to delete: {context}")
                    #delete_graph(context)
                for f in modified:
                    log.info(f"File {f} has been modified at {time.ctime(modified[f][-1])}, previous to last modified time: {time.ctime(modified[f][0]) if len(modified[f]) > 1 else 'N/A'}")
                    context_to_delete = f"{f}_{format_time(modified[f][0])}"
                    context_to_add = f"{f}_{format_time(modified[f][-1])}"
                    log.info(f"context to be used to delete: {context_to_delete}")
                    log.info(f"context to be used to add: {context_to_add}")
                    #ingest_data_file(f,context_to_add, context_to_delete)
                    
                time.sleep(5)
        except KeyboardInterrupt:
            log.info("Stopping watcher")     
            
def format_time(epoch_time):
    # Convert epoch time to struct_time object
    time_obj = time.localtime(epoch_time)
    # Format to return %Y_%m_%d_%H_%M_%S
    return time.strftime("%Y_%m_%d_%H_%M_%S", time_obj)

## test the watcher on local file system - not in docker
if __name__ == '__main__':
    load_dotenv()
    enable_logging()
    file_to_watch = resolve_path(os.getenv("GDB_DATA_FOLDER", "/root/graphdb-import/data"), "dotenv").absolute()
    log.info(f"env pointing to { file_to_watch }")
    w = Watcher(file_to_watch)
    w.run()
