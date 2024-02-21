import pycountry
import pandas as pd

file_path = "data/reference_data/AffiliationInfo.csv"


df = pd.read_csv(file_path)

for i in df.index:
    cntry = df.loc[i, 'country']
    try:
        country_stand = pycountry.countries.get(name=cntry)
        print(country_stand.alpha_2)
        df.loc[i, 'country_alpha2'] = country_stand.alpha_2
        df.loc[i, 'country_alpha3'] = country_stand.alpha_3
        df.loc[i, 'country_official_name'] = country_stand.official_name
        df.loc[i, 'country_url'] = "https://www.iso.org/obp/ui/#iso:code:3166:" + country_stand.alpha_2

        
    except:
        print(cntry)
        df.loc[i, 'country_alpha2'] = ''
        df.loc[i, 'country_alpha3'] = ''
        df.loc[i, 'country_official_name'] = ''
        if cntry == "European Union":
            df.loc[i, 'country_url'] = "https://www.iso.org/obp/ui/#iso:code:3166:EU"
        if cntry == "Global" or cntry == "personal":
            df.loc[i, 'country_url'] = "https://www.iso.org/obp/ui/#iso:code:3166:XAA"

df.to_csv("data/reference_data/AffiliationInfo_country.csv")