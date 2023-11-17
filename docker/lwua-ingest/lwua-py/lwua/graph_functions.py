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

log = logging.getLogger(__name__)
URN_BASE = "urn:lwua:INGEST"

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

def ingest_graph(graph: Graph, context: str = None, replace: bool = False):
    log.debug(f"to insert data into <{ context }>")

    gdb = gdb_from_config()

    # do the cleanup if possible
    if replace and context is not None:
        log.debug(f"deleting <{ context }> before insert")
        delete_graph(context, gdb)
        
    # extract the triples and format the insert statement
    ntstr = graph.serialize(format="nt")
    #log.debug(f"extracted tiples == { ntstr }") # comented out because it is too verbose
    if context is not None:
        inserts = f"INSERT DATA {{ GRAPH <{ context }> {{ { ntstr } }} }}"
    else:
        inserts = f"INSERT DATA {{ { ntstr} }}"
    #log.debug(f"INSERT of ==> { inserts }")

    gdb.setQuery(inserts)
    log.debug(f"detected querytype == {gdb.queryType}")

    # unsure if this is needed -- can sqlwrapper detect this automatically?
    gdb.queryType = 'INSERT'  # important to indicate that the update Endpoint should be used
    gdb.query()
    register_context_lastmod(context,gdb)

def named_context(name: str, base: str = URN_BASE):
    return f"{base}:{name}"   # TODO maybe consider something else?

def fname_2_context(fname: str):
    #return named_context(f"data/{fname}") # /data prefix is not needed until we have multiple data folders to ingest from
    return named_context(fname)

def admin_context():
    return named_context("ADMIN")

def register_context_lastmod(context: str, gdb: SPARQLWrapper = None):
    if URN_BASE not in context:
        context = named_context(context)
    if gdb is None:
        gdb = gdb_from_config()
        
    c_time = time.time()
    
    #check if the context is already in the admin graph, if so check if the last modified time of the return is smaller than the current time
    #if so, update the last modified time of the context
    #if not, do nothing
    lastmod = get_context_lastmod(context,gdb)
    if lastmod['results']['bindings']:
        if float(lastmod['results']['bindings'][0]['m']['value']) < c_time:
            #delete the old last modified time
            delete_context_from_admin(context,gdb)
    
    #tsparql for insert
    # GRAPH <{ admin_context() }> {{ <{ context }> <https://schema.org/dateModified> \"{time.time()}\"^^<http://www.w3.org/2001/XMLSchema#double> }}
    inserts = f"INSERT DATA {{ GRAPH <{ admin_context() }> {{ <{ context }> <https://schema.org/dateModified> \"{time.time()}\"^^<http://www.w3.org/2001/XMLSchema#double> }} }}"
    gdb.setQuery(inserts)
    gdb.queryType = 'INSERT'
    gdb.query()

def get_context_lastmod(context: str, gdb: SPARQLWrapper = None):
    if URN_BASE not in context:
        context = named_context(context)
    if gdb is None:
        gdb = gdb_from_config()
    #get last modified time of context
    query = f"SELECT ?m WHERE {{ GRAPH <{ admin_context() }> {{ <{ context }> <https://schema.org/dateModified> ?m }} }}"
    gdb.setQuery(query)
    gdb.setReturnFormat(JSON)
    results = gdb.query().convert()
    return results

def get_admin_graph(gdb: SPARQLWrapper = None):
    if gdb is None:
        gdb = gdb_from_config()
    #get full admin graph
    query = f"SELECT ?g ?m WHERE {{ GRAPH <{ admin_context() }> {{ ?g <https://schema.org/dateModified> ?m }} }}"
    gdb.setQuery(query)
    gdb.setReturnFormat(JSON)
    results = gdb.query().convert()
    return results


def delete_context_from_admin(context: str, gdb: SPARQLWrapper = None):
    if URN_BASE not in context:
        context = named_context(context)
    if gdb is None:
        gdb = gdb_from_config()
    deletes = f"DELETE WHERE {{ GRAPH <{ admin_context() }> {{ <{ context }> <https://schema.org/dateModified> ?m }} }}"
    gdb.setQuery(deletes)
    gdb.queryType = 'DELETE'
    gdb.query()

def delete_all_graphs(gdb):
    deletes = f"DELETE WHERE {{ GRAPH ?g {{ ?s ?p ?o }} }}"
    gdb.setQuery(deletes)
    gdb.queryType = 'DELETE'
    gdb.query()

def delete_graph(context: str,gdb: SPARQLWrapper= None):
    if URN_BASE not in context:
        context = named_context(context)
    if gdb is None:
        gdb = gdb_from_config()
    deletes = f"DELETE WHERE {{ GRAPH <{ context }> {{ ?s ?p ?o }} }}"
    gdb.setQuery(deletes)
    gdb.queryType = 'DELETE'
    gdb.query()
    
    #delete the graph from the admin graph
    delete_context_from_admin(context,gdb)

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

def ingest_data_file(fname, context: str = None, replace: bool = False):
    file_path = data_path_from_config() / fname
    assert file_path.exists(), f"cannot ingest file at {file_path}"

    graph = read_graph(file_path)
    
    if context is None:
        context = fname_2_context(fname)
    
    log.info(f"ingesting {file_path} into {context} | replace : {replace}")

    ingest_graph(graph, context=context, replace=replace)
    # TODO maintain metadata triples last-ingest / last-modified of ingested file in some admin graph context
