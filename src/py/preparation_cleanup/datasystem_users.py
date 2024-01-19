import pandas as pd
import openpyxl
from itertools import islice
from pathlib import Path, PosixPath
from collections import defaultdict
import uuid

## Functions
def read_input(filepath: PosixPath) -> pd.DataFrame:

    """ Reads data at given filepath into a Dataframe with filename added to 'source' column """

    if filepath.suffix == '.csv':
        df = pd.read_csv(filepath, delimiter=';')
    if filepath.suffix == '.txt':
        df = pd.read_csv(filepath, delimiter='\t')
    if filepath.suffix == '.xlsx' or filepath.suffix == '.xls':
        wb = openpyxl.load_workbook(filepath)
        ws = wb.active 
        data = ws.values
        cols = next(data)[1:]
        data = list(data)
        idx = [r[0] for r in data]
        data = (islice(r, 1, None) for r in data)
        df = pd.DataFrame(data, index=idx, columns=cols)
        print("df: ", df)
        print("df-type: ", type(df))
    #add other file configurations if necessary
    
    df['source'] = filepath.stem
    
    return df


def annonymize_input(df: pd.DataFrame) -> pd.DataFrame:

    """ Abstractifies personal information from a Dataframe """
    
    df.columns = df.columns.str.lower()
    
    df_ = pd.DataFrame()
    if 'email' in df.columns: #overwritten if more specific information is available
        try:
            _mailEnds = [email_lst[-1] for email_lst in df['email'].str.split("@")] 
            _split_mailsEnds = [mail_end.split('.')for mail_end in _mailEnds]
        
            df_['raw_country'] = [item_lst[-1] for item_lst in _split_mailsEnds]
            df_['raw_institute'] = [''.join(item_lst[0:-1]) for item_lst in _split_mailsEnds]
        except:
            df_['raw_country'] = df['email']
            df_['raw_institute'] = df['email']

    if 'institute' in df.columns:
        df_['raw_institute'] = df['institute']

    if 'organisation' in df.columns:
        df_['raw_institute'] = df['organisation']

    df_['identifier'] = [uuid.uuid4() for _ in range(len(df_))]
    
    return df_


def make_mapping_dict(affil_mapping: pd.DataFrame) -> dict:

    """
    Turn the reference mapping file into a dictionary with structure:
        {stand-affiliation-name : [all possible ways of writing affil name] }
    """

    mapping_dct = defaultdict(list)
    for i in affil_mapping.index:
        if affil_mapping['Institute_standardized'][i] not in mapping_dct.keys():
            mapping_dct[affil_mapping['Institute_standardized'][i]] = [affil_mapping['Institute'][i]]
        else:
            mapping_dct[affil_mapping['Institute_standardized'][i]].append(affil_mapping['Institute'][i])

    return mapping_dct

def standardize_affiliation_names(df: pd.DataFrame, mapping_dct: dict) -> pd.DataFrame:

    """
    Add standardized insitute names to df using as mapping dict

    returns 
    df with standard institute names added in a new column
    df consisting of institute names that couldn't be standardized yet
    """
    
    df['stand_institute'] = ''
    for index, row in df.iterrows():
        for stand_inst, inst_list in mapping_dct.items():
            if row['raw_institute'] in inst_list or str(row['raw_institute']).lower().strip() in inst_list:
                df.at[index, 'stand_institute'] = stand_inst

    df_tostand = df.loc[df['stand_institute'] == '']
    df_tostand = df_tostand.drop_duplicates()

    return df, df_tostand

def add_info(df: pd.DataFrame, affil_info: pd.DataFrame) -> pd.DataFrame:

    """ Add information linked to standardized affiliation name """

    df['stand_institute'] = df['stand_institute'].fillna('NA') # because NaN is of type Int64 and can't merge between different types
    merged_df = pd.merge(df, affil_info, on='stand_institute', how='left', suffixes=('_', '_info'))

    return merged_df


## PROJECT VARIABLES - depending on project folder structure & names
PROJECTPATH = Path.cwd()

RAWINPUT_FOLDERPATH = PROJECTPATH / 'data' / '_LWUA_DataSystems_RawInput'
RAWINPUT_FILEPATHS = [x for x in RAWINPUT_FOLDERPATH.iterdir() if x.is_file()]

REFINPUT_FILEPATH = PROJECTPATH / 'data' / 'reference_data' / 'AffiliationMappingFile.csv'
REFINFO_FILEPATH = PROJECTPATH / 'data' / 'reference_data' / 'AffiliationInfo.csv'

## CODE
# read reference files & make mapping dictionary
affil_mapping = pd.read_csv(REFINPUT_FILEPATH)
mapping_dct = make_mapping_dict(affil_mapping)

affil_info = pd.read_csv(REFINFO_FILEPATH)
affil_info.stand_institute.astype(str)

#standardize & add info to input files
for filepath in RAWINPUT_FILEPATHS:
    filename = filepath.stem
    print("filename: ", filename)
    print("filepath: ", filepath)
    # 1. read data
    df = read_input(filepath)

    # 2. annonymize data (& write to intermediate csv for check-up)
    filename_abstr = filename + '_abstract.csv'
    filepath_abstr = PROJECTPATH / 'data' / filename_abstr
    
    df_ = annonymize_input(df)
    
    df_.to_csv(filepath_abstr, index=False) 

    # 3. standardize affiliation names based on reference data (& write to intermediate csv for check-up)
    filename_stand = filename + '_standardized.csv'
    filepath_stand = PROJECTPATH / 'data' / filename_stand

    filename_to_stand = filename + '_to_standardize.csv'
    filepath_to_stand = PROJECTPATH / 'data' / filename_to_stand

    print(f"standardizing {filename}...")
    df_stand, df_tostand = standardize_affiliation_names(df_, mapping_dct)
    print("done!")
    
    df_stand.to_csv(filepath_stand, index=False) 
    df_tostand.to_csv(filepath_to_stand, index=False) 

    # 4. add info to standardized affiliation names (& write to intermediate csv for check-up)
    filename_infoadded = filename + '_info_added.csv'
    filepath_infoadded = PROJECTPATH / 'data' / filename_infoadded

    df__ = add_info(df_, affil_info)
    
    df__.to_csv(filepath_infoadded, index=False) 
 
