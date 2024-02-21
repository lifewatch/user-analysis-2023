import uuid
import pandas as pd

file_path = "data/reference_data/AffiliationInfo.csv"

df = pd.read_csv(file_path)
df["local_ID"] = [uuid.uuid4() for _ in range(len(df))]
df.to_csv("data/reference_data/AffiliationInfo.csv")