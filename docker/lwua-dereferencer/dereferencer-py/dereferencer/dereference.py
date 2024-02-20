import logging
import os
from pytravharv import TravHarv
from .helpers import resolve_path
from pathlib import Path
import time

log = logging.getLogger(__name__)

GDB_URL = "http://graphdb:7200/repositories/lwua23"


def config_path_from_config():
    local_default = str(resolve_path("./config", versus="dotenv"))
    folder_name = os.getenv("CONFIG_FILES_FOLDER", local_default)
    test = "/config"
    return Path(test).absolute()


class Dereference:
    def __init__(self):
        pass

    def run_dereference(self):
        log.info("running dereference")

        config_folder_path = config_path_from_config()
        log.info(f"run_dereference on config files in {str(config_folder_path)}")

        target_store = [GDB_URL, GDB_URL + "/statements"]
        try:
            TravHarv(
                config_folder_path,
                target_store_info=target_store,
            ).run_dereference_tasks()
        except Exception as e:
            log.error(f"Error running dereference: {e}")
            raise e
