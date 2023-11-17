import logging
from dotenv import load_dotenv
from .helpers import enable_logging #, resolve_path
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

# Note: this main method allows to locally test outside docker
# directly connecting to a localhost graphdb endpoint (which might be inside docker itself)
def main():
    load_dotenv()
    enable_logging()
    ingest_data_file("project.ttl")

if __name__ == '__main__':
    main()
