import pandas as pd
import time
idWithCoord = []

def getData(fileName):
    chunk = pd.read_csv(fileName, header=1, usecols = ['@mfidref','startTime','endTime','startCoord','endCoord','typecode'],dtype={'@mfidref': str,'startTime': str,'endTime': str,'startCoord':str,'endCoord':str,'typecode':str}, chunksize=100000)
    df = pd.concat(chunk)
    print(df)
    uniqueids = df['@mfidref'].unique()
    print(len(uniqueids))
    df_list = [d for _, d in df.groupby(['@mfidref'])]
    return df_list

