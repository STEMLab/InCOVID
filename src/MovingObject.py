from src.gmlParser import dictRooms
from src.gmlParser import floorsAndValues

global floorsAndValues,dictRooms

class MovingObject:
    def __init__(self,id,typeMO):
        self.id = id
        self.type = typeMO
        self.startTime = 0
        self.endTime = 0
        self.path = []
        self.iterator = 0
        self.isInfected = False
        self.isHealthy = True
        self.startInfection = False
        self.dayPassedAfterMeetingInfected = 0
        self.trajectory = []
        self.trajectoryZ = []
        self.movingBoolList = []

    # turn into infected person
    def makeInfected(self):
        self.isInfected = True
        self.isHealthy = False
        self.startInfection = False

    # checks in which floor the moving object is located
    def checkAtWhichFloor(self,currentZ):
        for k, v in floorsAndValues.items():
            if currentZ<= max(v) and currentZ >= min(v):
                return k

    # checks the current room number where the moving object is located
    def checker(self,currentPointLocation,floorN):
        for k, v in dictRooms.items():
            if k == floorN:
                for eachR in range(len(v)):
                    if v[eachR].poly_path.contains_point(currentPointLocation):
                        return v[eachR].id