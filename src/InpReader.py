import pandas as pd
import time
idWithCoord = []

def getData(fileName):
    tp = pd.read_csv(fileName, iterator=True, chunksize=1000000, header=1)
    df = pd.concat(tp, ignore_index=True)
    df['startTime'] = pd.to_datetime(df['startTime'],utc=True)
    startTimeThis = df['startTime'].min()
    timeS = startTimeThis.to_pydatetime()
    df['endTime'] = pd.to_datetime(df['endTime'],utc=True)
    endTimeThis = df['endTime'].max()
    timeF = endTimeThis.to_pydatetime()
    diffTime = (timeF-timeS).seconds
    uniqueids = df['@mfidref'].unique()
    id_arr = uniqueids.tolist()
    print(id_arr)
    df_list = [d for _, d in df.groupby(['@mfidref'])]



    return diffTime, df_list


