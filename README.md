# LifeWatch user-analysis

*A KGAP implementation for the LifeWatch user analysis.*

#### Folder structure

*./notebooks/*  
--> contains the Jupyter notebooks with statistics for the LWUA. (see notebooks for description of content itself)   

*./data/*  
--> contains the data used in the LWUA.

*./templates/*  
--> contains the templates used to semantically uplift input data into RDF.

*./src/py/*  
--> contains the pythons scripts used for data clean-up & affiliation standardization

*./config/*  
--> contains the sembench.yaml files that lists the tasks that will be executed when running this kgap project. 



## Updates

#### Yearly updates

With each yearly update of the lwua, following steps need to be performed: 
- Update the input files in **./data/_LWUA_DataSystems_RawInput/**   
Please follow spreadsheet structure of csv files present.

- Run the following to clean-up and standardize the updated raw input files:
  ```bash
  $ python src/py/preparation_cleanup/standardizeDatasystemUsers.py
  ```

- [Start the kgap project](##Steps-to-start-up-this-KGAP-project), this will prompt the execution of the steps listed in config/sembench.yaml

#### Standardization updates

Affiliations that still have to be standardized are listed in files ending with: *_to_standardize.csv*  
Standardization procedure to follow:  
- Identify the affiliations by looking up the affiliation name on the web
- Check presence of affiliation in both  
*./data/reference_data/AffiliationInfo.csv* and  
*./data/reference_data/AffiliationMappingFile.csv* 
  - **present**: this is a new way of writing the affiliation name  
  -> add the affiliation name and associated standard affiliation to the *AffiliationMappingFile.csv*  
  - **not present**: this is a completely new affiliation  
  -> **Add** the new standard affiliation name to **./data/reference_data/AffiliationInfo.csv** and look up necessary information such as QH, group, country, ...  
  -> **Add** the affiliation name and associated standard affiliation to the **./data/reference_data/AffiliationMappingFile.csv**  !

## Steps to start up this KGAP project

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
