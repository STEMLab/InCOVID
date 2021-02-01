import tkinter
from tkinter import *
import tkinter.filedialog
import iso8601 as iso8601
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from tkinter import Tk, Label, Entry, StringVar
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
import time
import numpy as np
import matplotlib.pyplot as plt
from src import constants, csvReader, gmlParser
from shapely.geometry import Point
import threading

humans = []
infectionCase = []
floorChanger = 1

# function for updating the values and the percentage in the pie chart
def updaterOfValuesAndPercentage(this, thisValues):
    output = int(this / 99.999*np.sum(thisValues))
    return "{:.1f}%\n({:d})".format(this, output)

# function for updating graph, pie chart, and label values
def update(ct, timeArray, infectedHumanNumber,healthPersonNumber):
        global c,axPie
        c.clear()
        c.plot(timeArray, ct,color="red")
        plt.ion()
        cvst, = c.plot(int(infectedHumanNumber), color="red", label="Infected people")
        c.legend(handles=[cvst])
        axPie.clear()
        dataProportion = np.array([healthPersonNumber, infectedHumanNumber])
        axPie.pie(dataProportion, autopct=lambda val: updaterOfValuesAndPercentage(val, dataProportion),
                  explode=constants.explode, labels=constants.labelCondition, shadow=True, colors=constants.colors)
        c.set_xlabel("Time")
        c.set_ylabel("Infected people")
        var2.set("Number of infected people: "+str(infectedHumanNumber))
        label2.pack()
        CurrentT = time.time()
        var3.set("Time: " + str(round(CurrentT-myTime, 2)))
        label3.pack(side="top",padx = 2, pady= 2)

def drawerByFloor(floorN):
    ax2D.collections.pop()
    ax2D.collections.pop()
    allPoints2D = []
    allObjects2D = []
    allPoints2D_Doors=[]
    allObjects2D_Doors = []
    global floorChanger
    floorChanger = floorN
    fig2D.suptitle("Floor "+str(floorN)+":", fontsize=12)
    # drawing the rooms and corridors 2D
    for myobject in gmlParser.gmlObjects_3D:
        if myobject.floor==floorN:
            for i in (range(len(myobject.allPos)-1)):
                 temp = [myobject.allPos[i][0], myobject.allPos[i][1], myobject.allPos[i][2]]
                 allPoints2D.append(temp)
            allObjects2D.append(allPoints2D)
            allPoints2D = []
    # drawing the doors 2D
    for myobject in gmlParser.gmlObjectsDoors_3D:
      if myobject.floor == floorN:
        for i in (range(len(myobject.allPos) - 1)):
            temp = [myobject.allPos[i][0], myobject.allPos[i][1], myobject.allPos[i][2]]
            allPoints2D_Doors.append(temp)
        allObjects2D_Doors.append(allPoints2D_Doors)
        allPoints2D_Doors = []
    thisIndoor2D = ax2D.add_collection3d(Poly3DCollection(allObjects2D,edgecolors='k', alpha=0.7,linewidth=1))
    thisIndoorDoors2D = ax2D.add_collection3d(Poly3DCollection(allObjects2D_Doors, facecolors='y', edgecolors='y',alpha=0.7, linewidth=1))
    ax2D.view_init(90)

# Graph class
# used for displaying graph
class Graph(tkinter.Frame):
    def __init__(self, parent):
        tkinter.Frame.__init__(self, parent)
        canvas = FigureCanvasTkAgg(f, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tkinter.BOTTOM, fill=tkinter.BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
        canvas.get_tk_widget().update_idletasks()

# PieGraph class
# used for displaying PieGraph
class PieGraph(tkinter.Frame):
    def __init__(self, parent):
        tkinter.Frame.__init__(self, parent)
        canvas = FigureCanvasTkAgg(myPie, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tkinter.BOTTOM, fill=tkinter.BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
        canvas.get_tk_widget().update_idletasks()

# update all scenes
def updateALL(t):
    first = updatingTheAnimation(t)
    second = updatingTheAnimation2D(t)
    return first+second


# used to animate the indoor gml and the update the movement of the people
def updatingTheAnimation(t):
    for h in humans:
        if (h.pathSize > h.pathCounter):
                h.moveOnPath()
                h.infectionProcess()
    outputFirst = [h.scatter for h in humans]
    return outputFirst

# update the scene of the infection in each floor
def updatingTheAnimation2D(t):
    tempList = []
    for h in infectionCase:
        if h.floorNumber == floorChanger:
            tempList.append(h)
            h.drawOnMap()
    outputSecond = [h.scatter for h in tempList]
    return outputSecond


# method used in order to find the path of the GML file
def path(entryPath):
        f = tkinter.filedialog.askopenfilename(
            parent=root, initialdir='C:',
            title='Choose file',
            filetypes=[('gml files', '.gml'),
                       ('xml files', '.xml')]
        )
        entryPath.set(str(f))


# method used in order to find the path of movement data made by SIMGen
def pathSIMOGen(entryPath):
        f = tkinter.filedialog.askopenfilename(
            parent=root, initialdir='C:',
            title='Choose file',
            filetypes=[('csv files', '.csv')]
        )
        entryPath.set(str(f))

def messageShower():
    if (infectedHumanNumber == HumanCount):
        displayWarning()

# Person class
class Person:
    def __init__(self,humanID, xyz, v,defaultInfectionPercentage):
        self.humanID = humanID
        self.xyz = np.array(xyz)
        self.v = np.array(v)
        self.path = []
        self.pathSize = 0
        self.pathCounter = 0
        self.infected = False
        self.healthy = True
        self.isMoving = False
        self.isStoping = True
        self.increaser = 0
        self.startT = []
        self.endT = []
        self.waitingTime = 0.0
        self.roomNumber = 0.0
        self.defaultInfectionProbability = defaultInfectionPercentage
        self.infectionCoordinates = []
        self.scatter, = ax.plot([], [], [], marker='', animated=True)

    def makeInfected(self):
        self.infected = True
        self.healthy = False
        self.scatter, = ax.plot([], [], [], color='red', label='Infected person', marker='o',
                                markeredgecolor='black', markeredgewidth=0.5, markersize=5, animated=True)


    def startmovement(self):
        if self.isMoving==False:
            start_time = threading.Timer(self.waitingTime, self.makeMover)
            start_time.start()

    def makeMover(self):
        self.isStoping = False
        self.isMoving = True
        if self.infected:
            self.scatter, = ax.plot([], [], [], color='red', label='Infected person', marker='o',
                                    markeredgecolor='black', markeredgewidth=0.5, markersize=5, animated=True)
        elif self.healthy:
            self.scatter, = ax.plot([], [], [], label='Healthy person', color='yellow', marker='o', markeredgecolor='black',
                                markeredgewidth=0.5, markersize=5, animated=True)
        hand, labl = ax.get_legend_handles_labels()
        by_label = dict(zip(labl, hand))
        ax.legend(by_label.values(), by_label.keys())

    def stopMoving(self):
        self.isMoving = False
        self.isStoping = True
        self.scatter, = ax.plot([], [], [], marker='', animated=True)

    def onWhichFloor(self,currentZ):
        if currentZ >= 0 and currentZ < 20:
           return 1
        elif currentZ >= 20 and currentZ < 40:
           return 2
        elif currentZ >= 40 and currentZ < 60:
           return 3
        elif currentZ >= 60 and currentZ < 80:
           return 4
        elif currentZ >= 80 and currentZ < 100:
           return 5

    def sameRoom(self,eachH):
        if(self.pathSize <= self.pathCounter):
            self.pathCounter = self.pathSize - 1
            self.increaser +=1
        if(eachH.pathSize <= eachH.pathCounter):
            eachH.pathCounter = eachH.pathSize - 1
            eachH.increaser +=1
        if (self.increaser == 1):
                  self.stopMoving()
        if (eachH.increaser == 1):
                  eachH.stopMoving()
        # checking if two person are in same floor
        if self.path[self.pathCounter][2] == eachH.path[eachH.pathCounter][2]:
            if self.roomNumber == eachH.roomNumber:
                    return True
            else:
                    return False

    def currentLoc(self):
            if self.isMoving is False:
                pass
            if self.isMoving is True and self.isStoping is False:
                myTempThread = threading.Thread(target=self.checker, daemon=True)
                myTempThread.start()

    def checker(self):
            p = Point(self.path[self.pathCounter][0], self.path[self.pathCounter][1])
            for myobject in gmlParser.gmlObjects_3D:
                # checking current room number where the person now is located
                if myobject.poly.contains(p):
                    self.roomNumber = myobject.objectID

    def inCaseOfInfection(self,eachH):
        global infectedHumanNumber,healthyHumanNumber
        global ct, timeArray
        eachH.makeInfected()
        tempObject = InfectionCase()
        tempObject.infectionCoordinates.append(eachH.path[eachH.pathCounter][0])
        tempObject.infectionCoordinates.append(eachH.path[eachH.pathCounter][1])
        tempObject.infectionCoordinates.append(eachH.path[eachH.pathCounter][2])
        tempObject.floorNumber = int(eachH.onWhichFloor(eachH.path[eachH.pathCounter][2]))
        infectionCase.append(tempObject)
        tempL = eachH.path[eachH.pathCounter][0], eachH.path[eachH.pathCounter][1]
        eachH.infectionCoordinates.append(tempL)
        infectedHumanNumber = infectedHumanNumber + 1
        later = time.time()
        intTime = later - myTime
        ct.append(infectedHumanNumber)
        timeArray.append(intTime)
        newCase = str(eachH.humanID) + "  |  " + str(round(intTime, 2))
        tkinter.Label(frameNew, font=constants.scrollFontSmall, text=newCase).pack()
        healthyHumanNumber = HumanCount - infectedHumanNumber
        update(ct, timeArray, infectedHumanNumber,healthyHumanNumber)

    def infectionProcess(self):
            # if the person is infected
            if self.isStoping is False and self.isMoving is True and self.infected is True:
                # find the non-infected person
                for eachH in humans:
                 if self.humanID != eachH.humanID:
                     if eachH.healthy == True and eachH.isStoping == False and eachH.isMoving == True:
                       if self.sameRoom(eachH):
                        # find the distance between them
                        d = eachH.getD(self.path[self.pathCounter][0], self.path[self.pathCounter][1])
                        # if the distance between two person is more than threshold distance, the probability of getting infected is ((default infection probability)/(distance between two Person objects^2))
                        if d>spreadDistance:
                            infectionDictanceP = (self.defaultInfectionProbability/d**2)
                            if np.random.random() < infectionDictanceP:
                                self.inCaseOfInfection(eachH)
                        # if the distance between two person is less than threshold distance then default infection probability will be applied
                        if d<=spreadDistance:
                             if np.random.random() < self.defaultInfectionProbability:
                                 self.inCaseOfInfection(eachH)

    # method for checking is person infected
    def isInfected(self):
        if self.infected:
            return True

    # method for checking is person is healthy
    def isHealthy(self):
        if self.healthy:
            return True

    # distance between two person
    def getD(self, x, y):
        if (self.pathSize <= self.pathCounter):
            self.pathCounter = self.pathSize - 1
        return np.math.sqrt((self.path[self.pathCounter][0] - x) ** 2 + (self.path[self.pathCounter][1] - y) ** 2)

    # for moving on path
    def moveOnPath(self):
        if self.isMoving:
            tempVarX = np.float64(self.path[self.pathCounter][0])
            tempVarY = np.float64(self.path[self.pathCounter][1])
            tempVarZ = np.float64(self.path[self.pathCounter][2])
            self.pathCounter = self.pathCounter + 1
            self.scatterZ(tempVarX,tempVarY,tempVarZ)

    # scatter method
    def scatterZ(self,tempVarX,tempVarY,tempVarZ):
        self.scatter.set_xdata(tempVarX)
        self.scatter.set_ydata(tempVarY)
        self.scatter.set_3d_properties(tempVarZ)

# used in order to display the warning message
def displayWarning():
        tkinter.messagebox.showinfo("Info", "All people were infected")

# continue animation function
def continueAnimation(anim):
    anim.event_source.start()

# pause animation function
def pauseAnimation(anim):
    anim.event_source.stop()

#InfectionCase class
class InfectionCase:
    def __init__(self):
        self.infectionCoordinates = []
        self.floorNumber = 1
        self.scatter, = ax2D.plot([], [], [], label='Infection case',color='orange',marker = 'p',markeredgecolor = 'black',markeredgewidth=0.6, markersize=6, animated=True)
        hand, labl = ax2D.get_legend_handles_labels()
        by_label = dict(zip(labl, hand))
        ax2D.legend(by_label.values(), by_label.keys())

    # for drawing
    def drawOnMap(self):
        tempVarX = np.float64(self.infectionCoordinates[0])
        tempVarY = np.float64(self.infectionCoordinates[1])
        tempVarZ = np.float64(self.infectionCoordinates[2])
        self.scatter.set_xdata(tempVarX)
        self.scatter.set_ydata(tempVarY)
        self.scatter.set_3d_properties(tempVarZ)

def closeFunction():
    ax.collections.pop()
    ax2D.collections.pop()
    top.destroy()
    root.destroy()

# SECOND WINDOW
def open_window(pathGML, pathSIMOGenMovData,numberOfInfected,percentageInfection,spreadD):
    global top
    top = Toplevel()
    top.title("Virus propagation model")
    top.geometry("300x300+120+120")
    top.attributes('-fullscreen', True)
    button1 = Button(top, text="Close", font = constants.fontNameSecondVersion, command=lambda top=top: closeFunction())
    button1.pack(padx=10,pady=10)

    global ax,fig,fig2D,ax2D
    fig = Figure(figsize=(7, 7), dpi=100,facecolor='#F0F0F0')
    ax = Axes3D(fig)
    fig2D = Figure(figsize=(5, 5), dpi=100,facecolor='#F0F0F0')
    ax2D = Axes3D(fig2D)
    allPoints = []
    allObjects = []
    allPointsDoors = []
    allObjectsDoors = []
    global spreadDistance
    spreadDistance = float(spreadD.get())
    # scaling by 1/150
    spreadDistance = spreadDistance/150
    # parsing indoor gml data
    gmlFloors = gmlParser.myGML_3D(pathGML.get())
    # parsing movement data created from SIMOGen program
    fromCSV, idWithCoord, id_arr = csvReader.gettingData(pathSIMOGenMovData.get())
    for eachObject in gmlParser.gmlObjects_MIN_MAX_3D:
        print("highest X:")
        print(eachObject.max_X)
        print("highest Y:")
        print(eachObject.max_Y)
        print("highest Z:")
        print(eachObject.max_Z)
        print("--------------------")
        print("lowest X:")
        print(eachObject.min_X)
        print("lowest Y:")
        print(eachObject.min_Y)
        print("lowest Z:")
        print(eachObject.min_Z)

    global canvas1,frame_top,canvas,canvas2D,frameNew
    canvas1 = tkinter.Canvas(top, highlightbackground="black", highlightcolor="black", highlightthickness=1)
    canvas1.pack(padx=20, pady=20, expand=True, fill = "both", side="right")
    frame_top = tkinter.Frame(top,highlightbackground="black", highlightcolor="black", highlightthickness=1)
    frame_top.pack(side="top", padx=20, pady=10)
    varNew = StringVar()
    labelNew = Label(frame_top, textvariable=varNew, font=('Arial', 14), relief=FLAT)
    varNew.set("Virus propagation model in Indoor space")
    labelNew.pack(side="top", padx=20, pady=10)
    frame_bottom = tkinter.Frame(frame_top)
    frame_bottom.pack(side="bottom", padx=5, pady=10)
    canvas = FigureCanvasTkAgg(fig, master=frame_top)
    canvas.get_tk_widget().pack(side="left",padx=5,pady=10)

    canvas.mpl_connect('button_press_event', ax.axes._button_press)
    canvas.mpl_connect('button_release_event', ax.axes._button_release)
    canvas.mpl_connect('motion_notify_event', ax.axes._on_move)

    global HumanCount,infectedHumanNumber,healthyHumanNumber
    HumanCount = len(id_arr)
    # creating objects by assigning their id's from csv file
    for i in np.arange(0, HumanCount):
        xyz = np.random.rand(1, 1)[0]
        v = np.random.rand(1, 1)[0] * 0.1
        regularHuman = Person(i, xyz, v, float(percentageInfection.get()))
        regularHuman.humanID = id_arr[i]
        humans.append(regularHuman)
    # adding path,start and end time to each person
    for h in humans:
        for i in range(len(idWithCoord)):
            if h.humanID == idWithCoord[i][0]:
                temporary = [idWithCoord[i][1], idWithCoord[i][2], idWithCoord[i][3]+2.5]
                h.path.append(temporary)
                updatedStartTime = iso8601.parse_date(idWithCoord[i][4])
                updatedEndTime = iso8601.parse_date(idWithCoord[i][5])
                h.startT.append(updatedStartTime)
                h.endT.append(updatedEndTime)
    # adding the size of the path to each person
    for human in humans:
        human.pathSize = int(len(human.path))
    infectedHumanNumber = 0
    timeStartAll = []
    for human in humans:
        timeStartAll.append(human.startT[0])
    startOfMovementTime = min(timeStartAll)
    for human in humans:
        difference = human.startT[0] - startOfMovementTime
        human.waitingTime = difference.seconds
    secondFrame = tkinter.Frame(frame_top,highlightbackground="black", highlightcolor="black", highlightthickness=1)
    canvasScroll = tkinter.Canvas(secondFrame)
    scrollbar = tkinter.Scrollbar(secondFrame, orient="vertical", command=canvasScroll.yview)
    frameNew = tkinter.Frame(canvasScroll)
    frameNew.bind(
        "<Configure>",
        lambda e: canvasScroll.configure(
            scrollregion=canvasScroll.bbox("all")
        )
    )
    canvasScroll.create_window((0, 0), window=frameNew, anchor="nw")
    canvasScroll.configure(yscrollcommand=scrollbar.set)
    tkinter.Label(frameNew, font=constants.scrollFontBig, text="Person id  |  Infection time").pack()
    tkinter.Label(frameNew, font=constants.scrollFontBig, text="--------------------------------------").pack()
    numberInfectedFromEntry = int(numberOfInfected.get())
    for i in range(numberInfectedFromEntry):
        humans[i].makeInfected()
        initalCase = str(humans[i].humanID) + "  |  " + str(0.00)
        tkinter.Label(frameNew, font = constants.scrollFontSmall, text=initalCase).pack()
        infectedHumanNumber = infectedHumanNumber + 1
    healthyHumanNumber = HumanCount - infectedHumanNumber
    secondFrame.pack(padx=5,pady=5)
    canvasScroll.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    thirdFrame = tkinter.Frame(frame_top, highlightbackground="black", highlightcolor="black", highlightthickness=1)
    tkinter.Label(thirdFrame, font=constants.scrollFontBig, text="Infection case coordinates in each floor").pack(padx=3, pady=3)
    canvas2D = FigureCanvasTkAgg(fig2D, master=thirdFrame)
    thirdFrame.pack(padx=5, pady=5)
    canvas2D.get_tk_widget().pack(side="bottom",expand=True,padx=5,pady=10)
    canvas2D.mpl_connect('button_press_event', ax2D.axes._button_press)
    canvas2D.mpl_connect('button_release_event', ax2D.axes._button_release)
    canvas2D.mpl_connect('motion_notify_event', ax2D.axes._on_move)
    floorNumber = 1
    button1F = tkinter.Button(thirdFrame, text="1st Floor", font=constants.fontName, command=lambda floorNumber=floorNumber:drawerByFloor(floorNumber))
    button1F.pack(padx=10, pady=1, side="left")
    if 2 in gmlFloors:
        floorNumber = 2
        button2F = tkinter.Button(thirdFrame, text="2nd Floor", font=constants.fontName, command=lambda floorNumber=floorNumber:drawerByFloor(floorNumber))
        button2F.pack(padx=10, pady=1, side="left")
    if 3 in gmlFloors:
        floorNumber = 3
        button3F = tkinter.Button(thirdFrame, text="3nd Floor", font=constants.fontName, command=lambda floorNumber=floorNumber:drawerByFloor(floorNumber))
        button3F.pack(padx=10, pady=1, side="left")
    if 4 in gmlFloors:
        floorNumber = 4
        button4F = tkinter.Button(thirdFrame, text="4th Floor", font=constants.fontName, command=lambda floorNumber=floorNumber:drawerByFloor(floorNumber))
        button4F.pack(padx=10, pady=1, side="left")
    global ct,timeArray
    ct = [infectedHumanNumber]
    timeArray = [0]
    # used to initialize the graph drawer
    global f, c
    f = plt.figure(figsize=(6, 4))
    c = f.add_subplot(1, 1, 1)
    c.axis([0, 5, 0, HumanCount])
    caja = plt.Rectangle((0, 0), 100, 100, fill=True)
    cvst, = c.plot(infectedHumanNumber, color="red", label="Infected people")
    c.legend(handles=[cvst])
    c.set_xlabel("Time")
    c.set_ylabel("Infected people")
    global myPie, axPie
    dataProportion = np.array([healthyHumanNumber, infectedHumanNumber])
    # Creating pie
    myPie, axPie = plt.subplots(figsize=(6, 6))
    axPie.pie(dataProportion, autopct = lambda val: updaterOfValuesAndPercentage(val, dataProportion), explode=constants.explode, labels=constants.labelCondition, shadow = True, colors = constants.colors, wedgeprops = constants.wedgeProp)
    # setting the dimesions of the matplot 3D
    xVal = eachObject.max_X
    ax.set_xlim3d([0.0, xVal])
    ax.set_xlabel('X')
    yVal = eachObject.max_Y*2
    ax.set_ylim3d([-10.0,yVal])
    ax.set_ylabel('Y')
    zVal = eachObject.max_Z*5
    ax.set_zlim3d([-10.0, zVal])
    ax.set_zlabel('Z')
    # setting the dimesions of the matplot 2D
    xVal2d = eachObject.max_X
    ax2D.set_xlim3d([0.0, xVal2d])
    ax2D.set_xlabel('X')
    yVal2d = eachObject.max_Y*2
    ax2D.set_ylim3d([-10.0,yVal2d])
    ax2D.set_ylabel('Y')
    zVal2d = eachObject.max_Z*5
    ax2D.set_zlim3d([-10.0, zVal2d])
    ax2D.set_zlabel('Z')
    # drawing the rooms and corridors
    for myobject in gmlParser.gmlObjects_3D:
        for i in (range(len(myobject.allPos)-1)):
            temp = [myobject.allPos[i][0], myobject.allPos[i][1], myobject.allPos[i][2]]
            allPoints.append(temp)
        allObjects.append(allPoints)
        allPoints = []

    # drawing the doors
    for myobject in gmlParser.gmlObjectsDoors_3D:
        for i in (range(len(myobject.allPos) - 1)):
            temp = [myobject.allPos[i][0], myobject.allPos[i][1], myobject.allPos[i][2]]
            allPointsDoors.append(temp)
        allObjectsDoors.append(allPointsDoors)
        allPointsDoors = []

    # default view of the first floor
    allPoints2D = []
    allObjects2D = []
    allPoints2D_Doors=[]
    allObjects2D_Doors = []
    # drawing the rooms and corridors 2D
    for myobject in gmlParser.gmlObjects_3D:
        if myobject.floor==1:
            for i in (range(len(myobject.allPos)-1)):
                 temp = [myobject.allPos[i][0], myobject.allPos[i][1], myobject.allPos[i][2]]
                 allPoints2D.append(temp)
            allObjects2D.append(allPoints2D)
            allPoints2D = []

    # drawing the doors
    for myobject in gmlParser.gmlObjectsDoors_3D:
      if myobject.floor == 1:
        for i in (range(len(myobject.allPos) - 1)):
            temp = [myobject.allPos[i][0], myobject.allPos[i][1], myobject.allPos[i][2]]
            allPoints2D_Doors.append(temp )
        allObjects2D_Doors.append(allPoints2D_Doors)
        allPoints2D_Doors = []

    global myTime,var1, var2, var3, label1, label2, label3
    myTime = time.time()
    var1 = StringVar()
    label1 = Label(canvas1, textvariable=var1, font=('Arial', 14), relief=FLAT)
    var1.set("Total number of people: " + str(HumanCount))
    label1.pack(side="top", padx=5, pady=5)
    var2 = StringVar()
    label2 = Label(canvas1, textvariable=var2, font=('Arial', 14), relief=FLAT)
    var2.set("Number of infected people: "+str(infectedHumanNumber))
    label2.pack(side="top", padx=5, pady=5)
    var3 = StringVar()
    label3 = Label(canvas1, textvariable=var3, font=('Arial', 14), relief=FLAT)
    var3.set("Time: 0")
    label3.pack(side="top", padx=5, pady=5)
    labelNew = Label(canvas1, justify='center')
    labelNew.pack()
    Graph(canvas1).pack(side="bottom",padx=10,pady=10)
    PieGraph(canvas1).pack(side="bottom",padx=10,pady=10)

    # drawing 3D version
    thisIndoor = ax.add_collection3d(Poly3DCollection(allObjects,edgecolors='k', alpha=0.1,linewidth=0.17))
    thisIndoorDoors = ax.add_collection3d(Poly3DCollection(allObjectsDoors,facecolors='y',alpha=0.5, linewidth=0.5))
    # drawing 2D version
    thisIndoor2D = ax2D.add_collection3d(Poly3DCollection(allObjects2D,edgecolors='k', alpha=0.7,linewidth=1))
    thisIndoorDoors2D = ax2D.add_collection3d(Poly3DCollection(allObjects2D_Doors, facecolors='y', edgecolors='y',alpha=0.7, linewidth=1))
    ax.set_axis_off()
    ax2D.set_axis_off()
    ax2D.view_init(90)
    # start movement at certain time
    for h in humans:
        h.startmovement()
    # check the location of the human
    for human in humans:
        human.currentLoc()

    # frames
    N=800
    global anim,anim2D
    anim = FuncAnimation(fig, updateALL, frames=N, interval=800/N, blit=True, repeat=True)
    buttonPausingMov = tkinter.Button(frame_bottom, text="Pause simulation", bg='brown', fg='white', font=constants.fontName, command=lambda anim=anim:pauseAnimation(anim))
    buttonPausingMov.pack(padx=5, pady=5, side="left")
    buttonStartingMov = tkinter.Button(frame_bottom, text="Continue simulation", bg='green', fg='white', font=constants.fontName, command=lambda anim=anim:continueAnimation(anim))
    buttonStartingMov.pack(padx=5, pady=5, side="left")
    canvas.draw()
    canvas2D.draw()

if __name__ == "__main__":
    root = Tk()
    label = tkinter.Label(root, text="InCOVID", font=constants.BigFontName)
    label.pack(padx=5, pady=20)
    entryPath = tkinter.StringVar()
    entry = tkinter.Entry(root, textvariable=entryPath, font=constants.fontName)
    entryPath.set("")
    entry.pack()
    b1 = tkinter.Button(root, text='Select IndoorGML file (3D version)', font=constants.fontName, relief='raised',
                        command=lambda  entryPath=entryPath: path(entryPath))
    b1.pack(padx=20, pady=20)
    entryPathSIMOGenData = tkinter.StringVar()
    entry2 = tkinter.Entry(root, textvariable=entryPathSIMOGenData, font=constants.fontName)
    entryPathSIMOGenData.set("")
    entry2.pack()
    b2 = tkinter.Button(root, text='Select SIMOGen movement data', font=constants.fontName, relief='raised',
                        command=lambda  entryPathSIMOGenData=entryPathSIMOGenData: pathSIMOGen(entryPathSIMOGenData))
    b2.pack(padx=20, pady=20)
    labelInfectedPeople = StringVar()
    labelInfectedPeople.set("Enter the initial number of infected people:")
    labelinfected = Label(root, textvariable=labelInfectedPeople, font=constants.fontName, height=2)
    labelinfected.pack()
    numberOfInfected = StringVar(None)
    numberOfInfected.set("3")
    numInf = Entry(root, textvariable=numberOfInfected, font=constants.fontName, width=10)
    numInf.pack()
    labelInfectionPercentage = StringVar()
    labelInfectionPercentage.set("Enter the default infection rate:")
    labelInfPercntg = Label(root, textvariable=labelInfectionPercentage, font=constants.fontName, height=2)
    labelInfPercntg.pack()
    percentageInfection = StringVar(None)
    percentageInfection.set("0.9")
    perInfec = Entry(root, textvariable=percentageInfection, font=constants.fontName, width=10)
    perInfec.pack()
    labelSpreadDistance = StringVar()
    labelSpreadDistance.set("Enter the threshold distance:")
    labelD = Label(root, textvariable=labelSpreadDistance, font=constants.fontName, height=2)
    labelD.pack()
    spreadD = StringVar(None)
    spreadD.set("2")
    sD = Entry(root, textvariable=spreadD, font=constants.fontName, width=10)
    sD.pack()
    bStart = Button(root, text="Start", font=constants.fontName, bg='blue', fg='white', command=lambda entryPath=entryPath, entryPathSIMOGenData=entryPathSIMOGenData, numberOfInfected=numberOfInfected, percentageInfection=percentageInfection, spreadD=spreadD:open_window(entryPath, entryPathSIMOGenData, numberOfInfected, percentageInfection, spreadD))
    bStart.pack(padx=30, pady=30)
    root.geometry("500x580+600+200")
    root.mainloop()