# import necessary modules
import csv

idsOfHuman = []
startTime = []
endTime = []
startCoord = []
endTimeCoord = []
allCoord = []
line = []
myLine = []

def gettingData(fileName):
    with open(fileName, 'rt')as R:
        myData = csv.reader(R)
        for row_num, row in enumerate(myData):
            if row_num <= 1:
                pass
            else:
                idsOfHuman.append(row[0])
                startTime.append(row[1])
                endTime.append(row[2])
                startCoord.append(row[3])
                endTimeCoord.append(row[4])
                allCoord.append(row[3])
                allCoord.append(row[4])
                line.append(row)
                temp = [float(x) for x in row[3].split(' ')]
                temp = [row[0], temp[0], temp[1], temp[2],row[1],row[2]]
                myLine.append(temp)
                temp2 = [float(x) for x in row[4].split(' ')]
                temp2 = [row[0], temp2[0], temp2[1], temp2[2],row[1],row[2]]
                myLine.append(temp2)
    setting = set()
    id_arr = []
    for item in idsOfHuman:
        if item not in setting:
            setting.add(item)
            id_arr.append(item)
    floatsCoord = []
    for i in range(0, len(allCoord)):
        temp = [float(x) for x in allCoord[i].split(' ')]
        temp = [temp[0], temp[1]]
        floatsCoord.append(temp)
    return floatsCoord, myLine, id_arr
