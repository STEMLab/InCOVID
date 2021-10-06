# Person class
from src.gmlParser import floorsAndValues, GMLOBJ_3D_Objects
import numpy as np
import random

class MovingObject:
    def __init__(self,id,typeMO):
        self.id = id
        #employee = 1 and client = 2
        self.type = typeMO
        self.startTime = 0
        self.endTime = 0
        self.path = []
        self.iterator = 0
        self.iterator2 = 0
        self.defaultInfectionProbability = 0.5
        self.isMoving = False
        self.isInfected = False
        self.isHealthy = True
        self.startInfection = False
        self.alreadyInfected = False
        self.dayPassedAfterMeetingInfected = 0
        self.metWithInfected = False
        self.currentFloor = 1
        self.currentRoom = ""
        self.personWhoInfected = ""

    # checks in which floor the moving object is located
    def onWhichFloor(self,currentZ):
        for k, v in floorsAndValues.items():
            if currentZ<= max(v) and currentZ >= min(v):
                return k

    # checks the current room number where the moving object is located
    def checker(self):
            currentPointLocation = (self.path[self.iterator][0], self.path[self.iterator][1])
            for i, myobject in enumerate(GMLOBJ_3D_Objects):
                    if myobject.poly_path.contains_point(currentPointLocation):
                        return myobject.id
                    else:
                        pass

    # distance between self and other person
    def getD(self, x, y):
        # if (self.pathSize <= self.iterator):
        #     self.iterator = self.pathSize - 1
        return np.math.sqrt((self.path[self.iterator][0] - x) ** 2 + (self.path[self.iterator][1] - y) ** 2)


    # method in case when person meets with infected person and start having symptoms
    def makeInfectedByPerson(self):
        self.startInfection = True



    # method for checking whether all conditions are satisfied for being infected
    def InfectedDayChecker(self):
        global infectedHumanNumber,healthyHumanNumber
        global ct, timeArray
        if self.startInfection is True and self.dayPassedAfterMeetingInfected == 2:
            print("make person infected")
            self.makeInfected()

    # turn into infected person
    def makeInfected(self):
        self.isInfected = True
        self.isHealthy = False
        self.startInfection = False

    # method for check the meeting
    def inCaseOfMeeting(self,eachH,currentDay):
        if random.random() <= self.defaultInfectionProbability:
            eachH.makeInfectedByPerson()
            eachH.infectedDay = currentDay
            eachH.personWhoInfected = self.id


#Meeting class
class Meeting:
    def __init__(self):
        self.id = 0
        self.between = []
        self.meetingCoordinates = []
        self.floorNumber = 1
        self.roomNumber = 0
        self.day = 0



