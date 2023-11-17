import time
import os
from pathlib import Path
from dotenv import load_dotenv
import logging
from lwua.helpers import enable_logging, resolve_path
from lwua.graph_functions import ingest_data_file, delete_data_file, get_admin_graph

log = logging.getLogger(__name__)

URN_BASE = os.getenv("URN_BASE", "urn:lwua:INGEST")

class Watcher:
    def __init__(self, directory_to_watch):
        self.directory_to_watch = resolve_path(os.getenv("GDB_DATA_FOLDER", os.path.join("/root/graphdb-import",directory_to_watch)), "dotenv").absolute()
        log.info(f"env pointing to { self.directory_to_watch }")
        self.files = self.get_all_files()
        self.first_loop = True
        
    def get_all_files(self):
        return {f: [os.path.getmtime(f)] for f in Path(self.directory_to_watch).glob('**/*') if f.is_file()}

    def observe(self):
        new_files = self.get_all_files()
        added = {f: new_files[f] for f in new_files if f not in self.files}
        deleted = {f: self.files[f] for f in self.files if f not in new_files}
        modified = {}
        for f in new_files:
            if f in self.files and new_files[f] != self.files[f]:
                self.files[f] = new_files[f]
                modified[f] = self.files[f]
      
        self.files = new_files
        return added, deleted, modified

    def run(self):
        try:
            while True:
                if self.first_loop:
                    log.info("First time loop")
                    #try and get the graph , if this fails due to the graphdb server not being up yet, the watcher will try again in 5 seconds untill it succeeds
                    get_admin = True
                    while get_admin:
                        try:
                            #get admin graph
                            admin_graph = get_admin_graph()
                            info_admin = [(g['g']['value'].replace(f"{URN_BASE}:", ''), g['m']['value']) for g in admin_graph['results']['bindings']]
                            all_files = self.get_all_files()
                            #compare the files to the admin graph
                            # if filename is not in the admin graph, add it
                            # if filename is in the admin graph, check if the last modified time is the same, if not update the graph
                            # if filename is in the admin graph, but not in the files, delete the graph
                            info_admin_dict = {g[0]: g[1] for g in info_admin}
                            
                            for g in info_admin:
                                if g[0] not in all_files:
                                    log.info(f"File {g[0]} has been deleted since downtime, deleting graph")
                                    delete_data_file(g[0])
                            
                            for f in all_files:
                                if f in info_admin_dict:
                                    # !TODO: check variables since the modified now just deletes the graph :/
                                    if info_admin_dict[f] < all_files[f][0]:
                                        log.info(f"File {f} has been modified since downtime, updating graph")
                                        ingest_data_file(f, True)
                                    continue
                                log.info(f"File {f} has been added since downtime, adding graph")
                                ingest_data_file(f)
                            
                        except Exception as e:
                            log.error(f"error: {e}")
                            time.sleep(1)
                            continue
                        
                        get_admin = False
                    self.first_loop = False

                log.info("Checking for updates")
                added, deleted, modified = self.observe()
                for f in added:
                    log.info(f"File {f} has been added ")
                    ingest_data_file(f)
                for f in deleted:
                    log.info(f"File {f} has been deleted")
                    delete_data_file(f)
                for f in modified:
                    log.info(f"File {f} has been modified")
                    ingest_data_file(f, True)
                    
                time.sleep(5)
        except KeyboardInterrupt:
            log.info("Stopping watcher")     

## test the watcher on local file system - not in docker
if __name__ == '__main__':
    load_dotenv()
    enable_logging()
    file_to_watch = resolve_path(os.getenv("GDB_DATA_FOLDER", "/root/graphdb-import/data"), "dotenv").absolute()
    log.info(f"env pointing to { file_to_watch }")
    w = Watcher(file_to_watch)
    w.run()