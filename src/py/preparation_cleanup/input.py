## Helper functions to read raw input files & transform to format that can be made public
import pandas as pd
import openpyxl
from itertools import islice
from pathlib import PosixPath
import uuid

## Functions
def read(filepath: PosixPath) -> pd.DataFrame:
    
    """
    Reads given filepath & loads data into a Dataframe
    Returns dataframe with filepath name added to 'source' column
    """

    if filepath.suffix == ".csv":
        df = pd.read_csv(filepath, delimiter=";")

    if filepath.suffix == ".txt":
        df = pd.read_csv(filepath, delimiter="\t")

    if filepath.suffix == ".xlsx" or filepath.suffix == ".xls":
        wb = openpyxl.load_workbook(filepath)
        ws = wb.active
        data = ws.values
        cols = next(data)[1:]
        data = list(data)
        idx = [r[0] for r in data]
        data = (islice(r, 1, None) for r in data)
        df = pd.DataFrame(data, index=idx, columns=cols)

    df["source"] = filepath.stem

    return df


def annonymize(df: pd.DataFrame) -> pd.DataFrame:

    """
    Returns DataFrame with personal information removed
    """

    df.columns = df.columns.str.lower()

    _df = pd.DataFrame()
    _df["source"] = df["source"]
    
    if "email" in df.columns:  
        mailEnds = [str(email).split("@")[-1] if email is not None else "NA" for email in df["email"]]
        split_mailsEnds = [mail_end.split(".") if mail_end is not None else "NA" for mail_end in mailEnds]

        _df["email_domain_end"] = [item_lst[-1] for item_lst in split_mailsEnds]
        _df["email_domain_name"] = ["".join(item_lst[0:-1]) for item_lst in split_mailsEnds]

    if "institute" in df.columns:
        _df["raw_institute"] = df["institute"]

    if "organisation" in df.columns:
        _df["raw_institute"] = df["organisation"]

    if "affiliation" in df.columns:
        _df["raw_institute"] = df["affiliation"]

    _df["user_identifier"] = [f"{row['source']}_{uuid.uuid4()}" for i, row in df.iterrows()]

    return _df