import pandas as pd
from pathlib import Path
import uuid

#Functions 
def read_input(filepath: pathlib.PosixPath) -> pd.DataFrame:

    """
    Takes input file and returns Dataframe with filename added as column
    """

    if filepath.suffix == '.csv':
        df = pd.read_csv(filepath, delimiter=';')  # Use pd.read_excel() for Excel files
    if filepath.suffix == '.txt':
        df = pd.read_csv(filepath, delimiter='\t')
    
    df['source'] = filepath.stem
    
    return df


def annonymize_input(df: pd.DataFrame) -> pd.DataFrame:

    """
    Takes an pd.Dataframe containing personal information and returns the annonimized version of it
    """
    
    df.columns = df.columns.str.lower()
    
    df_ = pd.DataFrame()
    if 'email' in df.columns: 
        _mailEnds = [email_lst[-1] for email_lst in df['email'].str.split("@")] 
        _split_mailsEnds = [mail_end.split('.')for mail_end in _mailEnds]
        
        df_['raw_country'] = [item_lst[-1] for item_lst in _split_mailsEnds]
        df_['raw_institute'] = [''.join(item_lst[0:-1]) for item_lst in _split_mailsEnds]

    if 'institute' in df.columns:
        df_['raw_institute'] = df['institute']

    df_['identifier'] = [uuid.uuid4() for _ in range(len(df_))]
    
    return df_


def write_to_csv(df, filepath: pathlib.PosixPath) -> None:

    """
    Writes dataframe to csv file
    """

    df.to_csv(filepath, index=False)


# CODE
PROJECTPATH = Path.cwd()
FOLDERPATH = PROJECTPATH / 'data' / '_LWUA_DataSystems_RawInput'
FILEPATHS = [x for x in FOLDERPATH.iterdir() if x.is_file()]

for filepath in FILEPATHS:
    new_filename = filepath.stem + '_abstract.csv'
    new_filepath = PROJECTPATH / 'data' / new_filename

    df = read_input(filepath)
    df_ = annonymize_input(df)
    write_to_csv(df_, new_filepath)
