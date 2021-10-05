# Person class
from src.gmlParser import floorsAndValues, GMLOBJ_3D_Objects
import numpy as np

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
        self.isMoving = False
        self.isInfected = False
        self.isHealthy = True
        self.metWithInfected = False
        self.currentFloor = 1
        self.currentRoom = ""

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





