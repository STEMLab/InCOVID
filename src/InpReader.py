import pandas as pd
idWithCoord = []

def getData(fileName):
    chunk = pd.read_csv(fileName, header=1, usecols = ['@mfidref','startTime','endTime','startCoord','endCoord','typecode'],dtype={'@mfidref': str,'startTime': str,'endTime': str,'startCoord':str,'endCoord':str,'typecode':str}, chunksize=100000)
    df = pd.concat(chunk)
    print(df)
    uniqueids = df['@mfidref'].unique()
    print(len(uniqueids))
    df_list = [d for _, d in df.groupby(['@mfidref'])]

    # pd.strptime(df['startTime'].values, "%Y-%m-%dT%H:%M:%SZ")
    # pd.strptime(df['endTime'].values, "%Y-%m-%dT%H:%M:%SZ")
    df['startTime'] = pd.to_datetime(df['startTime'],format="%Y-%m-%dT%H:%M:%SZ")
    startTimeThis = df['startTime'].min()
    timeS = startTimeThis.to_pydatetime()
    df['endTime'] = pd.to_datetime(df['endTime'],format="%Y-%m-%dT%H:%M:%SZ")
    endTimeThis = df['endTime'].max()
    timeF = endTimeThis.to_pydatetime()
    diff = (timeF-timeS).seconds


    return df_list, timeS, timeF, diff

