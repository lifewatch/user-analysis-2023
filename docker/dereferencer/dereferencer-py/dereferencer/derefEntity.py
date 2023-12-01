# This file will contain all the classes and functions needed to complete
# the dereferencing process

import logging
from pathlib import Path
import json
import requests
import os

from .helpers import resolve_path

log = logging.getLogger(__name__)


def data_folder_from_config():
    local_default = str(resolve_path("../data", versus="dotenv"))
    folder_name = os.getenv("DATA_FOLDER", local_default)
    return folder_name




DATA_FOLDER = data_folder_from_config()


class DerefUriEntity:
    def __init__(self, uri: str, propertypaths: dict):
        self.uri = uri
        self.propertypathmetadata = None
        self.propertypaths = propertypaths

        self.download_uri(uri)
        if propertypaths is not None:
            self.run_download_propertypaths()

    def download_uri(self, uri: str):
        """downloads the uri either in json-ld or ttl format and puts the result in the DATA_FOLDER

        :param uri: uri to download
        :type uri: str
        """
        log.info(f"downloading uri {uri}")
        # perform request with accept header for json-ld or ttl
        headers = {"Accept": "application/ld+json, text/turtle"}
        r = requests.get(uri, headers=headers)

        # check if the request was successful and it returned a json-ld or ttl
        # file
        if r.status_code == 200 and (
            "application/ld+json" in r.headers["Content-Type"]
            or "text/turtle" in r.headers["Content-Type"]
        ):
            # write the file to disk
            # TODO: check if the file already exists
            # check if the file is json-ld or ttl and add the correct extension
            if "application/ld+json" in r.headers["Content-Type"]:
                filename = DATA_FOLDER + "/" + uri.split("/")[-1] + ".json"
            elif "text/turtle" in r.headers["Content-Type"]:
                filename = DATA_FOLDER + "/" + uri.split("/")[-1] + ".ttl"
            with open(filename, "w") as f:
                f.write(r.text)
            log.info(f"file saved to {filename}")
            return filename
        else:
            log.warning(
                f"request for {uri} failed with status code {r.status_code} and content type {r.headers['Content-Type']}"
            )
            return None

    # This function cannot be run atm , first download main self.uri
    def run_download_propertypaths(self):
        """runs the download_propertypaths function for all propertypaths"""
        for propertypath in self.propertypaths:
            log.info(f"running download_propertypath for {propertypath}")
