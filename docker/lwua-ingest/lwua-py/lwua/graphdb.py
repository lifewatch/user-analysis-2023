# this file will be used to trigger the injest processes into graphdb
# this prevents the injest.py and tryout_watch.py to be run at the same
# time with conflicting circular imports

from SPARQLWrapper import SPARQLWrapper, JSON
from datetime import datetime
from pathlib import Path
import logging
from rdflib import Graph
import time
import os

# from dotenv import load_dotenv
from .helpers import resolve_path, singleton, data_path_from_config  # ,enable_logging
from pyrdfj2 import J2RDFSyntaxBuilder

log = logging.getLogger(__name__)
URN_BASE = os.getenv("URN_BASE", "urn:lwua:INGEST")

def gdb_from_config():
    base = os.getenv("GDB_BASE", "http://localhost:7200")
    repoid = os.getenv("GDB_REPO", "lwua23")

    endpoint = f"{ base }/repositories/{ repoid }"
    # update statements are handled at other endpoint
    updateEndpoint = endpoint + "/statements"

    log.debug(f"using endpoint {endpoint}")

    gdb = SPARQLWrapper(
        endpoint=endpoint,
        updateEndpoint=updateEndpoint,
        returnFormat=JSON,
        agent="lwua-python-sparql-client",
    )
    gdb.method = "POST"
    return gdb

gdb = gdb_from_config()

@singleton
def get_j2rdf_builder():
    template_folder = resolve_path("./lwua/templates")
    log.info(f"template_folder == {template_folder}")
    # init J2RDFSyntaxBuilder
    j2rdf = J2RDFSyntaxBuilder(templates_folder=template_folder)
    return j2rdf


def update_registry_lastmod(
    context: str, lastmod: str = None
):
    """
    Update the administration of a context.

    :param context: The context to update.
    :type context: str
    :param lastmod: The date string to update with.
    :type lastmod: str
    """
    log.info(f"update registry_of_lastmod_context on {context}")
    j2rdf = get_j2rdf_builder()

    # check if context is IRI compliant
    assert_iri_compliance(context)

    # variables for the template
    template = "update_context_lastmod.sparql"
    vars = {
        "registry_of_lastmod_context": registry_of_lastmod_context(),
        "context": context,
        "lastmod": lastmod,
    }
    # get the sparql query
    query = j2rdf.build_syntax(template, **vars)
    # log.debug(f"update_registry_lastmod query == {query}")
    # execute the query
    gdb.setQuery(query)
    gdb.query()


def assert_iri_compliance(context: str):
    assert URN_BASE in context, f"Context {context} is not IRI compliant"


def insert_graph(graph: Graph, context: str = None):
    """
    Insert data into a context.

    :param graph: The graph to insert data from.
    :type graph: Graph
    :param context: The context to insert data into.
    :type context: str
    """

    log.info(f"insert_graph into {context}")
    assert_context_exists(context)
    # Initialize the J2RDFSyntaxBuilder
    j2rdf = get_j2rdf_builder()

    assert_iri_compliance(context) if context is not None else None

    # Variables for the template
    template = "insert_graph.sparql"
    ntstr = graph.serialize(format="nt")
    vars = {"context": context, "raw_triples": ntstr}

    # Get the SPARQL query
    query = j2rdf.build_syntax(template, **vars)
    # log.debug(f"insert_graph query == {query}")

    # Execute the query
    gdb.setQuery(query)
    gdb.query()
    

def assert_context_exists(context: str):
    assert context is not None, "Context cannot be None"


def delete_graph(context: str):
    """
    Delete data from a context.

    :param context: The context to delete data from.
    :type context: str
    """

    log.info(f"delete_graph on {context}")
    assert_context_exists(context)

    # Initialize the J2RDFSyntaxBuilder
    j2rdf = get_j2rdf_builder()

    # check if context is IRI compliant
    assert_iri_compliance(context) if context is not None else None

    # Variables for the template
    template = "delete_graph.sparql"
    vars = {"context": context}

    # Get the SPARQL query
    query = j2rdf.build_syntax(template, **vars)

    # Execute the query
    gdb.setQuery(query)
    gdb.query()


def ingest_graph(graph: Graph, lastmod,  context: str, replace: bool = False):
    """
    Convert a filename to a context.

    :param fname: The filename to convert.
    :type fname: str
    :return: The context corresponding to the filename.
    :rtype: str
    """
    log.debug(f"to insert data into <{ context }>")
    assert_context_exists(context)
    # do the cleanup if possible
    if replace and context is not None:
        log.debug(f"deleting <{ context }> before insert")
        delete_graph(context)

    # insert the data
    insert_graph(graph, context)

    # convert the epoch timestamp to a date string
    date_string = datetime.utcfromtimestamp(lastmod).isoformat()
    update_registry_lastmod(context, date_string)


def named_context(name: str, base: str = URN_BASE):
    """
    Create a named context.

    :param name: The name of the context.
    :type name: str
    :param base: The base of the context. Defaults to URN_BASE.
    :type base: str, optional
    :return: The named context.
    :rtype: str
    """
    return f"{base}:{name}"  # TODO maybe consider something else?

def context_2_fname(context: str):
    """
    Convert a context to a filename path.

    :param context: The context to convert.
    :type context: str
    :return: The filename corresponding to the context.
    :rtype: str
    """
    return Path(context.replace(f"{URN_BASE}:", ""))


def fname_2_context(fname: str):
    """
    Convert a filename to a context.

    :param fname: The filename to convert.
    :type fname: str
    :return: The context corresponding to the filename.
    :rtype: str
    """
    return named_context(fname)

def date_2_epoch(date: str):
    """
    Convert a date string to an epoch timestamp.

    :param date: The date string to convert.
    :type date: str
    :return: The epoch timestamp corresponding to the date string.
    :rtype: float
    """
    return datetime.fromisoformat(date).timestamp()


def registry_of_lastmod_context():
    return named_context("ADMIN")


def get_registry_of_lastmod():
    log.info(f"getting last modified graph")

    j2rdf = get_j2rdf_builder()
    template = "lastmod_info.sparql"
    vars = {"context": registry_of_lastmod_context()}
    query = j2rdf.build_syntax(template, **vars)
    # log.debug(f"get_admin_graph query == {query}")
    gdb.setQuery(query)
    gdb.setReturnFormat(JSON)
    results = gdb.query().convert()
    
    # convert {'head': {'vars': ['graph', 'lastmod']}, 'results': {'bindings': []}} to [{PosixPath('graph'): lastmod}]
    # URI must be substracted from graph context and datetime str must be converted to epoch
    
    converted = {}
    for g in results["results"]["bindings"]:
        path = context_2_fname(g["graph"]["value"])
        time = date_2_epoch(g["lastmod"]["value"])
        converted[path] = time
    return converted
    

def suffix_2_format(suffix):
    if suffix in ["ttl", "turtle"]:
        return "turtle"
    if suffix in ["jsonld", "json"]:
        return "json-ld"
    # todo consider others if needed
    return None


def read_graph(fpath: Path, format: str = None):
    format = format or suffix_2_format(fpath.suffix)
    graph: Graph = Graph().parse(location=str(fpath), format=format)
    return graph


def delete_data_file(fname):
    context = fname_2_context(fname)
    log.info(f"deleting {fname} from {context}")
    assert_context_exists(context)
    delete_graph(context)
    update_registry_lastmod(context, None)


def ingest_data_file(fname, lastmod, replace: bool = True):
    """
    Ingest a data file.

    :param fname: The name of the file to ingest.
    :type fname: str
    :param replace: Whether to replace the existing data. Defaults to False.
    :type replace: bool
    :raises AssertionError: If the file does not exist.
    """
    file_path = data_path_from_config() / fname
    assert file_path.exists(), f"cannot ingest file at {file_path}"
    graph = read_graph(file_path)
    context = fname_2_context(fname)
    log.info(f"ingesting {file_path} into {context} | replace : {replace}")
    ingest_graph(graph, lastmod, context=context, replace=replace)
    # TODO maintain metadata triples last-ingest / last-modified of ingested
    # file in some admin graph context
