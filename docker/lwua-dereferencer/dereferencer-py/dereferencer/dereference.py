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

        config_files = [f for f in config_folder_path.glob("*.yml")]
        log.info(f"config files found: {config_files}")

        for f in config_files:
            with open(f, "r") as file:
                content = file.read()

            # Log the content of the file
            logging.info(content)

        TravHarv(config_folder=config_folder_path, target_store=GDB_URL).run()
