## add additional info to standardized institutes/affiliations
import pandas as pd
from pathlib import Path

PROJECTPATH = Path.cwd()
REFINFOPATH = PROJECTPATH / 'data' / 'reference_data' / 'AffiliationInfo.csv'
FOLDERPATH = PROJECTPATH / 'data'
FILEPATHS = [x for x in FOLDERPATH.iterdir() if x.stem.endswith('_standardized')]

#Load reference files
affil_info = pd.read_csv(REFINFOPATH)
affil_info.stand_institute.astype(str)

for filepath in FILEPATHS:
    filename = filepath.stem
    new_filename = filename.replace('_standardized', '_standardized_infoadded.csv')

    df = pd.read_csv(filepath, delimiter=',')

    #Standardize insitute names
    df['stand_institute'] = df['stand_institute'].fillna('NA') # because NaN is of type Int64 and can't merge between different types
    merged_df = pd.merge(df, affil_info, on='stand_institute', how='left', suffixes=('_', '_info'))

    #Write to file
    merged_df.to_csv(FOLDERPATH, new_filename, index=False) 
