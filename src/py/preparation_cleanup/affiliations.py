# Helper functions to standardize affiliation names in DataFrame
import pandas as pd
from collections import defaultdict

## Functions
def make_mapping_dict(affil_mapping: pd.DataFrame) -> dict:
    
    """
    Turns the reference mapping file into a dictionary with structure:
        { stand-affiliation-name : [list of possible ways to write the affiliation name] }
    """

    mapping_dct = defaultdict(list)
    for i in affil_mapping.index:
        if affil_mapping["Institute_standardized"][i] not in mapping_dct.keys():
            mapping_dct[affil_mapping["Institute_standardized"][i]] = [
                str(affil_mapping["Institute"][i]).lower().strip()
            ]
        else:
            mapping_dct[affil_mapping["Institute_standardized"][i]].append(
                str(affil_mapping["Institute"][i]).lower().strip()
            )

    return mapping_dct


def standardize_affiliation_names(df: pd.DataFrame, mapping_dct: dict) -> pd.DataFrame:
    
    """
    Adds standardized insitute names to df using the given mapping dict

    Returns 2 DataFrames:
        - original DataFrame with standard institute names added in a new column
        - new DataFrame with institute names for which no standard affiliation name was found 
          (and hence still have to be standardized)
    """

    # add standard affiliation names:
    df["stand_institute"] = ""
    for index, row in df.iterrows():
        for stand_inst, inst_list in mapping_dct.items():
            if "email_domain_name" in df.columns:
                if (row["email_domain_name"] in inst_list or str(row["email_domain_name"]).lower().strip() in inst_list):
                    df.at[index, "stand_institute"] = stand_inst
            if "raw_institute" in df.columns:
                if (row["raw_institute"] in inst_list or str(row["raw_institute"]).lower().strip() in inst_list):
                    df.at[index, "stand_institute"] = stand_inst

    # identify affiliations for which no standard affiliation was found:
    df_tostand = df.loc[df["stand_institute"] == ""]
    df_tostand = df_tostand.drop_duplicates()

    return df, df_tostand


def add_info(df: pd.DataFrame, affil_info: pd.DataFrame) -> pd.DataFrame:
    
    """
    Add information linked to standardized affiliation name
    """

    # because NaN is of type Int64 and can't merge between different types
    df["stand_institute"] = df["stand_institute"].fillna("")
    merged_df = pd.merge(df, affil_info, on="stand_institute", how="left", suffixes=("_", "_info"))
    
    return merged_df