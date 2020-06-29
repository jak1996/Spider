import pandas as pd
from os import listdir
from os.path import isfile, join
from Crawler import createDataFrame
import numpy as np

files = [f for f in listdir("Data") if isfile(join('Data', f))]

df = createDataFrame()
for file in files:
    print(file)
    df_partial = pd.read_csv('Data\\'+ file, error_bad_lines=False)
    df = df.append(df_partial)

print(len(df.index))

# drop rows with same product and same pairing
df.drop_duplicates(keep='first', inplace=True)
print(len(df.index))
# df = df.drop(df.columns[-1], axis=1)
df['indexes'] = np.arange(len(df.index))
df.set_index(['indexes'], inplace=True)
print(list(df.index))


# remove rows with a pairing product that is not present in the dataset
IDs = df['ID'].unique()
counter = 0
for index, row in df.iterrows():
    for i in range(1, 5):
        if row['ID pairing ' + str(i)] not in IDs and row['ID pairing ' + str(i)] != 'Null':
            counter += 1
    if counter == 4:
        df.drop(index, inplace=True, axis=0)
    counter = 0

print(len(df.index))
df.to_csv('Dataset.csv', index=False)
