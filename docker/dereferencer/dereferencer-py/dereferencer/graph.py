# this file will contain the functions that will be used to query the
# graph database

import logging
from SPARQLWrapper import SPARQLWrapper, JSON
import logging
import os
import re

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

    # Extract the variable from the SELECT clause
    select_part = re.search('SELECT(.*)WHERE', query, re.IGNORECASE).group(1)
    variables = select_part.split()
    
    # Check that there is exactly one variable in the SELECT part of the SPARQL query
    if len(variables) != 1:
        log.error("There should be exactly one variable in the SELECT part of the SPARQL query")
        raise AssertionError("There should be exactly one variable in the SELECT part of the SPARQL query")

    GDB.setQuery(query)
    GDB.setReturnFormat(JSON)
    results = GDB.query().convert()
    log.debug(f"uri_list: results: {results}")

    # Use the extracted variable when getting the results
    return [result[var]["value"] for result in results["results"]["bindings"]]

