from SPARQLWrapper import SPARQLWrapper, JSON
import logging


log = logging.getLogger(__name__)


def run_ingest():
    log.info("run_ingest")


def temp_code_testing():
    hostname = "localhost"
    port = 7200
    repoid = "lwua23"

    sparql = SPARQLWrapper(f"http://{ hostname }:{ port }/repositories/{ repoid }")

    file = "data/project.ttl"
    # convert the file to n3
    n3str = """
    <http://example.com/lwua23> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <https://schema.org/Project> .
    """
    graphid = f"https://example.org/lwua23/{ file }"
    inserts = f"INSERT DATA {{ GRAPH <{ graphid }> { n3str } }}"

    sparql.setQuery(inserts)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results
