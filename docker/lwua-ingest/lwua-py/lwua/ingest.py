from SPARQLWrapper import SPARQLWrapper, JSON
from pathlib import Path
import logging
from rdflib import Graph
import os
from dotenv import load_dotenv


log = logging.getLogger(__name__)


def run_ingest():
    data_path = data_path_from_config()
    log.info(f"run_ingest on updated files in {data_path}")
    # TODO -- immplement steps
    # list all the contents (files) in data_path together with last mod
    # get the <#admin-luwa-ingest> graph listing the maintained named-graphs and their lastmod
    # there nees to be a mapping between filenames and named-graphs !
    # check which filenames are younger then their named-graph equivalent
    # read them into mem - replace the coresponding named-graph in the repo
    # update the triple for the named-graph to lastmod in the admin grap


def data_path_from_config():
    folder_name = os.getenv("GDB_DATA_FOLDER", "/root/graphdb-import/data")
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


def ingest_graph(graph, gname: str = None, replace: bool = False):
    log.debug(f"to insert data into <{ gname }>")

    gdb = gdb_from_config()

    # do the cleanup if possible
    if replace and gname is not None:
        pass   # TODO execute delete of full graph -- have to check syntax

    # extract the triples and format the insert statement
    ntstr = graph.serialize(format="nt")
    log.debug(f"extracted tiples == { ntstr }")
    if gname is not None:
        inserts = f"INSERT DATA {{ GRAPH <{ gname }> {{ { ntstr } }} }}"
    else:
        inserts = f"INSERT DATA {{ { ntstr} }}"
    log.debug(f"INSERT of ==> { inserts }")

    gdb.setQuery(inserts)
    log.debug(f"detected querytype == {gdb.queryType}")

    # unsure if this is needed -- can sqlwrapper detect this automatically?
    gdb.queryType = 'INSERT'  # important to indicate that the update Endpoint should be used

    gdb.query()


def fname_2_gname(fname):
    return f"urn:lwua:data/{fname}"   # TODO maybe consider something else?


def suffix_2_format(suffix):
    if suffix in ["ttl", "turtle"]:
        return "turtle"
    if suffix in ["jsonld", "json"]:
        return "json-ld"
    # todo consider others if needed
    return None


def read_graph(fpath: Path, format: str = None):
    format = format or suffix_2_format(fpath.suffix)
    graph = Graph().parse(location=str(fpath), format=format)
    return graph


def ingest_data_file(fname):
    file_path = data_path_from_config() / fname
    assert file_path.exists(), f"cannot ingest file at {file_path}"

    gname = fname_2_gname(fname)
    graph = read_graph(file_path)

    ingest_graph(graph, gname=gname)


# Note: this main method allows to locally test outside docker
# directly connecting to a localhost graphdb endpoint (which might be inside docker!)
def main():
    load_dotenv()
    ingest_data_file("project.ttl")
    # todo 
    # run_ingest()


if __name__ == '__main__':
    main()
