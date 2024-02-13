import logging
import os
from pytravharv import TargetStore, TravHarvConfigBuilder, TravHarvExecutor
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

    def init_targetstore(self, url):
        try:
            return TargetStore(url)
        except Exception as e:
            log.error("init targetstore failed, trying again in 1s")
            log.error("error: {e}")
            time.sleep(1)
            self.init_targetstore(url)

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

        TARGETSTORE = TargetStore(GDB_URL)

        log.info(TARGETSTORE)

        CONFIGBUILDER = TravHarvConfigBuilder(
            TARGETSTORE,
            str(config_folder_path),
        )

        CONFIGLIST = CONFIGBUILDER.build_from_folder()

        for travHarvConfig in CONFIGLIST:
            log.info("Config object: {}".format(travHarvConfig()))
            prefix_set = travHarvConfig.PrefixSet
            config_name = travHarvConfig.ConfigName
            tasks = travHarvConfig.tasks

            travharvexecutor = TravHarvExecutor(
                config_name, prefix_set, tasks, TARGETSTORE
            )

            travharvexecutor.assert_all_paths()
