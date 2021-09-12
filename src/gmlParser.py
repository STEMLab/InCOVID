import xml.etree.ElementTree as ET
from tkinter import *
import numpy as np
from shapely.geometry import Polygon


floorsAndValues = {}
highAndLowX = []
highAndLowY = []
highAndLowZ = []
# defining arrays of object
floors = []
GMLOBJ_3D_forFloors = []
GMLOBJ_3D_Objects = []
gmlObjectsDoors_3D = []
gmlObjectsStairs_3D = []
gmlObjectsElevators_3D = []
gmlFloors_3D = []
gmlObjectsTransitions_3D = []


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
    object_id = 0

    # for finding the lowest and hightest value
    for envelope in root.findall(
            './/{http://www.opengis.net/gml/3.2}Polygon/{http://www.opengis.net/gml/3.2}exterior/{http://www.opengis.net/gml/3.2}LinearRing'):
        for ival,i in enumerate(envelope.getchildren()):
            myTemp = [float(x) for x in i.text.split(' ')]
            highAndLowX.append(myTemp[0])
            highAndLowY.append(myTemp[1])
            highAndLowZ.append(myTemp[2])

    zHighLow = []

    # for finding floors
    for envelope in root.findall(
                './/{http://www.opengis.net/indoorgml/1.0/core}cellSpaceGeometry/{http://www.opengis.net/indoorgml/1.0/core}Geometry3D'):
            tempObject = GMLOBJ_3D_FORFLOORS()
            for a in envelope.findall('{http://www.opengis.net/gml/3.2}Solid'):
              key = a.attrib
              tempObject.id = key.get('{http://www.opengis.net/gml/3.2}id')
              for b in a.findall(
                        '{http://www.opengis.net/gml/3.2}exterior/{http://www.opengis.net/gml/3.2}Shell'):
                for c in b.findall(
                          '{http://www.opengis.net/gml/3.2}surfaceMember/{http://www.opengis.net/gml/3.2}Polygon/{http://www.opengis.net/gml/3.2}exterior/{http://www.opengis.net/gml/3.2}LinearRing'):
                    for i in c.getchildren():
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
    for i in range(len(sortedRes)):
        floorsAndValues[i + 1] = sortedRes[i]

    # OBJECTS
    for envelope in root.findall(
                './/{http://www.opengis.net/indoorgml/1.0/core}cellSpaceGeometry/{http://www.opengis.net/indoorgml/1.0/core}Geometry3D'):
            tempObject = GMLOBJ_3D_OBJECTS()

            for a in envelope.findall('{http://www.opengis.net/gml/3.2}Solid'):
              key = a.attrib
              tempObject.id = key.get('{http://www.opengis.net/gml/3.2}id')
              thisCoords = []
              for b in a.findall(
                        '{http://www.opengis.net/gml/3.2}exterior/{http://www.opengis.net/gml/3.2}Shell'):
                numTimes = 0
                for c in b.findall(
                          '{http://www.opengis.net/gml/3.2}surfaceMember/{http://www.opengis.net/gml/3.2}Polygon/{http://www.opengis.net/gml/3.2}exterior/{http://www.opengis.net/gml/3.2}LinearRing'):
                    for i in c.getchildren():
                        myTemp = [float(x) for x in i.text.strip().split(' ')]
                        x = np.float64(myTemp[0])
                        y = np.float64(myTemp[1])
                        z = np.float64(myTemp[2])
                        myTemp = [x, y, z]
                        thisTemp = (x, y)
                        thisCoords.append(thisTemp)
                        tempObject.allPos.append(myTemp)
                        zHighLow.append(z)
                    numTimes += 1
                for k, v in floorsAndValues.items():
                    if max(zHighLow) <= max(v) and min(zHighLow) >= min(v):
                        tempObject.floor = k

                tempObject.sideNumber = int(numTimes)
                tempObject.poly = Polygon(thisCoords)
                thisCoords = []
                zHighLow = []
            GMLOBJ_3D_Objects.append(tempObject)


    # getting floors
    for test in root.findall(
            './/{http://www.opengis.net/indoorgml/1.0/core}cellSpaceBoundaryMember/{http://www.opengis.net/indoorgml/1.0/core}CellSpaceBoundary/{http://www.opengis.net/gml/3.2}description'):
        temp = re.findall(r'[A-Za-z]+|\d+', str(test.text))
        newList = [i for i in temp if i.isdigit()]
        if (temp[0] != 'None'):
            intVar = int(re.search(r'\d+', str(newList[0])).group())
            floors.append(intVar)
    floorsUpdated = []
    for i,x in enumerate(floors):
        if x not in floorsUpdated:
            floorsUpdated.append(x)

    # for door and elevator
    for envelope in root.findall(
            './/{http://www.opengis.net/indoorgml/1.0/core}geometry3D/{http://www.opengis.net/gml/3.2}Polygon'):
        key = envelope.attrib
        tempName = key.get('{http://www.opengis.net/gml/3.2}id')
        if "B" in tempName:
            for b in envelope.findall('{http://www.opengis.net/gml/3.2}exterior/{http://www.opengis.net/gml/3.2}LinearRing'):
                    numTimes = 0
                    tempObject = GMLOBJ_DOORS_3D()
                    for ival,i in enumerate(b.getchildren()):
                        numTimes += 1
                        myTemp = [float(x) for x in i.text.split(' ')]
                        myTemp = [myTemp[0], myTemp[1], myTemp[2]]
                        zHighLow.append(myTemp[2])
                        tempObject.allPos.append(myTemp)
                    for k, v in floorsAndValues.items():
                        if max(zHighLow) <= (max(v)/2) and min(zHighLow) >= min(v):
                            tempObject.floor = k
                            print("this is in the floor of door:")
                            print(k)
                    tempObject.sideNumber = int(numTimes)
                    gmlObjectsDoors_3D.append(tempObject)
                    zHighLow = []
        if "Elevator" in tempName:
            for b in envelope.findall('{http://www.opengis.net/gml/3.2}exterior/{http://www.opengis.net/gml/3.2}LinearRing'):
                    numTimes = 0
                    tempObject = GMLOBJ_ELEVATOR_3D()
                    for ival,i in enumerate(b.getchildren()):
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
        for ival,i in enumerate(envelope.getchildren()):
            numTimes += 1
            myTemp = [float(x) for x in i.text.split(' ')]
            myTemp = [myTemp[0], myTemp[1], myTemp[2]]
            tempObject.allPos.append(myTemp)
        tempObject.sideNumber = int(numTimes)
        gmlObjectsTransitions_3D.append(tempObject)
        object_id += 1