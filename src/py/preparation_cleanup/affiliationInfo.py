import pandas as pd
import uuid
import urllib.parse
import pycountry
import requests

url = 'https://api.ror.org/organizations'

def add_ror(df: pd.DataFrame) -> pd.DataFrame: 
    df_matches = pd.DataFrame(columns=['res_status_code', 'affil_OG','substring', 'score', 'chosen', 'organization_id', 'organization_name'])
    for i in df.index:
        affil = df.loc[i, 'stand_institute']
        print(affil)
        # Define any parameters or data you need to send with the request
        params = {'affiliation': urllib.parse.quote(affil)}
        response = requests.get(url, params=params)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            
            for item in response.json()['items']:
                df_matches = pd.concat([df_matches, pd.DataFrame(
                    [{
                    'res_status_code': response.status_code, 
                    'affil_OG': affil, 
                    'substring': item['substring'], 
                    'score': item['score'],
                    'chosen': item['chosen'],
                    'organization_id': item['organization']['id'],
                    'organization_name': item['organization']['name']
                    }]
                )], ignore_index=True)
        else:
            # Print an error message if the request was not successful
            df_matches = pd.concat([df_matches, pd.DataFrame(
                    [{
                    'res_status_code': response.status_code, 
                    'affil_OG': affil, 
                    'substring': '', 
                    'score': '',
                    'chosen': '',
                    'organization_id': '',
                    'organization_name': ''
                    }]
                )], ignore_index=True)

    return df_matches


def add_country(df: pd.DataFrame) -> pd.DataFrame:
    for i in df.index:
        cntry = df.loc[i, 'country']
        try:
            country_stand = pycountry.countries.get(name=cntry)
            print(country_stand.alpha_2)
            df.loc[i, 'country_alpha2'] = country_stand.alpha_2
            df.loc[i, 'country_alpha3'] = country_stand.alpha_3
            df.loc[i, 'country_official_name'] = country_stand.official_name
            country_url = "https://www.iso.org/obp/ui/#iso:code:3166:" + country_stand.alpha_2
            df.loc[i, 'country_url'] = urllib.parse.quote(country_url)

            
        except:
            print(cntry)
            df.loc[i, 'country_alpha2'] = ''
            df.loc[i, 'country_alpha3'] = ''
            df.loc[i, 'country_official_name'] = ''
            if cntry == "European Union":
                df.loc[i, 'country_url'] = urllib.parse.quote("https://www.iso.org/obp/ui/#iso:code:3166:EU")
            if cntry == "Global" or cntry == "personal":
                df.loc[i, 'country_url'] = urllib.parse.quote("https://www.iso.org/obp/ui/#iso:code:3166:XAA")

    return df


file_path = "data/reference_data/AffiliationInfo.csv"
df = pd.read_csv(file_path)

#1. add identifier information
df["local_ID"] = [uuid.uuid4() for _ in range(len(df))]
df.to_csv("data/reference_data/AffiliationInfo.csv")

#2. add country information 
df_country = add_country(df)
df_country.to_csv("data/reference_data/AffiliationInfo_country.csv")

#3. add ROR information
df_matches = add_ror(df_country)
df_matches.to_csv("data/reference_data/ROR_IDs.csv", index=False)