import pandas as pd
from os import listdir
from os.path import isfile, join
from Crawler import createDataFrame

files = [f for f in listdir("Data") if isfile(join('Data', f))]

df = createDataFrame()
for file in files:
    df_partial = pd.read_csv('Data\\'+ file)
    df = df.append(df_partial)

# drop rows with same product and same pairing
df.drop_duplicates(keep='first', inplace=True)

df.to_csv('DatasetIT.csv', index=False)
