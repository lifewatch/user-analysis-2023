## Standardize the institute names
import pandas as pd
from pathlib import Path
from collections import defaultdict

#Functions
def make_mapping_dict(affil_mapping: pd.DataFrame) -> dict:

    """
    Turn the reference mapping file into a dictionary with structure:
        {stand-affiliation-name : [all possible ways of writing affil name] }
    """

    mapping_dct = defaultdict(list)
    return [mapping_dct[row['Institute_standardized']].append(row['Institute']) for index, row in affil_mapping.iterrows()]


def standardize_affiliation_names(df: pd.DataFrame, mapping_dct: dict) -> pd.DataFrame:

    """
    Add standardized insitute names to df using as mapping dict

    returns 
    df with standard institute names added in a new column
    df consisting of institute names that couldn't be standardized yet
    """
        
    for index, row in df.iterrows():
        for stand_inst, inst_list in mapping_dct.items():
            if row['raw_institute'] in inst_list or str(row['raw_institute']).lower() in inst_list:
                df.at[index, 'stand_institute'] = stand_inst  

    df_tostand = df.loc[df['stand_institute'].isnull()]
    df_tostand = df_tostand.drop_duplicates()

    return df, df_tostand


# CODE
PROJECTPATH = Path.cwd()
FOLDERPATH = PROJECTPATH / 'data'
FILEPATHS = [x for x in FOLDERPATH.iterdir() if x.stem.endswith('_abstract')]
REFAFFILPATH = PROJECTPATH / 'data' / 'reference_data' / 'AffiliationMappingFile.csv'

affil_mapping = pd.read_csv(REFAFFILPATH)
mapping_dct = make_mapping_dict(affil_mapping)
#print(mapping_dct['Flanders Marine Institute (VLIZ)'])

for filepath in FILEPATHS:
    filename = filepath.stem
    filename_stand = filename.replace('_abstract', '_standardized.csv')
    filepath_stand = Path(FOLDERPATH, filename_stand)
    filename_to_stand = filename.replace('_abstract', '_to_standardize.csv')
    filepath_to_stand = Path(FOLDERPATH, filename_to_stand)

    #read input
    df = pd.read_csv(filepath, delimiter=',')

    #standardize affiliation names
    print(f"standardizing {filename}...")
    df_stand, df_tostand = standardize_affiliation_names(df, mapping_dct)
    print("done!")

    # write df to file, and subset of non-stand names to seperate file for manual check
    df_stand.to_csv(filepath_stand, index=False) 
    df_tostand.to_csv(filepath_to_stand, index=False) 
