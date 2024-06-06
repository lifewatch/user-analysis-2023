import pandas as pd
from pathlib import Path
import logging

from input import read, annonymize
from affiliations import make_mapping_dict, standardize_affiliation_names, add_info

# Create a logger
logger = logging.getLogger(__name__)

# set PROJECT VARIABLES - depending on project folder structure & names
PROJECTPATH = Path.cwd()

RAWINPUT_FOLDERPATH = PROJECTPATH / "data" / "_LWUA_DataSystems_RawInput"
RAWINPUT_FILEPATHS = [x for x in RAWINPUT_FOLDERPATH.iterdir() if x.is_file()]

REFINPUT_FILEPATH = (PROJECTPATH / "data" / "reference_data" / "AffiliationMappingFile.csv")
REFINFO_FILEPATH = PROJECTPATH / "data" / "reference_data" / "AffiliationInfo.csv"

# read reference files & make mapping dictionary
affil_mapping = pd.read_csv(REFINPUT_FILEPATH)
mapping_dct = make_mapping_dict(affil_mapping)

affil_info = pd.read_csv(REFINFO_FILEPATH)
affil_info.stand_institute.astype(str)

# standardize & add info to input files
for filepath in RAWINPUT_FILEPATHS:
    filename = filepath.stem
    
    # 1. read data
    df = read(filepath)

    # 2.A annonymize data
    df_ = annonymize(df)
    logger.info(f"{filename}: annonymized ")
    # 2.B write to intermediate csv for check-up
    #filename_abstr = filename + "_abstract_TESTING.csv"
    #filepath_abstr = PROJECTPATH / "data" / filename_abstr
    #df_.to_csv(filepath_abstr, index=False)

    # 3.A standardize affiliation names based on reference data
    logger.info(f"{filename}: started standardizing...")
    df_stand, df_tostand = standardize_affiliation_names(df_, mapping_dct)
    logger.info(f"{filename}: done standardizing!")
    
    # 3.B write to intermediate csv for check-up
    #filename_stand = filename + "_standardized.csv"
    #filepath_stand = PROJECTPATH / "data" / filename_stand    
    # df_stand.to_csv(filepath_stand, index=False)
    
    # 3.C write to-stand-affiliations to csv 
    filename_to_stand = filename + "_to_standardize.csv"
    filepath_to_stand = PROJECTPATH / "data" / filename_to_stand
    df_tostand.to_csv(filepath_to_stand, index=False)

    # 4.A add info to standardized affiliation names
    df__ = add_info(df_stand, affil_info)
    
    # 4.B write to intermediate csv for check-up
    filename_infoadded = filename + "_info_added.csv"
    filepath_infoadded = PROJECTPATH / "data" / filename_infoadded
    df__.to_csv(filepath_infoadded, index=False)
