import logging
import time
from dotenv import load_dotenv
from datetime import datetime
from SPARQLWrapper import SPARQLWrapper, JSON
import os
from pathlib import Path
from .helpers import enable_logging, resolve_path

log = logging.getLogger(__name__)

class Dereference:
    def __init__(self):
        pass

    def run_dereference(self):
        log.info("running dereference")