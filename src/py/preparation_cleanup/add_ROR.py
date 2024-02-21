import requests
import pandas as pd
import urllib.parse
import json

url = 'https://api.ror.org/organizations'


file_path = "data/reference_data/AffiliationInfo.csv"
df = pd.read_csv(file_path)

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

df_matches.to_csv("data/reference_data/ROR_IDs.csv", index=False)