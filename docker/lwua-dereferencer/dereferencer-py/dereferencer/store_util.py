# all functions that involve changing and getting something from a given store

from rdflib import Graph
import logging
from pyrdfj2 import J2RDFSyntaxBuilder
import os
from .helpers import resolve_path

# from dotenv import load_dotenv

log = logging.getLogger(__name__)
URN_BASE = os.getenv("URN_BASE", "urn:lwua:INGEST")


def get_j2rdf_builder():
    template_folder = resolve_path("./dereferencer/templates")
    log.info(f"template_folder == {template_folder}")
    # init J2RDFSyntaxBuilder
    j2rdf = J2RDFSyntaxBuilder(
        templates_folder=template_folder,
        extra_functions={"registry_of_lastmod_context": f"{URN_BASE}:ADMIN"},
    )
    return j2rdf


J2RDF = get_j2rdf_builder()


def getURIsFromStore(store: Graph, property_path: str, url: str):
    template = "deref_property_path.sparql"
    vars = {"subject": url, "property": property_path}

    query = J2RDF.build_syntax(template, **vars)
    log.debug(f"getURIsFromStore: {query}")
    results = store.query(query)
    # get the results as a list
    results_list = [str(result[0]) for result in results]
    log.debug(f"results_list: {results_list}")
    return results_list
