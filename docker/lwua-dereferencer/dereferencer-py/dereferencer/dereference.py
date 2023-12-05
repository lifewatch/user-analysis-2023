import logging
import time
from dotenv import load_dotenv
from datetime import datetime
from SPARQLWrapper import SPARQLWrapper, JSON
import os
import yaml
from rdflib import Graph
from pathlib import Path
from .helpers import enable_logging, resolve_path
from .graphdb import uri_list
from .derefEntity import DerefUriEntity

log = logging.getLogger(__name__)


def config_path_from_config():
    local_default = str(resolve_path("../configs", versus="dotenv"))
    folder_name = os.getenv("CONFIG_FILES_FOLDER", local_default)
    return Path(folder_name).absolute()


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

        # for each config file , parse the file and get the config
        for config_file in config_files:
            #make a store
            self.store = Graph()
            log.info(f"config file: {config_file}")
            with open(config_file, "r") as stream:
                try:
                    config = yaml.safe_load(stream)
                    log.info(f"config: {config}")

                    sparql_query = config["SPARQL"]
                    uri_list_from_query = uri_list(sparql_query)

                    file_name = config_file.name
                    # make a derefEntity for each uri in the
                    # uri_list_from_query
                    for uri in uri_list_from_query:
                        log.info(f"uri: {uri}")
                        derefEntity = DerefUriEntity(
                            uri, config["property_paths"],self.store)
                        log.info(f"derefEntity: {derefEntity}")
                        derefEntity.write_store(file_name)

                except yaml.YAMLError as exc:
                    log.error(exc)
