import logging
import time
from dotenv import load_dotenv
from SPARQLWrapper import SPARQLWrapper, JSON
from pathlib import Path
from .helpers import enable_logging,  data_path_from_config
from .watcher import FolderChangeDetector, IngestChangeObserver
from .graphdb import ingest_data_file, get_registry_of_lastmod


log = logging.getLogger(__name__)

def run_ingest():
    data_path = data_path_from_config()
    log.info(f"run_ingest on updated files in {data_path}")
    
    # get the last context graph modification dates
    # run while true loop with 5 second sleep
    detector = FolderChangeDetector(data_path)
    ingestor = IngestChangeObserver()
    last_mod = None
    while last_mod is None:
        try:
            last_mod = get_registry_of_lastmod()
            log.info(f"initial last mod == {last_mod}")
        except Exception as e:
            log.exception(e)
            time.sleep(2)
    
    while True:
        log.info("reporting changes")
        last_mod = detector.report_changes(last_mod,ingestor)
        log.info(f"last_mod == {last_mod}")
        time.sleep(5)


# Note: this main method allows to locally test outside docker
# directly connecting to a localhost graphdb endpoint (which might be
# inside docker itself)


def main():
    load_dotenv()
    enable_logging()
    ingest_data_file("project.ttl")


if __name__ == "__main__":
    main()
