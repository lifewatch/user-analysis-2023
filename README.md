# LifeWatch user-analysis

*A KGAP implementation for the LifeWatch user analysis.*

## Steps to start up this K-GAP project

1. retrieve the source code from github

2. to build the services simply run 

```bash
.$ cp dotenv-example .env             # make sure you have an .env file
.$ cd docker && docker-compose build  # use docker to build the services 
```

3. to start up the services simply run 

```bash
.$ cd docker && docker compose up     # use docker to run the services 
```

4. open the jupyter notebook
 
- http://localhost:8889/
- ```bash
  .$ xdg-open $(docker/jupyter_url.sh)  # this gets the url for the service and opens a browser to it
  ```

5. open the graphdb browser ui

- http://localhost:7201/
- ```bash
  .$ xdg-open http://localhost:7200     # opens the web ui in a browser
  ```


## Updates

With each yearly update of the lwua, following folders need to be updated: 
- **./data/_LWUA_DataSystems_RawInput/**  
This folder contains the raw input files.  
Please follow spreadsheet structure of csv files present.

- **./data/reference_data/**  
This folder contains 2 files that need to be updated when new affiliations occur in the input data:  
*AffiliationInfo.csv*  
--> Manually curated list of standardized reference affiliations, with information added about the country, QH, group, ...  
*AffiliationMappingFile.csv*  
--> Mapping between standardized affiliation names and other possible writings of affiliation names  

## Folder structure

**./notebooks/**  
--> contains the Jupyter notebooks with statistics for the LWUA. (see notebooks for description of content itself)   

**./data/**  
--> contains the data used in the LWUA.

**./templates/**  
--> contains the templates used to semantically uplift input data into RDF.

**./src/py/**  
--> contains the pythons scripts used to standardize affliations information

**./config/**  
--> contains the sembench.yaml files that lists the tasks that need to be executed when running this kgap project. 