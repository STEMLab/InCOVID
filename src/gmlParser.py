import xml.etree.ElementTree as ET
import matplotlib.path as mplPath
import numpy as np

floorsAndValues = {}
highAndLowX = []
highAndLowY = []
highAndLowZ = []
floors = []
GMLOBJ_3D_forFloors = []
GMLOBJ_3D_Objects = []
gmlObjectsDoors_3D = []
gmlObjectsStairs_3D = []
gmlObjectsElevators_3D = []
gmlObjectsTransitions_3D = []
dictRooms = {}


class GMLOBJ_3D_FORFLOORS:
    def __init__(self):
        # current position
        self.id = 0
        self.floor = []

# GMLOBJ_3D_OBJECTS class
class GMLOBJ_3D_OBJECTS:
    def __init__(self):
        # current position
        self.id = 0
        self.sideNumber = 0
        self.xyz = []
        self.allPos = []
        self.onlyZ = []
        self.locationVal = []
        self.floor = []
        self.numCases = 0
        self.poly = 0
        self.poly_path = []

# GMLOBJ_DOORS_3D class
class GMLOBJ_DOORS_3D:
    def __init__(self):
        # current position
        self.sideNumber = 0
        self.allPos = []
        self.floor = 0

# GMLOBJ_STAIR_3D class
class GMLOBJ_STAIR_3D:
    def __init__(self):
        # current position
        self.sideNumber = 0
        self.allPos = []

# GMLOBJ_ELEVATOR_3D class
class GMLOBJ_ELEVATOR_3D:
    def __init__(self):
        # current position
        self.sideNumber = 0
        self.allPos = []

# GMLOBJ_TRANSITION CLASS
class GMLOBJ_TRANSITION:
    def __init__(self):
        # current position
        self.sideNumber = 0
        self.allPos = []

####################################  PARSING GML #####################################
# parsing function
def myGML_3D(gmlFileName):
    tree = ET.parse(gmlFileName)
    root = tree.getroot()

    # for finding the lowest and hightest value
    for envelope in root.findall(
            './/{http://www.opengis.net/gml/3.2}Polygon/{http://www.opengis.net/gml/3.2}exterior/{http://www.opengis.net/gml/3.2}LinearRing'):
        for ival,i in enumerate(list(envelope)):
            myTemp = [float(x) for x in i.text.split(' ')]
            highAndLowX.append(myTemp[0])
            highAndLowY.append(myTemp[1])
            highAndLowZ.append(myTemp[2])

    zHighLow = []

    # for finding floors
    for envelope in root.findall(
                './/{http://www.opengis.net/indoorgml/1.0/core}Geometry3D'):
            tempObject = GMLOBJ_3D_FORFLOORS()
            for a in envelope.findall('{http://www.opengis.net/gml/3.2}Solid'):
              key = a.attrib
              tempObject.id = key.get('{http://www.opengis.net/gml/3.2}id')
              for b in a.findall(
                        '{http://www.opengis.net/gml/3.2}exterior/{http://www.opengis.net/gml/3.2}Shell'):
                for c in b.findall(
                          '{http://www.opengis.net/gml/3.2}surfaceMember/{http://www.opengis.net/gml/3.2}Polygon/{http://www.opengis.net/gml/3.2}exterior/{http://www.opengis.net/gml/3.2}LinearRing'):
                    for i in list(c):
                        myTemp = [float(x) for x in i.text.strip().split(' ')]
                        x = np.float64(myTemp[0])
                        y = np.float64(myTemp[1])
                        z = np.float64(myTemp[2])
                        zHighLow.append(z)
                tempObject.floor = (min(zHighLow),max(zHighLow))
                zHighLow = []
            GMLOBJ_3D_forFloors.append(tempObject)

    new_list = [x.floor for x in GMLOBJ_3D_forFloors]
    res = list(set(new_list))
    sortedRes = sorted(res, key=lambda tuple: tuple[1])
    temp = [abs(abs(b) - abs(a)) for a, b in sortedRes]
    maxDiff = max(temp)
    newListFloors =[]
    for i in range(len(sortedRes)):
            newListFloors.append(sortedRes[i])
    index = 0
    for i in range(len(newListFloors)):
            if min(newListFloors[i])==0:
                index = i
    for i in range(len(newListFloors)):
            if min(newListFloors[i])>=0:
                floorsAndValues[i-index+1] = newListFloors[i]
            else:
                diff = int(max(newListFloors[i])*2/maxDiff)
                floorsAndValues[diff-1] = newListFloors[i]

    # OBJECTS
    for envelope in root.findall(
                './/{http://www.opengis.net/indoorgml/1.0/core}Geometry3D'):
            tempObject = GMLOBJ_3D_OBJECTS()
            for a in envelope.findall('{http://www.opengis.net/gml/3.2}Solid'):
              key = a.attrib
              tempObject.id = key.get('{http://www.opengis.net/gml/3.2}id')
              thisCoords = []
              newCoords = []
              eachSide=[]
              for b in a.findall(
                        '{http://www.opengis.net/gml/3.2}exterior/{http://www.opengis.net/gml/3.2}Shell'):
                numTimes = 0
                for c in b.findall(
                          '{http://www.opengis.net/gml/3.2}surfaceMember/{http://www.opengis.net/gml/3.2}Polygon/{http://www.opengis.net/gml/3.2}exterior/{http://www.opengis.net/gml/3.2}LinearRing'):
                    for i in list(c):
                        myTemp = [float(x) for x in i.text.strip().split(' ')]
                        x = np.float64(myTemp[0])
                        y = np.float64(myTemp[1])
                        z = np.float64(myTemp[2])
                        myTemp = [x, y, z]
                        thisTemp = (x, y)
                        newTemp = [x,y]
                        thisCoords.append(thisTemp)
                        tempObject.allPos.append(myTemp)
                        newCoords.append(newTemp)
                        zHighLow.append(z)
                        eachSide.append(myTemp)
                    numTimes += 1
                    tempObject.xyz.append(eachSide)
                    eachSide = []
                for k, v in floorsAndValues.items():
                    if max(zHighLow) <= max(v) and min(zHighLow) >= min(v):
                        tempObject.floor = k
                tempObject.sideNumber = int(numTimes)
                tempObject.poly_path = mplPath.Path(np.array(newCoords))
                newCoords = []
                thisCoords = []
                zHighLow = []
            GMLOBJ_3D_Objects.append(tempObject)

    # old indoorGML standard
    # for door and elevator
    for envelope in root.findall(
            './/{http://www.opengis.net/indoorgml/1.0/core}CellSpaceBoundary'):
        key = envelope.attrib
        tempName = key.get('{http://www.opengis.net/gml/3.2}id')
        if "B" in tempName:
            for b in envelope.findall('{http://www.opengis.net/indoorgml/1.0/core}geometry3D/{http://www.opengis.net/gml/3.2}Polygon/{http://www.opengis.net/gml/3.2}exterior/{http://www.opengis.net/gml/3.2}LinearRing'):
                    numTimes = 0
                    tempObject = GMLOBJ_DOORS_3D()
                    for ival,i in enumerate(list(b)):
                        numTimes += 1
                        myTemp = [float(x) for x in i.text.split(' ')]
                        myTemp = [myTemp[0], myTemp[1], myTemp[2]]
                        zHighLow.append(myTemp[2])
                        tempObject.allPos.append(myTemp)
                    for k, v in floorsAndValues.items():
                        if max(zHighLow) <= max(v) and min(zHighLow) >= min(v):
                            tempObject.floor = k
                    tempObject.sideNumber = int(numTimes)
                    gmlObjectsDoors_3D.append(tempObject)
                    zHighLow = []
        if "Elevator" in tempName:
            for b in envelope.findall('{http://www.opengis.net/gml/3.2}exterior/{http://www.opengis.net/gml/3.2}LinearRing'):
                    numTimes = 0
                    tempObject = GMLOBJ_ELEVATOR_3D()
                    for ival,i in enumerate(list(b)):
                        numTimes += 1
                        myTemp = [float(x) for x in i.text.split(' ')]
                        myTemp = [myTemp[0], myTemp[1], myTemp[2]]
                        tempObject.allPos.append(myTemp)
                    tempObject.sideNumber = int(numTimes)
                    gmlObjectsElevators_3D.append(tempObject)

    #new indoorGML standard
    if(len(gmlObjectsDoors_3D)==0):
        # for door and elevator
        for envelope in root.findall(
                './/{http://www.opengis.net/indoorgml/1.0/core}geometry3D/{http://www.opengis.net/gml/3.2}Polygon'):
            key = envelope.attrib
            tempName = key.get('{http://www.opengis.net/gml/3.2}id')
            if "B" in tempName:
                for b in envelope.findall(
                        '{http://www.opengis.net/gml/3.2}exterior/{http://www.opengis.net/gml/3.2}LinearRing'):
                    numTimes = 0
                    tempObject = GMLOBJ_DOORS_3D()
                    for ival, i in enumerate(list(b)):
                        numTimes += 1
                        myTemp = [float(x) for x in i.text.split(' ')]
                        myTemp = [myTemp[0], myTemp[1], myTemp[2]]
                        zHighLow.append(myTemp[2])
                        tempObject.allPos.append(myTemp)
                    for k, v in floorsAndValues.items():
                        if max(zHighLow) <= max(v) and min(zHighLow) >= min(v):
                            tempObject.floor = k
                    tempObject.sideNumber = int(numTimes)
                    gmlObjectsDoors_3D.append(tempObject)
                    zHighLow = []
            if "Elevator" in tempName:
                for b in envelope.findall(
                        '{http://www.opengis.net/gml/3.2}exterior/{http://www.opengis.net/gml/3.2}LinearRing'):
                    numTimes = 0
                    tempObject = GMLOBJ_ELEVATOR_3D()
                    for ival, i in enumerate(b.getchildren()):
                        numTimes += 1
                        myTemp = [float(x) for x in i.text.split(' ')]
                        myTemp = [myTemp[0], myTemp[1], myTemp[2]]
                        tempObject.allPos.append(myTemp)
                    tempObject.sideNumber = int(numTimes)
                    gmlObjectsElevators_3D.append(tempObject)

    # for transition
    for envelope in root.findall(
            './/{http://www.opengis.net/indoorgml/1.0/core}Transition/{http://www.opengis.net/indoorgml/1.0/core}geometry/{http://www.opengis.net/gml/3.2}LineString'):
        numTimes = 0
        tempObject = GMLOBJ_TRANSITION()
        for ival,i in enumerate(list(envelope)):
            numTimes += 1
            myTemp = [float(x) for x in i.text.split(' ')]
            myTemp = [myTemp[0], myTemp[1], myTemp[2]]
            tempObject.allPos.append(myTemp)
        tempObject.sideNumber = int(numTimes)
        gmlObjectsTransitions_3D.append(tempObject)

    global dictRooms

    for floorT in range(len(newListFloors) + 1):
        newList = []
        for i, myobject in enumerate(GMLOBJ_3D_Objects):
            if floorT == myobject.floor:
                newList.append(myobject)
                dictRooms[floorT] = newList

