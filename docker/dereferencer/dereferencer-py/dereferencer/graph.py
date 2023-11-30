# this file will contain the functions that will be used to query the graph database

import logging
from SPARQLWrapper import SPARQLWrapper, JSON
import logging
import os

# from dotenv import load_dotenv

log = logging.getLogger(__name__)

def gdb_from_config():
    base = os.getenv("GDB_BASE", "http://localhost:7200")
    repoid = os.getenv("GDB_REPO", "lwua23")

    endpoint = f"{ base }/repositories/{ repoid }"
    # update statements are handled at other endpoint
    updateEndpoint = endpoint + "/statements"

    log.debug(f"using endpoint {endpoint}")

    GDB = SPARQLWrapper(
        endpoint=endpoint,
        updateEndpoint=updateEndpoint,
        returnFormat=JSON,
        agent="lwua-python-sparql-client",
    )
    GDB.method = "POST"
    return GDB


GDB = gdb_from_config()

def uri_list(query):
    """
    Return a list of URI's from a query
    """
    log.debug(f"uri_list: {query}")
    GDB.setQuery(query)
    GDB.setReturnFormat(JSON)
    results = GDB.query().convert()
    log.debug(f"uri_list: results: {results}")
    return [result["s"]["value"] for result in results["results"]["bindings"]]

