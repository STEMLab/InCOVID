import tkinter
from tkinter import ttk
import tkinter.filedialog
from src import gmlParser
import iso8601 as iso8601
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from src.csvReader import *
from src.constants import *
from src.gmlParser import *
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import networkx as nx
import random

globalTime = 0
beforeMovementhumans = []
humans = []
IncubationVal = 0
infectionCase = []
floorChanger = 1
infectedHumanNumber = 0
currentDay = 1
meetingCase = []

# shuffle the path and waiting time of each person
def shuffleThePath():
    humansCopy = humans.copy()
    for ival,h in enumerate(humans):
        randomHumanI = random.randint(0,len(humansCopy))
        # id and other attributes will be the same, ONLY the path, path size, waiting time will change
        h.path = humansCopy[randomHumanI].path
        h.pathSize = humansCopy[randomHumanI].pathSize

#Meeting class
class Meeting:
    def __init__(self):
        self.id = 0
        self.between = []
        self.meetingCoordinates = []
        self.floorNumber = 1
        self.roomNumber = 0
        self.day = 0
        self.scatter, = ax2D.plot([], [], [], color='yellow', label='Meeting with infected person case', marker='p', markeredgecolor='black',
                                  markeredgewidth=0.6, markersize=6, animated=True)
        hand, labl = ax2D.get_legend_handles_labels()
        by_label = dict(zip(labl, hand))
        ax2D.legend(by_label.values(), by_label.keys(),loc="lower center")

    # for drawing
    def drawOnMap(self):

        tempVarX = np.float64(self.meetingCoordinates[0])
        tempVarY = np.float64(self.meetingCoordinates[1])
        tempVarZ = np.float64(self.meetingCoordinates[2])
        self.scatter.set_xdata(tempVarX)
        self.scatter.set_ydata(tempVarY)
        self.scatter.set_3d_properties(tempVarZ)

# for visualization IndoorGML data
def drawer(ax,allPoints,allPointsDoors,allObjects,allObjectsDoors,v3d,alphaVal,lineWidthVal,alphaVal2,lineWidthVal2,FloorCheck,floorN):
    # drawing the rooms and corridors
    def drawEach(object, allPoints, allObjects):
        for ival2, i in enumerate((range(len(object.allPos)))):
            temp = [object.allPos[i][0], object.allPos[i][1], object.allPos[i][2]]
            allPoints.append(temp)
        allObjects.append(allPoints)
        allPoints = []
        return allObjects, allPoints
    # drawing doors
    def drawEachDoor(object, allPointsDoors, allObjectsDoors):
        for ival2, i in enumerate((range(len(myobject.allPos)))):
            temp = [myobject.allPos[i][0], myobject.allPos[i][1], myobject.allPos[i][2]]
            allPointsDoors.append(temp)
        allObjectsDoors.append(allPointsDoors)
        allPointsDoors = []
        return allObjectsDoors, allPointsDoors
    for ival,myobject in enumerate(GMLOBJ_3D_Objects):
        if v3d==False:
            if FloorCheck == True:
                if myobject.floor == floorN:
                    allObjects, allPoints = drawEach(myobject, allPoints, allObjects)
            elif FloorCheck == False:
                if myobject.floor == 1:
                    allObjects, allPoints = drawEach(myobject, allPoints, allObjects)
        else:
            allObjects, allPoints = drawEach(myobject, allPoints, allObjects)
    # drawing the doors
    for ival,myobject in enumerate(gmlObjectsDoors_3D):
        if v3d==False:
            if FloorCheck == True:
                if myobject.floor == floorN:
                    allObjectsDoors, allPointsDoors = drawEachDoor(myobject, allPointsDoors, allObjectsDoors)
            elif FloorCheck == False:
                if myobject.floor == 1:
                    allObjectsDoors, allPointsDoors = drawEachDoor(myobject, allPointsDoors, allObjectsDoors)
        else:
            allObjectsDoors, allPointsDoors = drawEachDoor(myobject, allPointsDoors, allObjectsDoors)
    thisIndoor = ax.add_collection3d(Poly3DCollection(allObjects,edgecolors='k', alpha=alphaVal,linewidth=lineWidthVal))
    thisIndoorDoors = ax.add_collection3d(Poly3DCollection(allObjectsDoors,facecolors='y',alpha=alphaVal2, linewidth=lineWidthVal2))


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
                  explode=explode, labels=labelCondition, shadow=True, colors=colors)
        c.set_xlabel("Time (days)")
        c.set_ylabel("Infected people")
        var2.set("Number of infected people: "+str(infectedHumanNumber))
        label2.pack()

def drawerByFloor(floorN):
    ax2D.collections.pop()
    ax2D.collections.pop()
    allPoints2D = []
    allObjects2D = []
    allPoints2D_Doors=[]
    allObjects2D_Doors = []
    global floorChanger
    floorChanger = floorN
    fig2D.suptitle("Floor "+str(floorChanger)+":", fontsize=12)
    alphaVal = 0.7
    lineWidthVal = 1
    alphaVal2 = 0.7
    lineWidthVal2 = 1
    drawer(ax2D, allPoints2D,allPoints2D_Doors, allObjects2D, allObjects2D_Doors, False, alphaVal,lineWidthVal,alphaVal2,lineWidthVal2,True,floorChanger)

# Graph class for graph and pie graph
class Graph(tkinter.Frame):
    def __init__(self, parent,param):
        tkinter.Frame.__init__(self, parent)
        canvas = FigureCanvasTkAgg(param, self)
        canvas.get_tk_widget().pack(side=tkinter.BOTTOM, fill=tkinter.BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
        canvas.get_tk_widget().update_idletasks()

# update all scenes
def updateALL(t):
    global globalTime
    globalTime += 1
    for ival, h in enumerate(humans):
            if globalTime == max(h.timeline):
                h.startmovement()
            else:
                pass
    first = updatingTheAnimation(t)
    second = updatingTheAnimation2D(t)
    return first+second

def animateinit():
    return [h.scatter for h in humans]

# used to animate the indoor gml and the update the movement of the people
def updatingTheAnimation(t):
    global txt, currentDay, globalTime
    for ival,h in enumerate(humans):
        if (h.pathSize > h.pathCounter and h.isMoving == True):
                h.moveOnPath()
                h.meetingProcess()
    if all(h.isStoping == True for h in humans):
        currentDay += 1
        labelDay.set("Day: "+str(currentDay))
        for ival, h in enumerate(humans):
            if h.startInfection==True and h.alreadyInfected == False:
                h.dayPassedAfterMeetingInfected+=1
                h.InfectedDayChecker()
        for ival, h in enumerate(humans):
            h.isStoping = False
        globalTime = 0
    outputFirst = [h.scatter for h in humans]
    return outputFirst

# for visualization infection cases
def visualize():
    x = []
    y = []
    z = []
    for myobject in gmlParser.GMLOBJ_3D_Objects:
        for i in (range(len(myobject.allPos) - 2)):
            temp = np.float64(myobject.allPos[i][0])
            temp2 = np.float64(myobject.allPos[i][1])
            temp3 = np.float64(myobject.allPos[i][2])
            tempX = np.float64(myobject.allPos[i + 1][0])
            temp2Y = np.float64(myobject.allPos[i + 1][1])
            temp3Z = np.float64(myobject.allPos[i + 1][2])
            x.append(temp)
            x.append(tempX)
            x.append(None)
            y.append(temp2)
            y.append(temp2Y)
            y.append(None)
            z.append(temp3)
            z.append(temp3Z)
            z.append(None)

    x2 = []
    y2 = []
    z2 = []
    for myobject in gmlParser.gmlObjectsDoors_3D:
        for i in (range(len(myobject.allPos) - 1)):
            temp = np.float64(myobject.allPos[i][0])
            temp2 = np.float64(myobject.allPos[i][1])
            temp3 = np.float64(myobject.allPos[i][2])
            tempX = np.float64(myobject.allPos[i + 1][0])
            temp2Y = np.float64(myobject.allPos[i + 1][1])
            temp3Z = np.float64(myobject.allPos[i + 1][2])
            x2.append(temp)
            x2.append(tempX)
            x2.append(None)

            y2.append(temp2)
            y2.append(temp2Y)
            y2.append(None)

            z2.append(temp3)
            z2.append(temp3Z)
            z2.append(None)


    x3 = []
    y3 = []
    z3 = []
    annotation = []
    edgesList = []
    labelsList = []
    labels1 = []
    from collections import defaultdict
    d = defaultdict(lambda: len(d))

    for i,k in enumerate(meetingCase):
        tempVarX = np.float64(k.meetingCoordinates[0])
        tempVarY = np.float64(k.meetingCoordinates[1])
        tempVarZ = np.float64(k.meetingCoordinates[2])
        annotation ="Meeting between"+ "<br>Infected person<br>" +str(k.between[0]) + "<br> and"+"<br>Healthy person<br>" +str(k.between[1]) + "<br> in the room: " + str(k.roomNumber) + "<br> At the floor: " + str(k.floorNumber) +"<br> On the day:" + str(k.day)

        x3.append(tempVarX)
        y3.append(tempVarY)
        z3.append(tempVarZ)

    # Initialize figure with 2 subplots
    fig = make_subplots(
        rows=1, cols=2,subplot_titles=("Infection case coordinates", "Network tree of infection"), print_grid =False,
        specs=[[{'type': 'surface'}, {'type': 'scatter'}],
               ])

    # adding cellspaces
    fig.add_trace(
        go.Scatter3d(x=x, y=y, z=z, mode='lines',
                     surfacecolor='#0000FF', showlegend=False, hoverinfo='skip',
                     line=dict(
                         width=4,
                         color='#0000FF'
                     )),
        row=1, col=1)

    # adding doors
    fig.add_trace(
        go.Scatter3d(x=x2, y=y2, z=z2, mode='lines',
                     surfacecolor='#000000', showlegend=False, hoverinfo='skip',
                     line=dict(
                         width=4,
                         color='#964B00'
                     )),
        row=1, col=1)

    # adding meeting coordinates
    fig.add_trace(
            go.Scatter3d(x=x3, y=y3, z=z3, mode='markers', showlegend=False, text= annotation, marker=dict(color="#F6BE00", size=5,line=dict(width=2,color='DarkSlateGrey')),
            ),row=1, col=1)
    # creating network graph
    G = nx.Graph()
    my_nodes = range(len(humans))
    G.add_nodes_from(my_nodes)
    for i,k in enumerate(humans):
        labelsList.append("Person " + str(k.humanID))
    for i, k in enumerate(humans):
        for i2, k2 in enumerate(humans):
            if humans[i].humanID != humans[i2].humanID:
                for z, j in enumerate(meetingCase):
                        if humans[i].humanID == j.between[0]  and humans[i2].humanID == j.between[1]:
                            edge1 = i
                            edge2 = i2
                            edgesList.append((edge1, edge2))
                            labels1.append("Meeting between"+ "<br>Infected person<br>" +str(j.between[0]) + "<br> and"+"<br>Healthy person<br>" +str(j.between[1]) + "<br> in the room: " + str(j.roomNumber) + "<br> At the floor: " + str(j.floorNumber) +"<br> On the day:" + str(j.day))

    my_edges = edgesList
    G.add_edges_from(my_edges)
    pos = nx.spring_layout(G)
    labels = labelsList
    Xn = [pos[k][0] for k in range(len(pos))]
    Yn = [pos[k][1] for k in range(len(pos))]

    fig.add_trace(
            go.Scatter(x=Xn,y=Yn,  mode='markers',text=labels,
                 hoverinfo='text',showlegend=False,  marker=dict(color="#F6BE00", size=15,line=dict(width=2,color='DarkSlateGrey')),
            ),row=1, col=2)

    Xe = []
    Ye = []
    xt = []
    yt = []
    for e in G.edges():
        mid_edge = 0.5 * (pos[e[0]] + pos[e[1]])
        xt.append(mid_edge[0])
        yt.append(mid_edge[1])
    # adding edges
    fig.add_trace(
            go.Scatter(x=Xe,y=Ye,  mode='lines',
            ),row=1, col=2)
    # adding nodes
    fig.add_trace(
            go.Scatter(x=Xn,y=Yn,  mode='markers',text=labels,
                 hoverinfo='text',showlegend=False,  marker=dict(color="#F6BE00", size=15,line=dict(width=2,color='DarkSlateGrey')),
            ),row=1, col=2)
    # adding relations between them
    fig.add_trace(
            go.Scatter(x=xt, y=yt,mode='lines', text=labels1, textposition='bottom center', hoverinfo='text'
            ),row=1, col=2)

    fig.update_yaxes(
        scaleanchor="x",
        scaleratio=1
    )

    fig.update_layout(
        title_text='InCOVID', uirevision=True,
        plot_bgcolor = '#FFFFFF',
        showlegend=False,
    )

    fig.update_layout(scene_aspectmode='data')

    config = {
        'displayModeBar': False,
        'editable': False,
        'showLink': False,
        'displaylogo': False,
    }

    fig.show(config=config)

# update the scene of the infection in each floor
def updatingTheAnimation2D(t):
    tempList = []
    for hval,h in enumerate(meetingCase):
        if h.floorNumber == floorChanger:
            tempList.append(h)
            h.drawOnMap()
    outputSecond = [h.scatter for i,h in enumerate(tempList)]
    return outputSecond

# continue animation function
def continueAnimation(anim):
    anim.event_source.start()

# pause animation function
def pauseAnimation(anim):
    anim.event_source.stop()

# Person class
class Person:
    def __init__(self,humanID, xyz, v,defaultInfectionPercentage):
        self.humanID = humanID
        self.xyz = np.array(xyz)
        self.v = np.array(v)
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
        self.defaultInfectionProbability = defaultInfectionPercentage
        self.meetingCoordinates = ()
        self.meetingRoom = ""
        self.meetingFloor = 0
        self.scatter, = ax.plot([], [], [], marker='', animated=True)

    def makeInfectedByPerson(self):
        self.startInfection = True


    def InfectedDayChecker(self):
        global infectedHumanNumber,healthyHumanNumber
        global ct, timeArray
        if self.startInfection is True and self.alreadyInfected is False and self.dayPassedAfterMeetingInfected >= IncubationVal:
            self.makeInfected()
            infectedHumanNumber = infectedHumanNumber + 1
            ct.append(infectedHumanNumber)
            healthyHumanNumber = HumanCount - infectedHumanNumber
            timeArray.append(currentDay)
            #update(ct, timeArray, infectedHumanNumber, healthyHumanNumber)

            newCase = "Person " + "\n" + str(self.humanID) + "\nwas infected by" + "\nPerson " +str(self.personWhoInfected) + "\ncoordinate: " + str(self.meetingCoordinates)+"\nin room: " + str(self.meetingRoom) + "\n at floor: " + str(self.meetingFloor)  + "\n Day: " + str(currentDay)
            colorText = "red"

            tkinter.Label(frameNew, font=scrollFontSmall, text=newCase, fg=colorText).pack()
            spaceAfter = "------------------------------------"
            tkinter.Label(frameNew, font=scrollFontSmall, text=spaceAfter).pack()
            update(ct, timeArray, infectedHumanNumber, healthyHumanNumber)



    def makeInfected(self):
        self.infected = True
        self.healthy = False
        self.alreadyInfected = True
        self.scatter, = ax.plot([], [], [], color='red', label='Infected person', marker='o',
                                markeredgecolor='black', markeredgewidth=0.5, markersize=5, animated=True)

    def startmovement(self):
        self.pathCounter = 0
        if self.isMoving==False and self.isStoping == False:
            self.makeMover()

    def makeMover(self):
        self.isStoping = False
        self.isMoving = True
        if self.infected:
            self.scatter, = ax.plot([], [], [], color='red', label='Infected person', marker='o',
                                    markeredgecolor='black', markeredgewidth=0.5, markersize=5, animated=True)
        elif self.healthy:
            self.scatter, = ax.plot([], [], [], color='lime', label='Healthy person', marker='o', markeredgecolor='black',
                                markeredgewidth=0.5, markersize=5, animated=True)
        hand, labl = ax.get_legend_handles_labels()
        by_label = dict(zip(labl, hand))
        ax.legend(by_label.values(), by_label.keys())

    def stopMoving(self):
        global humans
        self.isMoving = False
        self.isStoping = True
        self.scatter.set_visible(False)

    def restartmovement(self):
        self.isMoving == False
        self.isStoping == False
        self.pathCounter = 0
        self.makeMover()

    def onWhichFloor(self,currentZ):
        for k, v in floorsAndValues.items():
            if currentZ<= max(v) and currentZ >= min(v):
                return k

    def checker(self):
            currentPointLocation = (self.path[self.pathCounter][0], self.path[self.pathCounter][1])
            for i, myobject in enumerate(GMLOBJ_3D_Objects):
                # checking current room number where the person now is located
                    if myobject.poly_path.contains_point(currentPointLocation):
                        return myobject.id
                    else:
                        pass


    def inCaseOfMeeting(self,eachH):
        # eachH.makeInfected()
        tempObject = Meeting()
        tempObject.meetingCoordinates.append(self.path[self.pathCounter][0])
        tempObject.meetingCoordinates.append(self.path[self.pathCounter][1])
        tempObject.meetingCoordinates.append(self.path[self.pathCounter][2])
        tempObject.floorNumber = int(self.onWhichFloor(self.path[self.pathCounter][2]))
        tempObject.between = [self.humanID,eachH.humanID]
        tempObject.day = currentDay

        valueOfRoomNumber = self.checker()
        tempObject.roomNumber = valueOfRoomNumber
        meetingCase.append(tempObject)
        tempL = (self.path[self.pathCounter][0], self.path[self.pathCounter][1])
        eachH.meetingCoordinates = (tempL)
        eachH.meetingRoom = valueOfRoomNumber
        eachH.meetingFloor = int(self.onWhichFloor(self.path[self.pathCounter][2]))
        newCase = "Infected person" + "\n"+ str(self.humanID) + "\nmet with\n"+ "Healthy person" + "\n"+ str(eachH.humanID) +"\ncoordinate: "+str(tempL) +"\nin room: " + str(tempObject.roomNumber) + "\n at floor: " + str(tempObject.floorNumber) + "\n Day: " +str(currentDay)
        colorText = "darkgoldenrod"

        # with default infection probability the person is infected when meeting
        if random.random() <= self.defaultInfectionProbability:
            eachH.makeInfectedByPerson()
            eachH.infectedDay = currentDay
            eachH.personWhoInfected = self.humanID
        tkinter.Label(frameNew, font=scrollFontSmall, text=newCase, fg=colorText).pack()
        spaceAfter = "------------------------------------"
        tkinter.Label(frameNew, font=scrollFontSmall, text=spaceAfter).pack()


    def meetingProcess(self):
        # if the person is infected
        if self.infected and  self.isMoving is True:
            for i, eachH in enumerate(humans):
                if self.humanID != eachH.humanID:
                    if eachH.healthy and eachH.isMoving is True:
                        if self.onWhichFloor(self.path[self.pathCounter][2]) == eachH.onWhichFloor(eachH.path[eachH.pathCounter][2]):
                            # find the distance between them
                            d = self.getD(eachH.path[eachH.pathCounter][0], eachH.path[eachH.pathCounter][1])
                            if d <= spreadDistance*10:
                                self.inCaseOfMeeting(eachH)


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
            if self.pathCounter>=self.pathSize-1:
                self.stopMoving()
            else:
                self.pathCounter = self.pathCounter + 1
            self.scatterZ(tempVarX,tempVarY,tempVarZ)
        else:
            self.scatter.set_visible(False)

    # scatter method
    def scatterZ(self,tempVarX,tempVarY,tempVarZ):
        self.scatter.set_xdata(tempVarX)
        self.scatter.set_ydata(tempVarY)
        self.scatter.set_3d_properties(tempVarZ)

class program(tkinter.Tk):
    def __init__(self, *args, **kwargs):
        tkinter.Tk.__init__(self, *args, **kwargs)
        thisContainer = tkinter.Frame(self)
        thisContainer.pack(side="top", fill="both", expand=True)
        thisContainer.grid_rowconfigure(0, minsize=300, weight=1)
        thisContainer.grid_columnconfigure(0, minsize=300, weight=1)
        self.allFrames = self.initialization({}, thisContainer)
        self.frames(Menu)

    def initialization(self, frames, thisContainer):
        f = Menu(thisContainer, self)
        frames[Menu] = f
        f.grid(row=0, column=0, sticky='nsew')
        return frames

    def frames(self, j):
        frame = self.allFrames[j]
        frame.tkraise()

# Menu page
class Menu(tkinter.Frame):
    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent)
        label = tkinter.Label(self, text="InCOVID", font=BigFontName)
        label.grid(row=0, padx=5, pady=20)
        entryPath = tkinter.StringVar()
        entry = tkinter.Entry(self, textvariable=entryPath, font=fontName)
        entryPath.set("")
        entry.grid()
        b1 = tkinter.Button(self, text='Select IndoorGML file', font=fontName, relief='raised',
                            command=lambda entryPath=entryPath: self.path(entryPath,'.gml'))
        b1.grid(padx=20, pady=20)
        entryPathSIMOGenData = tkinter.StringVar()
        entry2 = ttk.Entry(self, textvariable=entryPathSIMOGenData, font=fontName)
        entryPathSIMOGenData.set("")
        entry2.grid()
        b2 = tkinter.Button(self, text='Select SIMOGen movement data', font=fontName, relief='raised',
                            command=lambda entryPathSIMOGenData=entryPathSIMOGenData: self.path(entryPathSIMOGenData,'.csv'))
        b2.grid(padx=20, pady=20)
        labelInfectedPeople = tkinter.StringVar()
        labelInfectedPeople.set("Enter the initial number of infected people:")
        labelinfected = tkinter.Label(self, textvariable=labelInfectedPeople, font=fontName, height=2)
        labelinfected.grid()
        numberOfInfected = tkinter.StringVar(None)
        numberOfInfected.set("10")
        numInf = ttk.Entry(self, textvariable=numberOfInfected, font=fontName, width=10)
        numInf.grid()
        labelInfectionPercentage = tkinter.StringVar()
        labelInfectionPercentage.set("Enter the default infection rate:")
        labelInfPercntg = tkinter.Label(self, textvariable=labelInfectionPercentage, font=fontName, height=2)
        labelInfPercntg.grid()
        percentageInfection = tkinter.StringVar(None)
        percentageInfection.set("0.5")
        perInfec = tkinter.Entry(self, textvariable=percentageInfection, font=fontName, width=10)
        perInfec.grid()
        labelSpreadDistance = tkinter.StringVar()
        labelSpreadDistance.set("Enter the threshold distance:")
        labelD = tkinter.Label(self, textvariable=labelSpreadDistance, font=fontName, height=2)
        labelD.grid()
        spreadD = tkinter.StringVar(None)
        spreadD.set("2")
        sD = tkinter.Entry(self, textvariable=spreadD, font=fontName, width=10)
        sD.grid()
        labelIncubationPeriod = tkinter.StringVar()
        labelIncubationPeriod.set("Enter incubation period(days):")
        labelIP = tkinter.Label(self, textvariable=labelIncubationPeriod, font=fontName, height=2)
        labelIP.grid()
        IP = tkinter.StringVar(None)
        IP.set("2")
        IPentry = tkinter.Entry(self, textvariable=IP, font=fontName, width=10)
        IPentry.grid()
        bStart = tkinter.Button(self, text="Start", font=fontName, bg='blue', fg='white',
                        command=lambda self=self, controller=controller,entryPath=entryPath, entryPathSIMOGenData=entryPathSIMOGenData,
                                       numberOfInfected=numberOfInfected, percentageInfection=percentageInfection,
                                       spreadD=spreadD, IP=IP: self.new_window(controller, entryPath, entryPathSIMOGenData, numberOfInfected,
                                                                    percentageInfection, spreadD,IP))

        bStart.grid(padx=30, pady=30)

    def path(self, entryPath, inputType):
            f = tkinter.filedialog.askopenfilename(
                parent=self, initialdir='C:',
                title='Choose file',
                filetypes=[(inputType + ' files', inputType)]
            )
            entryPath.set(str(f))

    def closeFunction(self,controller):
        global humans, infectionCase, floorChanger, infectedHumanNumber, beforeMovementhumans
        humans = []
        beforeMovementhumans = []
        infectionCase = []
        floorChanger = 1
        infectedHumanNumber = 0
        ax.collections.pop()
        ax2D.collections.pop()
        top.destroy()
        controller.frames(Menu)

    def new_window(self, controller, pathGML, pathSIMOGenMovData,numberOfInfected,percentageInfection, spreadD,IP):
        global top
        top = tkinter.Toplevel()
        top.title("Virus propagation model")
        top.attributes('-fullscreen', True)
        global ax, fig, fig2D, ax2D, currentDay, labelDay, IncubationVal
        fig = Figure(figsize=(7, 7), dpi=100, facecolor='#F0F0F0')
        ax = Axes3D(fig,auto_add_to_figure=False)
        fig.add_axes(ax)
        fig2D = Figure(figsize=(4.5, 4.5), dpi=100, facecolor='#F0F0F0')
        ax2D = Axes3D(fig2D,auto_add_to_figure=False)
        fig2D.add_axes(ax2D)
        fig2D.suptitle("Floor " + str(floorChanger) + ":", fontsize=12)
        button1 = Button(top, text="Close", font=fontName, command=lambda self=self, controller = controller: self.closeFunction(controller))
        button1.pack(padx=10, pady=10)
        allPoints = []
        allObjects = []
        allPointsDoors = []
        allObjectsDoors = []
        global spreadDistance
        spreadDistance = float(spreadD.get())
        IncubationVal = int(IP.get())
        # scaling by 1/150
        spreadDistance = spreadDistance / 150
        # parsing indoor gml data
        myGML_3D(pathGML.get())
        gettingData(pathSIMOGenMovData.get())
        global canvas1, frame_top, canvas, canvas2D, frameNew
        canvas1 = tkinter.Canvas(top, highlightbackground="black", highlightcolor="black", highlightthickness=1)
        canvas1.pack(padx=20, pady=20, expand=True, fill="both", side="right")
        frame_top = tkinter.Frame(top, highlightbackground="black", highlightcolor="black", highlightthickness=1)
        frame_top.pack(side="top", padx=5, pady=5)
        varNew = StringVar()
        labelNew = Label(frame_top, textvariable=varNew, font=('Arial', 16), relief=FLAT)
        varNew.set("Virus propagation model in Indoor space")
        labelNew.pack(side="top", padx=10, pady=10)
        labelDay = tkinter.StringVar()
        labelDay.set("Day: "+str(currentDay))
        main_label = tkinter.Label(frame_top, textvariable=labelDay, font=('Arial 14 bold'))
        main_label.pack(side="top", padx=5, pady=10)
        frame_bottom = tkinter.Frame(frame_top)
        frame_bottom.pack(side="bottom", padx=5, pady=5)
        canvas = FigureCanvasTkAgg(fig, master=frame_top)
        canvas.get_tk_widget().pack(side="left", padx=5, pady=5)
        canvas.mpl_connect('button_press_event', ax.axes._button_press)
        canvas.mpl_connect('button_release_event', ax.axes._button_release)
        canvas.mpl_connect('motion_notify_event', ax.axes._on_move)
        global HumanCount, infectedHumanNumber, healthyHumanNumber
        HumanCount = len(id_arr)
        # creating objects by assigning their id's from csv file
        for ival, i in enumerate(np.arange(0, HumanCount)):
            xyz = np.random.rand(1, 1)[0]
            v = np.random.rand(1, 1)[0] * 0.1
            regularHuman = Person(i, xyz, v, float(percentageInfection.get()))
            regularHuman.humanID = id_arr[i]
            humans.append(regularHuman)
            beforeMovementhumans.append(regularHuman)
        # adding path,start and end time to each person
        for ival, h in enumerate(humans):
            for ival2, i in enumerate(range(len(idWithCoord))):
                if h.humanID == idWithCoord[i][0]:
                    temporary = [idWithCoord[i][1], idWithCoord[i][2], idWithCoord[i][3] + 2.5]
                    h.path.append(temporary)
                    updatedStartTime = iso8601.parse_date(idWithCoord[i][4])
                    updatedEndTime = iso8601.parse_date(idWithCoord[i][5])
                    h.startT.append(updatedStartTime)
                    h.endT.append(updatedEndTime)
        timeStartAll = []

        timeAll = []
        # adding the size of the path to each person
        for i, h in enumerate(humans):
            h.pathSize = int(len(h.path))
            timeStartAll.append(h.startT[0])
            timeAll.append(h.startT)
            timeAll.append(h.endT)

        startOfMovementTime = min(timeStartAll)
        for i, h in enumerate(humans):
            for j in range(len(h.endT)):
                difference = h.endT[j] - startOfMovementTime
                h.timeline.append(difference.seconds)

        for i, h in enumerate(humans):
            h.timeline = list(dict.fromkeys(h.timeline))
            h.timeline.sort()

        secondFrame = tkinter.Frame(frame_top, highlightbackground="black", highlightcolor="black",
                                    highlightthickness=1)
        canvasScroll = tkinter.Canvas(secondFrame)
        scrollbar = tkinter.Scrollbar(secondFrame, orient="vertical", command=canvasScroll.yview)
        frameNew = tkinter.Frame(canvasScroll)
        frameNew.bind(
            "<Configure>",
            lambda e: canvasScroll.configure(
                scrollregion=canvasScroll.bbox("all")
            )
        )
        canvasScroll.create_window((0, 0), window=frameNew)
        canvasScroll.configure(yscrollcommand=scrollbar.set)
        tkinter.Label(frameNew, font=scrollFontBig, text="Events log").pack()
        tkinter.Label(frameNew, font=scrollFontBig, text="--------------------------").pack()
        numberInfectedFromEntry = int(numberOfInfected.get())
        for ival, i in enumerate(range(numberInfectedFromEntry)):
            humans[i].makeInfected()
            initalCase = "Person " + str(humans[i].humanID) +  "\nis infected"
            tkinter.Label(frameNew, font=scrollFontSmall, text=initalCase).pack()
            infectedHumanNumber = infectedHumanNumber + 1
        healthyHumanNumber = HumanCount - infectedHumanNumber
        secondFrame.pack(padx=5, pady=5)

        buttonVisualize = tkinter.Button(secondFrame, text="Visualize" , font=fontName,
                                 command=lambda pathGML=pathGML: visualize())
        buttonVisualize.pack(padx=10, pady=1, side="left")


        canvasScroll.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        thirdFrame = tkinter.Frame(frame_top, highlightbackground="black", highlightcolor="black", highlightthickness=1)
        tkinter.Label(thirdFrame, font=scrollFontBig, text="Infection case coordinates in each floor").pack(padx=3,
                                                                                                            pady=3)
        canvas2D = FigureCanvasTkAgg(fig2D, master=thirdFrame)
        thirdFrame.pack(padx=5, pady=5)
        canvas2D.get_tk_widget().pack(side="bottom", expand=True, padx=5, pady=10)
        canvas2D.mpl_connect('button_press_event', ax2D.axes._button_press)
        canvas2D.mpl_connect('button_release_event', ax2D.axes._button_release)
        canvas2D.mpl_connect('motion_notify_event', ax2D.axes._on_move)

        for k, v in floorsAndValues.items():
            if k:
                floorNumber = k
                buttonF = tkinter.Button(thirdFrame, text="Floor"+str(k), font=fontName,
                                          command=lambda floorNumber=floorNumber: drawerByFloor(floorNumber))
                buttonF.pack(padx=10, pady=1, side="left")

        global ct, timeArray
        ct = [infectedHumanNumber]
        timeArray = [0]
        global f, c
        f = plt.figure(figsize=(6, 4))
        c = f.add_subplot(1, 1, 1)
        c.axis([0, 5, 0, HumanCount])
        caja = plt.Rectangle((0, 0), 100, 100, fill=True)
        cvst, = c.plot(infectedHumanNumber, color="red", label="Infected people")
        c.legend(handles=[cvst])
        c.set_xlabel("Time (days)")
        c.set_ylabel("New infections")
        global myPie, axPie
        dataProportion = np.array([healthyHumanNumber, infectedHumanNumber])
        # Creating pie
        myPie, axPie = plt.subplots(figsize=(6, 6))
        axPie.pie(dataProportion, autopct=lambda val: updaterOfValuesAndPercentage(val, dataProportion),
                  explode=explode, labels=labelCondition, shadow=True, colors=colors, wedgeprops=wedgeProp)
        # setting the dimesions
        ax.set_xlim3d([0.0, max(highAndLowX)])
        ax.set_ylim3d([0.0, max(highAndLowY)])
        ax.set_zlim3d([0.0, max(highAndLowZ)])
        ax.set_box_aspect((max(highAndLowX), max(highAndLowY), max(highAndLowZ)))
        ax2D.set_xlim3d([0.0, max(highAndLowX)])
        ax2D.set_ylim3d([0.0, max(highAndLowY)])
        ax2D.set_zlim3d([0.0, max(highAndLowZ)])
        ax2D.set_box_aspect((max(highAndLowX), max(highAndLowY), max(highAndLowZ)))
        try:
            ax.set_aspect('equal')
        except NotImplementedError:
            pass
        allPoints2D = []
        allObjects2D = []
        allPoints2D_Doors = []
        allObjects2D_Doors = []
        global myTime, var1, var2, var3, label1, label2, label3
        var1 = StringVar()
        label1 = Label(canvas1, textvariable=var1, font=('Arial', 14), relief=FLAT)
        var1.set("Total number of people: " + str(HumanCount))
        label1.pack(side="top", padx=5, pady=5)
        var2 = StringVar()
        label2 = Label(canvas1, textvariable=var2, font=('Arial', 14), relief=FLAT)
        var2.set("Number of infected people: " + str(infectedHumanNumber))
        label2.pack(side="top", padx=5, pady=5)
        labelNew = Label(canvas1, justify='center')
        labelNew.pack()
        Graph(canvas1, f).pack(side="bottom", padx=10, pady=10)
        Graph(canvas1, myPie).pack(side="bottom", padx=10, pady=10)
        alphaVal = 0.1
        lineWidthVal = 0.17
        alphaVal2 = 0.5
        lineWidthVal2 = 1
        drawer(ax, allPoints, allPointsDoors, allObjects, allObjectsDoors, True, alphaVal, lineWidthVal, alphaVal2,
               lineWidthVal2, False, 0)

        alphaVal = 0.7
        lineWidthVal = 1
        alphaVal2 = 0.7
        drawer(ax2D, allPoints2D, allPoints2D_Doors, allObjects2D, allObjects2D_Doors, False, alphaVal, lineWidthVal,
               alphaVal2, lineWidthVal2, False, 0)
        ax.set_axis_off()
        ax2D.set_axis_off()
        ax2D.view_init(90)
        canvas.draw()
        canvas2D.draw()
        global anim, anim2D
        anim = FuncAnimation(fig, updateALL, frames=frameN, interval=0, blit=True, repeat=True)
        buttonPausingMov = tkinter.Button(frame_bottom, text="Pause simulation", bg='brown', fg='white', font=fontName,
                                          command=lambda anim=anim: pauseAnimation(anim))
        buttonPausingMov.pack(padx=5, pady=5, side="left")
        buttonStartingMov = tkinter.Button(frame_bottom, text="Continue simulation", bg='green', fg='white',
                                           font=fontName, command=lambda anim=anim: continueAnimation(anim))
        buttonStartingMov.pack(padx=5, pady=5, side="left")


def main():
    app = program()
    app.mainloop()

if __name__ == "__main__":
    main()