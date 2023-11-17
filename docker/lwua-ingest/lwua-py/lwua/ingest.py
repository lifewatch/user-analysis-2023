from SPARQLWrapper import SPARQLWrapper, JSON
from pathlib import Path
import logging
from rdflib import Graph
import os
from dotenv import load_dotenv
from .helpers import enable_logging, resolve_path
from .watcher import Watcher
from .graph_functions import ingest_data_file, data_path_from_config


log = logging.getLogger(__name__)
URN_BASE = "urn:lwua:INGEST"


def run_ingest():
    data_path = data_path_from_config()
    log.info(f"run_ingest on updated files in {data_path}")
    #init watcher on data_path
    w = Watcher(data_path)
    w.run()
    
    # TODO -- immplement steps
    # list all the contents (files) in data_path together with last mod
    # get the <#admin-luwa-ingest> graph listing the maintained named-graphs and their lastmod
    # there nees to be a mapping between filenames and named-graphs !
    # check which filenames are younger then their named-graph equivalent
    # read them into mem - replace the coresponding named-graph in the repo
    # update the triple for the named-graph to lastmod in the admin grap



# Note: this main method allows to locally test outside docker
# directly connecting to a localhost graphdb endpoint (which might be inside docker itself)
def main():
    load_dotenv()
    enable_logging()
    ingest_data_file("project.ttl")

if __name__ == '__main__':
    main()
