# This file will contain all the classes and functions needed to complete
# the dereferencing process

import logging
import requests
from rdflib import Graph
import os
from .store_util import getURIsFromStore
from .graphdb import writeStoreToGraphDB

log = logging.getLogger(__name__)


def run_download_propertypaths(propertypaths, uri, store):
    """runs the download_propertypaths function for all propertypaths"""
    log.info(f"store length: {len(store)}")
    for propertypath in propertypaths:
        log.info(f"running download_propertypath for {propertypath}")
        # if propertypath is a string, download it
        if isinstance(propertypath, str):
            log.info(f"propertypath is a string: {propertypath}, downloading")
            to_download = getURIsFromStore(store,propertypath,uri)
            for uri in to_download:
                download_uri_to_store(uri, store)
                
        if isinstance(propertypath, dict):
            log.info(f"propertypath is a dict: {propertypath}, downloading")
            # property path is the key of the dict
            property_to_search = list(propertypath.keys())[0]
            log.info(f"property_to_search: {property_to_search}")

            to_download = getURIsFromStore(store,property_to_search,uri)
            for uri in to_download:
                log.info(f"uri: {uri}")
                # download the uri
                download_uri_to_store(uri, store)
                uri = uri
                propertypath = propertypath[property_to_search]
                run_download_propertypaths(propertypath, uri, store)
                
    return store


def download_uri_to_store(uri, store, format='json-ld'):
    headers = {"Accept": "application/ld+json, text/turtle"}
    r = requests.get(uri, headers=headers)

    # check if the request was successful and it returned a json-ld or ttl file
    if r.status_code == 200 and (
        "application/ld+json" in r.headers["Content-Type"]
        or "text/turtle" in r.headers["Content-Type"]
    ):
        # parse the content directly into the store
        if "application/ld+json" in r.headers["Content-Type"]:
            format = 'json-ld'
        elif "text/turtle" in r.headers["Content-Type"]:
            format = 'turtle'
        store.parse(data=r.text, format=format)
        log.info(f"content of {uri} added to the store")
    else:
        log.warning(
            f"request for {uri} failed with status code {r.status_code} and content type {r.headers['Content-Type']}"
        )


class DerefUriEntity:
    def __init__(self, uri: str, propertypaths: dict, store: Graph):
        self.uri = uri
        self.store = store
        self.propertypathmetadata = None
        self.propertypaths = propertypaths
        
        # download the uri to the store
        download_uri_to_store(uri, self.store)

        if propertypaths is not None:
            self.store = run_download_propertypaths(
                self.propertypaths, self.uri, self.store 
            )
            
        # log the store and the ammount of triples in the store
        log.info(f"store: {self.store}")
        log.info(f"FINAL store length: {len(self.store)}")

    def __repr__(self):
        return f"DerefUriEntity({self.uri},{self.propertypaths},{self.store})"
    
    def write_store(self,filename):
        """
        Write the store to the graph database
        """
        log.info("writing store to graph database")
        writeStoreToGraphDB(self.store,filename)