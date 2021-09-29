# Person class
class MovingObject:
    def __init__(self,id):
        self.id = id
        self.path = []
        self.pathSize = 0
        self.pathCounter = 0
        self.alreadyInfected = False
        self.infected = False
        self.healthy = True
        self.isMoving = False
        self.isStoping = False
        self.startInfection = False
        self.personWhoInfected = 0
        self.infectedDay = 0
        self.dayPassedAfterMeetingInfected = 0
        self.startT = []
        self.endT = []
        self.timeline = []
        self.waitingTime = 0.0
        self.roomNumber = 0
        self.meetingCoordinates = ()
        self.meetingRoom = ""
        self.meetingFloor = 0



