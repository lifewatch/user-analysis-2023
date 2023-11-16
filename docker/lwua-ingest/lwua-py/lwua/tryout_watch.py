import time
import os
from pathlib import Path
from dotenv import load_dotenv
import logging
from lwua.helpers import enable_logging, resolve_path
from lwua.graph_functions import delete_graph, ingest_data_file, get_admin_graph

log = logging.getLogger(__name__)

URN_BASE = "urn:lwua:INGEST" # !TODO: shouldn't this be in the env file?

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
                    
                    #try and get the graph , if this fails due to the graphdb server not being up yet, the watcher will try again in 5 seconds untill it succeeds
                    get_admin = True
                    while get_admin:
                        try:
                            admin_graph = get_admin_graph()
                            log.info(f"admin graph: {admin_graph}")
                            # admin graph looks like {'head': {'vars': ['g', 'm']}, 'results': {'bindings': [{'g': {'type': 'uri', 'value': 'urn:lwua:INGEST#admin-lwua-ingest'}, 'm': {'datatype': 'http://www.w3.org/2001/XMLSchema#dateTime', 'type': 'literal', 'value': '2021-09-16T14:00:00Z'}}}]}}
                            # we need to extract all the g.value's and put them in a list 
                            all_graphs_unformatted = [g['g']['value'] for g in admin_graph['results']['bindings']]
                            #replace the URN_BASE with the empty string to get the context
                            all_graphs = [g.replace(f"{URN_BASE}:","") for g in all_graphs_unformatted]
                            
                            #from this extract the name and last modified time of the graph by splitting on the last "_"
                            info_admin_graph = []
                            for g in all_graphs:
                                info_g = {}
                                #split the string on the last "_" to get the name and last modified time
                                name, last_modified = g.rsplit("_",1)
                                info_g['name'] = name
                                info_g['last_modified'] = last_modified
                                info_admin_graph.append(info_g)
                            
                            log.info(f"all graphs: {info_admin_graph}")
                            get_admin = False
                            
                            #get all the files in the data folder recursively
                            all_files = self.file_store.get_all_files()
                            #compare the files to the admin graph 
                            # if filename is not in the admin graph, add it
                            # if filename is in the admin graph, check if the last modified time is the same, if not update the graph
                            # if filename is in the admin graph, but not in the files, delete the graph
                            
                            for f in all_files:
                                #check if the file is in the admin graph
                                if f not in all_graphs:
                                    #add the file to the graph
                                    context = f"{f}_{all_files[f][0]}"
                                    log.info(f"context to be used to add: {context}")
                                    ingest_data_file(f,context)
                                else:
                                    #check if the last modified time is the same
                                    if all_files[f][0] != info_admin_graph[all_graphs.index(f)]['last_modified']:
                                        #update the graph
                                        context_to_delete = f"{f}_{info_admin_graph[all_graphs.index(f)]['last_modified']}"
                                        context_to_add = f"{f}_{all_files[f][0]}"
                                        log.info(f"context to be used to delete: {context_to_delete}")
                                        log.info(f"context to be used to add: {context_to_add}")
                                        ingest_data_file(f,context_to_add, context_to_delete)
                            
                            #check if there are any graphs in the admin graph that are not in the files
                            for g in info_admin_graph:
                                if g['name'] not in all_files:
                                    log.info(f"graph {g['name']} not in files, deleting")
                                    #delete the graph
                                    context = f"{g['name']}_{g['last_modified']}"
                                    log.info(f"context to be used to delete: {context}")
                                    delete_graph(context)
                            
                        except:
                            log.info("graphdb server not up yet, trying again in 1 second")
                            time.sleep(1)
                            continue

                log.info("Checking for updates")
                added, deleted, modified, previous_filestore = self.file_store.update()
                for f in added:
                    log.info(f"File {f} has been added at {time.ctime(added[f][0])}")
                    #context = f"{f}_{format_time(added[f][0])}"
                    context = f"{f}_{added[f][0]}"
                    log.info(f"context to be used to add: {context}")
                    ingest_data_file(f,context)
                for f in deleted:
                    log.info(f"File {f} has been deleted")
                    #find the file in the previous filestore and use the last modified time to delete the graph
                    #context = f"{f}_{format_time(previous_filestore[f][-1])}"
                    context = f"{f}_{previous_filestore[f][-1]}"
                    log.info(f"context to be used to delete: {context}")
                    delete_graph(context)
                for f in modified:
                    log.info(f"File {f} has been modified at {time.ctime(modified[f][-1])}, previous to last modified time: {time.ctime(modified[f][0]) if len(modified[f]) > 1 else 'N/A'}")
                    #context_to_delete = f"{f}_{format_time(modified[f][0])}"
                    #context_to_add = f"{f}_{format_time(modified[f][-1])}"
                    context_to_delete = f"{f}_{modified[f][0]}"
                    context_to_add = f"{f}_{modified[f][-1]}"
                    log.info(f"context to be used to delete: {context_to_delete}")
                    log.info(f"context to be used to add: {context_to_add}")
                    ingest_data_file(f,context_to_add, context_to_delete)
                    
                time.sleep(5)
        except KeyboardInterrupt:
            log.info("Stopping watcher")     

#left out this part of the code since it is easier to just use the epoch time as the context , that way there is no need to reverse the process for the startup of the watcher
'''      
def format_time(epoch_time):
    # Convert epoch time to struct_time object
    time_obj = time.localtime(epoch_time)
    # Format to return %Y_%m_%d_%H_%M_%S
    return time.strftime("%Y_%m_%d_%H_%M_%S", time_obj)
'''     

## test the watcher on local file system - not in docker
if __name__ == '__main__':
    load_dotenv()
    enable_logging()
    file_to_watch = resolve_path(os.getenv("GDB_DATA_FOLDER", "/root/graphdb-import/data"), "dotenv").absolute()
    log.info(f"env pointing to { file_to_watch }")
    w = Watcher(file_to_watch)
    w.run()
