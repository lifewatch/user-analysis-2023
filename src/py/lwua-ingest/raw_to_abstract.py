## Turn raw input files into files with institutes that can be standardized & made public
import pandas as pd
import os

CURRENTPATH = os.path.dirname(os.path.realpath(__file__))
PROJECTPATH = os.path.abspath(os.path.join(CURRENTPATH, '..', '..', '..'))

#Read input
FOLDERPATH = os.path.join(PROJECTPATH, 'data', '_LWUA_DataSystems_RawInput')
files = [item for item in os.listdir(FOLDERPATH) if os.path.isfile(os.path.join(FOLDERPATH, item))]

for file in files:
    filename = os.path.splitext(os.path.basename(file))[0]
    filepath = os.path.join(FOLDERPATH, file)

    if file.endswith('.csv'):
        df = pd.read_csv(filepath, delimiter=';')  # Use pd.read_excel() for Excel files
    if file.endswith('.txt'):
        df = pd.read_csv(filepath, delimiter='\t')

    df.columns = df.columns.str.lower()
    
    #Make df --> to standardize & that can be made public
    df_ = pd.DataFrame()
    if 'email' in df.columns: 
        _mailEnds = [email_lst[-1] for email_lst in df['email'].str.split("@")] 
        _split_mailsEnds = [mail_end.split('.')for mail_end in _mailEnds]
        
        df_['raw_country'] = [item_lst[-1] for item_lst in _split_mailsEnds]
        df_['raw_institute'] = [''.join(item_lst[0:-1]) for item_lst in _split_mailsEnds]

    if 'institute' in df.columns:
        df_['raw_institute'] = df['institute']

    df_['raw_source'] = filename

    #write to new files in data folder
    df_.to_csv(os.path.join(PROJECTPATH, 'data', filename+'_abstract.csv'), index=False) 