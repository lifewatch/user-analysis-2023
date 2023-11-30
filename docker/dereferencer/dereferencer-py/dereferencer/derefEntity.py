# This file will contain all the classes and functions needed to complete
# the dereferencing process

import logging
from pathlib import Path
import json
import requests
import os

from .helpers import resolve_path

log = logging.getLogger(__name__)


def metadata_folder_from_config():
    local_default = str(resolve_path("./memory_dereferencer", versus="dotenv"))
    folder_name = os.getenv("METADATA_FILES_FOLDER", local_default)
    return folder_name


METADATA_FOLDER = metadata_folder_from_config()


def check_metadata_folder_exists():
    metadata_folder = metadata_folder_from_config()
    if not os.path.exists(metadata_folder):
        log.info(
            f"metadata folder {metadata_folder} does not exist, creating it")
        os.makedirs(metadata_folder)


METADATA_FILE = METADATA_FOLDER + "/metadata.json"


def make_metadata(input_list):
    result = []

    if input_list is None:
        return result

    for item in input_list:
        if isinstance(item, dict):
            for key, values in item.items():
                if isinstance(values, list):
                    children = make_metadata(values)
                    result.append(
                        {key: {"completed": False, "children": children}})
                else:
                    result.append({values: {"completed": False}})
        elif isinstance(item, str):
            result.append({item: {"completed": False}})

    return result


def save_metadata(uri: str, data: object, completed: bool = False):
    """saves the metadata to file"""
    with open(METADATA_FILE, "r") as f:
        # read the json file
        current_metadata = json.load(f)
    # replace the metadata for the uri with the new metadata
    current_metadata[uri] = {"completed": completed, "metadata": data}
    with open(METADATA_FILE, "w") as f:
        json.dump(current_metadata, f)


class DerefUriEntity:
    def __init__(self, uri: str, propertypaths: dict):
        self.uri = uri
        self.propertypathmetadata = None
        self.propertypaths = propertypaths

        check_metadata_folder_exists()
        if not os.path.exists(METADATA_FILE):
            log.info(
                f"metadata file {METADATA_FILE} does not exist, creating it")
            with open(METADATA_FILE, "w") as f:
                json.dump({}, f)
        else:
            with open(METADATA_FILE, "r") as f:
                self.metadata = json.load(f)
            self.propertypathmetadata = self.get_metadata_uri(uri)

        log.debug(f"propertypathmetadata: {self.propertypathmetadata}")

        # if propertyMetadata is None then run function make metadata
        if self.propertypathmetadata is None:
            self.propertypathmetadata = make_metadata(self.propertypaths)
            log.info(f"propertypathmetadata: {self.propertypathmetadata}")
            save_metadata(self.uri, self.propertypathmetadata)

    def get_metadata_uri(self, uri: str):
        """checks if a given uri is in the metadata

        :param uri: uri to check
        :type uri: str
        :return: dict with the metadata for the uri
        """
        if uri in self.metadata:
            return self.metadata[uri]["metadata"]
        else:
            return None
