#!/usr/bin/env python
import os
from pathlib import Path
from pysembench.core import Sembench
import logging
import logging.config
import yaml

with open(Path("kgap/debug-logconf.yml"), "r") as f:
    log_cfg = yaml.safe_load(f.read())

logging.config.dictConfig(log_cfg)

log = logging.getLogger(__name__)

log.info("Starting Sembench")

sb = Sembench(
    input_data_location=os.getenv("INPUT_DATA_LOCATION"),
    output_data_location=os.getenv("OUTPUT_DATA_LOCATION"),
    sembench_data_location=os.getenv("SEMBENCH_DATA_LOCATION"),
    sembench_config_path=os.getenv("SEMBENCH_CONFIG_PATH"),
    scheduler_interval_seconds=os.getenv("SCHEDULER_INTERVAL_SECONDS"),
)

sb.process()
