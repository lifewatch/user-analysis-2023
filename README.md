# user-analysis-2023

## using this project

Steps:

1. retrieve the source code from github

2. to build the services simply run 

```bash
.$ cp dotenv-example .env             # make sure you have an .env file
.$ cd docker && docker-compose build  # use docker to build the services 
```

3. to start up the services simply run 

```bash
.$ cd docker && docker-compose up     # use docker to run the services 
```

4. open the jupyter notebook

```bash
.$ xdg-open $(docker/jupyter_url.sh)  # this gets the url for the service and opens a browser to it
```

5. open the graphdb browser ui

```bash
.$ xdg-open http://localhost:7200     # opens the web ui in a browser
```

6. run a test-ingest
   
This introduces forcefully at least the data/project.ttl into the triple store
This should not be needed when the ingest runs automatically

```bash
.$ docker exec -it lwua_ingest /bin/bash            # interactively gets you into the ingest env
root@f226b253fbd4:/lwua-py# python -m lwua.ingest   # run the ingest 
```


## general plan ahead -- details to be converted into github issues

big idea is to have a central triples store for the user analysis approach
this to decouple the ingest (retrieval and semantic mapping) from the different sources from the reporting (which should be based on the assembled knowledge graph)

### for the ingest we will need a mix of strategies
* actually getting raw (non linkd) data by using dumps from webservices
* additionally uplifting those to triples (via pysubyt)
* possibly ingesting long-living reference sets through ldes client
* augmenting strategies --> starting by reading from what we already have in store, decide, then fetch more connected data, and produce more triples
* possibly add semantic reasoner
* attention to provenance triples for meta analysis ?

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

### meta & wrap up

#### release management
- to be setup 
- to consider split between reusable platform of components for generic semantic analysis & lwua23
- to organise multiple repos
- to publish images on docker-hub? elsewhere?

#### documentation 
- todo / make lists 
- probably organize into separate /docs/**md linked from this readme ? 



## documentation

### repo layout

src / py / lwua_ingest --> module for ingest, has nested ./lwua_ingest/ and ./tests/

src / py / lwua_report --> module for the pykg2tbl stuff ./lwua_teport/templates  and ./tests
                                
src / py / ipynb / *.ipynb with available ipynb sources

docker / lwua_ingest --> local docker image build space start from py3.10 image  (./.dockerignore ./Dockerfile ./entrypoint.sh )

docker --> local docker-compose environment (./docker-compose.yml)

docker / tools --> useful bash scripts to do some standard docker commands (as a local help and reference)

docs / **.md --> with useful planning / motivation / usage / etc etc docs (e.g. list-of-sources.md)

data / {source} / **.*  out of band retrieved actual files

logging / ** placeholder folder where dedicated logging from different docker-containers are grouped and put together.
