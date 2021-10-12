from src.gmlParser import floorsAndValues, GMLOBJ_3D_Objects
import numpy as np
import random


class MovingObject:
    def __init__(self,id,typeMO):
        self.id = id
        self.type = typeMO
        self.startTime = 0
        self.endTime = 0
        self.path = []
        self.iterator = 0
        self.iterator2 = 0
        self.defaultInfectionProbability = 0.9
        self.isMoving = False
        self.isInfected = False
        self.isHealthy = True
        self.startInfection = False
        self.alreadyInfected = False
        self.metWithInfected = False
        self.becameNewInfected = False
        self.dayPassedAfterMeetingInfected = 0
        self.dayMetWithInfectedMO = 0
        self.IDInfectedMO = 0
        self.incubationVal = 0
        self.currentFloor = 1
        self.currentRoom = ""
        self.personWhoInfected = ""
        self.trajectory = []
        self.trajectoryZ = []

    # turn into infected person
    def makeInfected(self):
        self.isInfected = True
        self.isHealthy = False
        self.startInfection = False

    # method for check the meeting
    def inCaseOfMeeting(self,eachH,currentDay):
            eachH.makeInfectedByPerson()
            eachH.infectedDay = currentDay
            eachH.personWhoInfected = self.id

    # method for check the meeting
    def metWithInfectedMO(self,otherMO,day):
            self.startInfection = True
            self.dayMetWithInfectedMO = day
            self.IDInfectedMO = otherMO.id

    # checks in which floor the moving object is located
    def checkAtWhichFloor(self,currentZ):
        for k, v in floorsAndValues.items():
            if currentZ<= max(v) and currentZ >= min(v):
                return k

    # checks the current room number where the moving object is located
    def checker(self,currentPointLocation,floorN):
            #currentPointLocation = (self.path[self.iterator][0], self.path[self.iterator][1])
            for i, myobject in enumerate(GMLOBJ_3D_Objects):
                    if myobject.poly_path.contains_point(currentPointLocation) and myobject.floor==floorN:
                        return myobject.id
                    else:
                        pass

    # method for checking whether all conditions are satisfied for being infected
    def InfectedDayChecker(self):
        global infectedHumanNumber,healthyHumanNumber
        global ct, timeArray
        if self.startInfection is True and self.dayPassedAfterMeetingInfected >= self.incubationVal:
            if random.random() <= self.defaultInfectionProbability:
                    self.makeInfected()
                    self.becameNewInfected = True
            else:
                self.startInfection = False
                self.dayPassedAfterMeetingInfected = 0