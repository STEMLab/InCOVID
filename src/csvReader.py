# import necessary modules
import csv

idsOfHuman = []
idWithCoord = []
id_arr = []

def gettingData(fileName):
    with open(fileName, 'rt')as R:
        myData = csv.reader(R)
        for row_num, row in enumerate(myData):
            if row_num <= 1:
                pass
            else:
                idsOfHuman.append(row[0])
                temp = [float(x) for i,x in enumerate(row[3].split(' '))]
                temp = [row[0], temp[0], temp[1], temp[2],row[1],row[2]]
                idWithCoord.append(temp)
                temp2 = [float(x) for i,x in enumerate(row[4].split(' '))]
                temp2 = [row[0], temp2[0], temp2[1], temp2[2],row[1],row[2]]
                idWithCoord.append(temp2)
    setting = set()
    for i,item in enumerate(idsOfHuman):
        if item not in setting:
            setting.add(item)
            id_arr.append(item)
