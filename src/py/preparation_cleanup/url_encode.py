import pycountry
import pandas as pd
import urllib.parse

file_path = "data/reference_data/AffiliationInfo.csv"
df = pd.read_csv(file_path)

for i in df.index:
    cntry_url = df.loc[i, 'country_url']
    df.loc[i,'country_url'] = urllib.parse.quote(cntry_url)

df.to_csv("data/reference_data/AffiliationInfo.csv")