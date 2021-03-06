import xml.etree.ElementTree as ET
from tkinter import *
import numpy as np
from shapely.geometry import Polygon

highAndLowX = []
highAndLowY = []
highAndLowZ = []

# GMLOBJ_3D class
class GMLOBJ_3D:
    def __init__(self, objectID):
        # current position
        self.objectID = objectID
        self.sideNumber = 0
        self.allPos = []
        self.floor = 0
        self.points = []
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

# defining arrays of object
gmlObjects_MIN_MAX_3D = []
gmlObjects_3D = []
gmlObjectsDoors_3D = []
gmlObjectsStairs_3D = []
gmlObjectsElevators_3D = []
gmlObjectsTransitions_3D = []
gmlFloors_3D = []

####################################  PARSING GML #####################################
# parsing function
def myGML_3D(gmlFileName):
    tree = ET.parse(gmlFileName)
    root = tree.getroot()
    object_id = 0

    # for finding the lowest and hightest value
    for envelope in root.findall(
            './/{http://www.opengis.net/gml/3.2}Polygon/{http://www.opengis.net/gml/3.2}exterior/{http://www.opengis.net/gml/3.2}LinearRing'):
        numTimes = 0
        for ival,i in enumerate(envelope.getchildren()):
            myTemp = [float(x) for x in i.text.split(' ')]
            highAndLowX.append(myTemp[0])
            highAndLowY.append(myTemp[1])
            highAndLowZ.append(myTemp[2])


    thisCoords =[]

    # for rooms and corridors
    for envelope in root.findall(
            './/{http://www.opengis.net/gml/3.2}Polygon/{http://www.opengis.net/gml/3.2}exterior/{http://www.opengis.net/gml/3.2}LinearRing'):
        numTimes = 0
        tempObject = GMLOBJ_3D(object_id)
        for i in envelope.getchildren():
            numTimes += 1
            myTemp = [float(x) for x in i.text.split(' ')]
            if myTemp[2] == 0:
                tempObject.floor = 1
            if myTemp[2] == 20:
                tempObject.floor = 2
            if myTemp[2] == 40:
                tempObject.floor = 3
            if myTemp[2] == 60:
                tempObject.floor = 4
            if myTemp[2] == 80:
                tempObject.floor = 5
            x = np.float64(myTemp[0])
            y = np.float64(myTemp[1])
            z = np.float64(myTemp[2])
            myTemp = [x,y,z]
            thisTemp = (x,y)
            thisCoords.append(thisTemp)
            tempObject.allPos.append(myTemp)
        tempObject.sideNumber = int(numTimes)
        tempObject.points = np.vstack(tempObject.allPos)
        tempObject.poly = Polygon(thisCoords)
        gmlObjects_3D.append(tempObject)
        object_id += 1
        thisCoords = []

    floors = []
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
                        if myTemp[2] == 0 and myTemp[2] <= 15:
                            tempObject.floor = 1
                        if myTemp[2] >= 20 and myTemp[2] <= 35:
                            tempObject.floor = 2
                        if myTemp[2] >= 40 and myTemp[2] <= 55:
                            tempObject.floor = 3
                        if myTemp[2] >= 60 and myTemp[2] <= 75:
                            tempObject.floor = 4
                        if myTemp[2] >= 80 and myTemp[2] <= 95:
                            tempObject.floor = 5
                        myTemp = [myTemp[0], myTemp[1], myTemp[2]]
                        tempObject.allPos.append(myTemp)
                    tempObject.sideNumber = int(numTimes)
                    gmlObjectsDoors_3D.append(tempObject)
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

    return floorsUpdated




