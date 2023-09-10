from SPARQLWrapper import SPARQLWrapper, JSON
import logging


log = logging.getLogger(__name__)


def run_ingest():
    log.info("run_ingest")


def gdb_from_config(insert: bool = False):
    # todo get base and repoid from .env
    base = "http://localhost:7200"
    repoid = "lwua23"

    endpoint = f"{ base }/repositories/{ repoid }"
    updateEndpoint = endpoint + "/statements"   # update statements are handled at other endpoint

    gdb = SPARQLWrapper(
        endpoint=endpoint,
        updateEndpoint=updateEndpoint,
        returnFormat='json',
        agent="lwua-python-sparql-client"
    )
    gdb.method = 'POST'
    return gdb


def ingest_testing():

    file = "../../data/project.ttl"
    # todo convert the file to n3
    # for now hardcoded sample:
    n3str = """
    <http://example.com/lwua23-from-py> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <https://schema.org/Project> .
    """
    
    # define a graph -- todo find better id
    graphid = f"https://example.org/lwua23/{ file }"
    # assemble the insert statement
    inserts = f"INSERT DATA {{ GRAPH <{ graphid }> {{ { n3str } }} }}"
    print(inserts)

    gdb = gdb_from_config()
    gdb.setQuery(inserts)
    gdb.queryType = 'INSERT'  # important to indicate that the update Endpoint should be used

    results = gdb.query().convert()
    print(results)
    return results


def main():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    reqlog = logging.getLogger('requests.packages.urllib3')
    reqlog.setLevel(logging.DEBUG)
    reqlog.propagate = True

    ingest_testing()


if __name__ == '__main__':
    main()
