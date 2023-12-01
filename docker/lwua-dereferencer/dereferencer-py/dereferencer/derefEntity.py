# This file will contain all the classes and functions needed to complete
# the dereferencing process

import logging
from pathlib import Path
import json
import requests
import os

from .helpers import resolve_path
from .graph import uri_list_from_deref_property_path

log = logging.getLogger(__name__)


def data_folder_from_config():
    local_default = str(resolve_path("../data", versus="dotenv"))
    folder_name = os.getenv("DATA_FOLDER", local_default)
    return folder_name


def url_2_fname(url: str):
    """
    Convert a URL to a filename.

    :param url: The URL to convert.
    :type url: str
    :return: The filename corresponding to the URL.
    :rtype: str
    """
    return url.replace(":", "_").replace("/", "_").replace("?", "_").replace("&", "_").replace("=", "_").replace("#", "_")


DATA_FOLDER = data_folder_from_config()



def run_download_propertypaths(propertypaths, uri, file_name, download_uri):
    """runs the download_propertypaths function for all propertypaths"""
    for propertypath in propertypaths:
        log.info(f"running download_propertypath for {propertypath}")
        # if propertypath is a string, download it
        if isinstance(propertypath, str):
            log.info(f"propertypath is a string: {propertypath}, downloading")
            to_download = uri_list_from_deref_property_path(uri, file_name, propertypath)
            for uri in to_download:
                if get_uri_downloaded(url_2_fname(uri)) is None:
                    download_uri(uri, url_2_fname(uri))
        if isinstance(propertypath, dict):
            log.info(f"propertypath is a dict: {propertypath}, downloading")
            # property path is the key of the dict
            property_to_search = list(propertypath.keys())[0]
            log.info(f"property_to_search: {property_to_search}")
            
            to_download = uri_list_from_deref_property_path(uri, file_name, property_to_search)
            for uri in to_download:
                file_name = get_uri_downloaded(url_2_fname(uri))
                if file_name is None:
                    file_name = download_uri(uri, url_2_fname(uri))
                uri = uri
                propertypath = propertypath[property_to_search]
                run_download_propertypaths(propertypath, uri, file_name, download_uri)
                
def download_uri(uri: str, file_name: str):
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
            filename = DATA_FOLDER + "/" + file_name + ".json"
        elif "text/turtle" in r.headers["Content-Type"]:
            filename = DATA_FOLDER + "/" + file_name + ".ttl"
        with open(filename, "w") as f:
            f.write(r.text)
        log.info(f"file saved to {filename}")
        filename = filename.replace(DATA_FOLDER, "/data")
        return filename
    else:
        log.warning(
            f"request for {uri} failed with status code {r.status_code} and content type {r.headers['Content-Type']}"
        )
        return None

def get_uri_downloaded(file_name: str):
    """gets the filename of the uri if it is already downloaded

    :param file_name: filename of the uri
    :type file_name: str
    :return: filename of the uri if it is already downloaded
    :rtype: str
    """
    
    if os.path.isfile(DATA_FOLDER + "/" + file_name + ".json"):
        filename = DATA_FOLDER + "/" + file_name + ".json"
        return filename.replace(DATA_FOLDER, "/data")
    if os.path.isfile(DATA_FOLDER + "/" + file_name + ".ttl"):
        filename = DATA_FOLDER + "/" + file_name + ".ttl"
        return filename.replace(DATA_FOLDER, "/data")
    return None


class DerefUriEntity:
    def __init__(self, uri: str, propertypaths: dict):
        self.uri = uri
        self.propertypathmetadata = None
        self.propertypaths = propertypaths
        self.file_name = url_2_fname(uri)
        self.filename = get_uri_downloaded(self.file_name)
        if self.filename is None:
            log.info(f"uri {uri} not downloaded yet")
            self.filename = download_uri(uri, self.file_name)
        
        if propertypaths is not None:
            run_download_propertypaths(self.propertypaths, self.uri, self.filename, download_uri)
            
