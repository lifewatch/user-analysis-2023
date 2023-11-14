## Standardize the institute names
import pandas as pd
import os
from collections import defaultdict

CURRENTPATH = os.path.dirname(os.path.realpath(__file__))
PROJECTPATH = os.path.abspath(os.path.join(CURRENTPATH, '..', '..', '..'))

#Load reference files
REFPATH = os.path.join(PROJECTPATH, 'data', 'reference_data')
affil_mapping = pd.read_csv(os.path.join(REFPATH, 'AffiliationMappingFile.csv'))

# turn mapping file into dictionary
mapping_dct = defaultdict(list)
[mapping_dct[row['Institute_standardized']].append(row['Institute']) for index, row in affil_mapping.iterrows()]
#print(mapping_dct['Flanders Marine Institute (VLIZ)'])

#Load '*_abstract' input files
FOLDERPATH = os.path.join(PROJECTPATH, 'data')
files = [item for item in os.listdir(FOLDERPATH) if item.endswith('_abstract.csv')]

for file in files:
    filename = os.path.splitext(os.path.basename(file))[0]
    filepath = os.path.join(FOLDERPATH, file)
    df = pd.read_csv(filepath, delimiter=',')

    #Standardize insitute names
    print(f"standardizing {filename}...")
    for index, row in df.iterrows():
        for stand_inst, inst_list in mapping_dct.items():
            if row['raw_institute'] in inst_list or str(row['raw_institute']).lower() in inst_list:
                df.at[index, 'stand_institute'] = stand_inst  
    print("done!")

    # write to file
    df.to_csv(os.path.join(FOLDERPATH, filename.replace('_abstract', '_standardized.csv')), index=False) 

    # write non-standardized institutes to separate file for manual check
    df_tostand = df.loc[df['stand_institute'].isnull()]
    df_tostand = df_tostand.drop_duplicates()
    df_tostand.to_csv(os.path.join(FOLDERPATH, filename.replace('_abstract', '_to_standardize.csv')), index=False) 
