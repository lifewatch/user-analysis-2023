import logging
import os
import yaml
from rdflib import Graph
from datetime import datetime, timedelta
from pathlib import Path
from .helpers import resolve_path
from .graphdb import uri_list, get_registry_of_lastmod, writeStoreToGraphDB
from .derefEntity import DerefUriEntity

log = logging.getLogger(__name__)


def config_path_from_config():
    local_default = str(resolve_path("../configs", versus="dotenv"))
    folder_name = os.getenv("CONFIG_FILES_FOLDER", local_default)
    return Path(folder_name).absolute()


def isExpired(lastmod: datetime, cache_lifetime: int):
    # check if the cache_lifetime is set
    if cache_lifetime == 0:
        return True
    # check if the lastmod is set
    if lastmod is None:
        return True
    # check if the lastmod is older than the cache_lifetime
    if lastmod + timedelta(minutes=cache_lifetime) < datetime.now():
        return True
    # if the lastmod is not older than the cache_lifetime, return false
    return False


class Dereference:
    def __init__(self):
        pass

    def run_dereference(self):
        log.info("running dereference")

        config_folder_path = config_path_from_config()
        log.info(f"run_dereference on config files in {config_folder_path}")
        # get all the config files in the config folder
        # the files should be in yml or yaml format and should start with
        # dereference
        config_files = [f for f in config_folder_path.glob("dereference*.yml")]
        log.info(f"config files found: {config_files}")

        # get all tasks from the graphdb
        tasks_run = get_registry_of_lastmod()

        # for each config file , parse the file and get the config
        for config_file in config_files:
            log.info(f"running dereference for {config_file}")
            derefTask = DerefTask(config_file)

            # log the tasks that have been run
            log.info(f"tasks_run: {tasks_run}")

            if derefTask.file_name not in tasks_run:
                log.info(f"task {derefTask.file_name} not in tasks_run")
                derefTask.run_deref_task()
                continue

            # check if the task is expired
            if isExpired(tasks_run[derefTask.file_name],
                         derefTask.cache_lifetime):
                derefTask.run_deref_task()
                continue

            log.info(
                f"task {derefTask.file_name} was present in GraphDB and is not expired"
            )


class DerefTask:
    def __init__(self, config_file: Path):
        self.store = Graph()
        self.load_config(config_file)

    def load_config(self, config_file):
        with open(config_file, "r") as stream:
            try:
                config = yaml.safe_load(stream)
                self.subjects = config["subjects"]
                # check if child of subjects is SPARQL or literal
                # if SPARQL then get the uri's from the SPARQL query
                # if literal then get the uri's from the literal
                if "SPARQL" in self.subjects:
                    self.uris = uri_list(self.subjects["SPARQL"])
                elif "literal" in self.subjects:
                    self.uris = self.subjects["literal"]
                else:
                    log.error(
                        "subjects should contain either SPARQL or literal")
                    raise Exception(
                        "subjects should contain either SPARQL or literal")
                self.prefixes = {}
                if "prefixes" in config:
                    self.prefixes = config["prefixes"]    
                
                self.deref_paths = config["assert-paths"]
                log.info(f"deref_paths: {self.deref_paths}")
                self.cache_lifetime = (
                    config["cache_lifetime"] if "cache_lifetime" in config else 0)
                self.file_name = config_file.name
            except yaml.YAMLError as exc:
                log.error(exc)
    
    def write_store(self, filename):
        """
        Write the store to the graph database
        """
        log.info("writing store to graph database")
        writeStoreToGraphDB(self.store, filename)

    def run_deref_task(self):
        self.store = Graph()
        for uri in self.uris:
            derefEntity = DerefUriEntity(uri, self.deref_paths, self.store, self.prefixes)
            log.info(f"derefEntity: {derefEntity}")
            # indent the following line to ingest after each uri is done
            # this is better for having intermediate results in dev testing but significantly slower
            # derefEntity.write_store(self.file_name)
            self.store = derefEntity.store
        #write store
        self.write_store(self.file_name)  
