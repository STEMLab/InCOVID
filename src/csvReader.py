import pandas as pd

idWithCoord = []

def gettingData(fileName):
    tp = pd.read_csv(fileName, iterator=True, chunksize=1000, header=1)
    df = pd.concat(tp, ignore_index=True)
    df['startTime'] = pd.to_datetime(df['startTime'],utc=True)
    startTimeThis = df['startTime'].min()
    timeS = startTimeThis.to_pydatetime()
    df['endTime'] = pd.to_datetime(df['endTime'],utc=True)
    endTimeThis = df['endTime'].max()
    timeF = endTimeThis.to_pydatetime()
    increasetime = (timeF-timeS).seconds
    uniqueids = df['@mfidref'].unique()
    id_arr = uniqueids.tolist()
    listOfObjects = []
    for i in uniqueids:
        tempObj = df[df['@mfidref'] == i]
        listOfObjects.append(tempObj)
        l_2d = tempObj.values.tolist()
        for k in range(len(l_2d)):
            temp = [float(x) for i, x in enumerate(l_2d[k][3].split(' '))]
            temp = [l_2d[k][0], temp[0], temp[1], temp[2], l_2d[k][1], l_2d[k][2]]
            idWithCoord.append(temp)
            temp2 = [float(x) for i, x in enumerate(l_2d[k][4].split(' '))]
            temp2 = [l_2d[k][0], temp2[0], temp2[1], temp2[2], l_2d[k][1], l_2d[k][2]]
            idWithCoord.append(temp2)
    return id_arr, timeS, timeF, increasetime
