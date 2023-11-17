# this file will be used to trigger the injest processes into graphdb
# this prevents the injest.py and tryout_watch.py to be run at the same time with conflicting circular imports

from SPARQLWrapper import SPARQLWrapper, JSON
from pathlib import Path
import logging
from rdflib import Graph
import time
import os
from dotenv import load_dotenv
from .helpers import enable_logging, resolve_path
from pyrdfj2 import J2RDFSyntaxBuilder

log = logging.getLogger(__name__)
URN_BASE = os.getenv("URN_BASE", "urn:lwua:INGEST")

def data_path_from_config():
    local_default = str(resolve_path("./data", versus="dotenv"))
    folder_name = os.getenv("INGEST_DATA_FOLDER", local_default)
    return Path(folder_name).absolute()

def gdb_from_config():
    base = os.getenv("GDB_BASE", "http://localhost:7200")
    repoid = os.getenv("GDB_REPO", "lwua23")

    endpoint = f"{ base }/repositories/{ repoid }"
    updateEndpoint = endpoint + "/statements"   # update statements are handled at other endpoint

    log.debug(f"using endpoint {endpoint}")

    gdb = SPARQLWrapper(
        endpoint=endpoint,
        updateEndpoint=updateEndpoint,
        returnFormat=JSON,
        agent="lwua-python-sparql-client"
    )
    gdb.method = 'POST'
    return gdb

def get_j2rdf_builder():
    template_folder = resolve_path("./lwua/templates", versus="dotenv")
    #log.info(f"template_folder == {template_folder}")
    #init J2RDFSyntaxBuilder
    j2rdf = J2RDFSyntaxBuilder(templates_folder=template_folder)
    return j2rdf

def update_context_admin(context: str, gdb: SPARQLWrapper = None, lastmod: str= None):
    """Update the last modified time of a context in the admin graph

    Args:
        context (str): The context to update the last modified time of
        gdb (SPARQLWrapper, optional): the SPARQLWrapper to post to. Defaults to None.
        lastmod (str, optional): epoch time. Defaults to None.
    """
    log.info(f"update_context_admin on {context}")
    j2rdf = get_j2rdf_builder()
    
    # check if context is IRI compliant
    context = check_iri_compliance(context)
    
    #variables for the template
    template = "update.sparql"
    vars = {
        "admin_graph": admin_context(),
        "context": context,
        "lastmod": lastmod
    }
    #get the sparql query
    query = j2rdf.build_syntax(template, **vars)
    #log.debug(f"update_context_admin query == {query}")
    #execute the query
    gdb.setQuery(query)
    gdb.query()
    
def check_iri_compliance(context: str):
    if URN_BASE not in context:
        context = named_context(context)
    return context

    
def insert_data(graph: Graph, context: str = None, gdb: SPARQLWrapper = None):
    """Insert data into a context in the graph database

    Args:
        graph (Graph): The graph to insert data from
        context (str): The context to insert data into
        gdb (SPARQLWrapper): The SPARQLWrapper to post to
    """
    
    log.info(f"insert_data into {context}")
    
    # Get the SPARQLWrapper
    gdb = gdb_from_config() if gdb is None else gdb
    
    # Initialize the J2RDFSyntaxBuilder
    j2rdf = get_j2rdf_builder()
    
    #check if context is IRI compliant if context is not None
    context = check_iri_compliance(context) if context is not None else None

    # Variables for the template
    template = "insert_data.sparql"
    ntstr = graph.serialize(format="nt")
    vars = {
        "context": context,
        "data": ntstr
    }

    # Get the SPARQL query
    query = j2rdf.build_syntax(template, **vars)
    #log.debug(f"insert_data query == {query}")
    
    # Execute the query
    gdb.setQuery(query)
    gdb.query()
    
def delete_data(context: str = None, gdb: SPARQLWrapper = None):
    """Delete data from a context in the graph database

    Args:
        context (str): The context to delete data from (if None, delete all data)
        gdb (SPARQLWrapper): The SPARQLWrapper to post to
    """
    
    log.info(f"delete_data on {context}")
    
    # Get the SPARQLWrapper
    gdb = gdb_from_config() if gdb is None else gdb
    
    # Initialize the J2RDFSyntaxBuilder
    j2rdf = get_j2rdf_builder()
    
    #check if context is IRI compliant
    context = check_iri_compliance(context) if context is not None else None

    # Variables for the template
    template = "delete_data.sparql"
    vars = {
        "context": context
    }

    # Get the SPARQL query
    query = j2rdf.build_syntax(template, **vars)

    # Execute the query
    gdb.setQuery(query)
    gdb.query()
    
def ingest_graph(graph: Graph, context: str = None, replace: bool = False):
    log.debug(f"to insert data into <{ context }>")
    gdb = gdb_from_config()
    # do the cleanup if possible
    if replace and context is not None:
        log.debug(f"deleting <{ context }> before insert")
        delete_data(context, gdb)
   
    # insert the data
    insert_data(graph, context, gdb)
    
    #get the time
    c_time = time.time()
    update_context_admin(context, gdb, c_time)

def named_context(name: str, base: str = URN_BASE):
    return f"{base}:{name}"   # TODO maybe consider something else?

def fname_2_context(fname: str):
    #return named_context(f"data/{fname}") # /data prefix is not needed until we have multiple data folders to ingest from
    return named_context(fname)

def admin_context():
    return named_context("ADMIN")

def get_admin_graph(gdb: SPARQLWrapper = None):
    
    log.info(f"get_admin_graph")
    
    if gdb is None:
        gdb = gdb_from_config()
    
    j2rdf = get_j2rdf_builder()
    template = "get_admin.sparql"
    vars = {
        "admin_context": admin_context()
    }
    query = j2rdf.build_syntax(template, **vars)
    #log.debug(f"get_admin_graph query == {query}")
    gdb.setQuery(query)
    gdb.setReturnFormat(JSON)
    results = gdb.query().convert()
    return results

def delete_all_graphs(gdb):
    delete_data(None, gdb)

def delete_graph(context: str,gdb: SPARQLWrapper= None):
    if gdb is None:
        gdb = gdb_from_config()
    delete_data(context, gdb)
    update_context_admin(context, gdb, None)

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
    delete_graph(context)

def ingest_data_file(fname, replace: bool = False):
    file_path = data_path_from_config() / fname
    assert file_path.exists(), f"cannot ingest file at {file_path}"
    graph = read_graph(file_path)
    context = fname_2_context(fname)
    log.info(f"ingesting {file_path} into {context} | replace : {replace}")
    ingest_graph(graph, context=context, replace=replace)
    # TODO maintain metadata triples last-ingest / last-modified of ingested file in some admin graph context
