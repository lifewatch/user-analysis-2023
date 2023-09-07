# user-analysis-2023

## using this project

Steps:
1. retrieve the source code from github
2. to start up the services simply run 

```bash
.$ touch .env # make sure you have an .env file
.$ cd docker
./docker$ docker-compose up
```



## general plan 

big idea is to have a central triples store for the user analysis approach
this to decouple the ingest (retrieval and semantic mapping) from the different sources from the reporting (which should be based on the assembled knowledge graph)

### for the ingest we will need a mix if strategies
* actually getting data by using dumps our webservices
* additionally uplifting thos to triples (via pysubyt)
* possibly ingesting long-living reference sets through ldes client


#### Ingest Tasks
- identify sources (dumps, werbservices or sparql endpoints)
- code automated retrieval (possibly adding some uritemplating)
- apply uplifting where needed
- code ingest into triple store


### for the reporting
- identify named queries and required resultsets
- code the sparql for the queries
- make multiple ipynb for 
  - testing + 
  - full automated report (investigate producing latex / pdf / md / html ...)

#### reporting tasks

- list and code sparql queries
- build ipynb reports



### model-design
* identify the shape of the graph we will use and how all items will be linked together
* source for uplifting and querying

### additional RDF tooling and opportunities
- optionally consider validation steps (if we have a e.g a shacl for the model) 
- optionally conswer reasoning to introduce derived triples based on rules (extra step after ingest) 



### for the deployment of this

* we use docker-compose to launch the various microservices
* graphdb triple store (existing docker image)
* own ingest system 
* ipynb server (existing docker images) with connection to graphdb
  + env that can load pykg2table and has access to our own named queries

#### Deploy Tasks
- dev env on laptop for running docker
- ssh access to docker-dev --> agreed location in /data
- find docker images
- build own local ingest-image
- deploy at docker-dev
- setup ci/cd for autodeploy



## repo layout

src / py / lwua_ingest --> module for ingest, has nested ./lwua_ingest/ and ./tests/

src / py / lwua_report --> module for the pykg2tbl stuff ./lwua_teport/templates  and ./tests
                                
src / py / ipynb / *.ipynb with available ipynb sources

docker / lwua_ingest --> local docker image build space start from py3.10 image  (./.dockerignore ./Dockerfile ./entrypoint.sh )

docker --> local docker-compose environment (./docker-compose.yml)

docker / tools --> useful bash scripts to do some standard docker commands (as a local help and reference)

docs / **.md --> with useful planning / motivation / usage / etc etc docs (e.g. list-of-sources.md)

data / {source} / **.*  out of band retrieved actual files
