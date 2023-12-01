# this file will contain the functions that will be used to query the
# graph database

import logging
from SPARQLWrapper import SPARQLWrapper, JSON
from urllib.parse import unquote, quote
import logging
import os
import re

# from dotenv import load_dotenv

log = logging.getLogger(__name__)
URN_BASE = os.getenv("URN_BASE", "urn:lwua:INGEST")


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


def get_j2rdf_builder():
    template_folder = resolve_path("./lwua/templates")
    log.info(f"template_folder == {template_folder}")
    # init J2RDFSyntaxBuilder
    j2rdf = J2RDFSyntaxBuilder(
        templates_folder=template_folder,
        extra_functions={"registry_of_lastmod_context": f"{URN_BASE}:ADMIN"},
    )
    return j2rdf


J2RDF = get_j2rdf_builder()


def get_registry_of_lastmod():
    log.info(f"getting last modified graph")

    template = "lastmod_info.sparql"
    vars = {}
    query = J2RDF.build_syntax(template, **vars)
    # log.debug(f"get_admin_graph query == {query}")
    GDB.setQuery(query)
    GDB.setReturnFormat(JSON)
    results = GDB.query().convert()

    # convert {'head': {'vars': ['graph', 'lastmod']}, 'results': {'bindings': []}} to [{PosixPath('graph'): lastmod}]
    # URI must be substracted from graph context and datetime str must be
    # converted to epoch

    converted = {}
    return convert_results_registry_of_lastmod(results)


def convert_results_registry_of_lastmod(results):
    converted = {}
    for g in results["results"]["bindings"]:
        path = context_2_fname(g["graph"]["value"])
        time = datetime.fromisoformat(g["lastmod"]["value"])
        converted[path] = time
    return converted


def context_2_fname(context: str):
    """
    Convert a context to a filename path.

    :param context: The context to convert.
    :type context: str
    :return: The filename corresponding to the context.
    :rtype: str
    """
    assert context.startswith(
        URN_BASE), f"Context {context} is not IRI compliant"
    return unquote(context[len(URN_BASE) + 1:])


def fname_2_context(fname: str):
    """
    Convert a filename to a context.

    :param fname: The filename to convert.
    :type fname: str
    :return: The context corresponding to the filename.
    :rtype: str
    """
    fname = str(fname)
    return f"{URN_BASE}:{quote(fname)}"


def uri_list(query):
    """
    Return a list of URI's from a query
    """
    log.debug(f"uri_list: {query}")

    # Extract the variable from the SELECT clause
    select_part = re.search("SELECT(.*)WHERE", query, re.IGNORECASE).group(1)
    variables = select_part.split()

    # Check that there is exactly one variable in the SELECT part of the
    # SPARQL query
    if len(variables) != 1:
        error_message = f"There should be exactly one variable in the SELECT part of the SPARQL query but found {len(variables)} in {variables}"
        log.error(error_message)
        raise ValueError(error_message)

    var = variables[0][1:]  # remove the ? from the variable

    GDB.setQuery(query)
    GDB.setReturnFormat(JSON)
    results = GDB.query().convert()
    log.debug(f"uri_list: results: {results}")

    # Use the extracted variable when getting the results
    return [result[var]["value"] for result in results["results"]["bindings"]]
