## add additional info to standardized institutes/affiliations
import pandas as pd
import os

CURRENTPATH = os.path.dirname(os.path.realpath(__file__))
PROJECTPATH = os.path.abspath(os.path.join(CURRENTPATH, '..', '..', '..'))

#Load reference files
REFPATH = os.path.join(PROJECTPATH, 'data', 'reference_data')
affil_info = pd.read_csv(os.path.join(REFPATH, 'AffiliationInfo.csv'))
affil_info.stand_institute.astype(str)

#Load '*_standardized.csv' input files
FOLDERPATH = os.path.join(PROJECTPATH, 'data')
files = [item for item in os.listdir(FOLDERPATH) if item.endswith('_standardized.csv')]

for file in files:
    filename = os.path.splitext(os.path.basename(file))[0]
    filepath = os.path.join(FOLDERPATH, file)
    df = pd.read_csv(filepath, delimiter=',')

    #Standardize insitute names
    df['stand_institute'] = df['stand_institute'].fillna('NA') # because NaN is of type Int64 and can't merge between different types
    merged_df = pd.merge(df, affil_info, on='stand_institute', how='left', suffixes=('_', '_info'))

    #Write to file
    merged_df.to_csv(os.path.join(FOLDERPATH, filename.replace('_standardized', '_standardized_infoadded.csv')), index=False) 
