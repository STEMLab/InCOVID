import tkinter
from tkinter import ttk
import tkinter.filedialog
from src import gmlParser
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from src.InpReader import getData
from src.MovingObject import MovingObject
from src.constants import *
from src.gmlParser import *
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import networkx as nx
from datetime import timedelta, datetime, date, time

humansCountInfected = []
locationHealthy = []
locationInfected = []
diff = 0
timeController = 0
newObjectsList = []
first = []
notMovingOvbjectsList = []
movingObjectsList = []
sometime = time(8, 50)  # 8:50am
newTime = time(8,50) # 8:50am
globalTime = 0
humans = []
IncubationVal = 0
infectionCase = []
floorChanger = 1
infectedHumanNumber = 0
currentDay = 1
currentTime = 0
timeIncreaser = 0
meetingCase = []
valX=[]
valY=[]
valZ=[]

#Meeting class
class Meeting:
    def __init__(self):
        self.id = 0
        self.between = []
        self.meetingCoordinates = []
        self.floorNumber = 1
        self.roomNumber = 0
        self.day = 0
        self.scatter, = ax2D.plot([], [], [], color='yellow', label='Meeting with infected person case', marker='p', markeredgecolor='black',markeredgewidth=0.6, markersize=6, animated=True)
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
def drawer(ax,allPoints,allPointsDoors,allObjects,allObjectsDoors,v3d,alphaVal,lineWidthVal,FloorCheck,floorN):
    newlist =[]
    newlistDoors = []
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
        for ival2, i in enumerate((range(len(object.allPos)))):
            temp = [object.allPos[i][0], object.allPos[i][1], object.allPos[i][2]]
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
            allObjectsDoors, allPointsDoors= drawEachDoor(myobject, allPointsDoors, allObjectsDoors)
    for i in range(len(allObjects)):
            for j in range(len(allObjects[i])):
                    newlist.append(allObjects[i][j])
            newlist.append([np.nan,np.nan,np.nan])
    inputList = [newlist]
    for i in range(len(allObjectsDoors)):
            for j in range(len(allObjectsDoors[i])):
                    newlistDoors.append(allObjectsDoors[i][j])
            newlistDoors.append([np.nan,np.nan,np.nan])
    inputListDoors = [newlistDoors]
    #fininputList = inputList+inputListDoors
    fininputList = inputList
    thisIndoor = ax.add_collection3d(Poly3DCollection(fininputList, edgecolors='k', alpha=alphaVal,
                                                      linewidth=lineWidthVal))

# function for updating the values and the percentage in the pie chart
def updaterOfValuesAndPercentage(this, thisValues):
    output = int(this / 99.999*np.sum(thisValues))
    return "{:.1f}%\n({:d})".format(this, output)

# function for updating graph, pie chart, and label values
def update(ct, timeArray, infectedHumanNumber,healthPersonNumber):
        c.clear()
        ct.append(infectedHumanNumber)
        timeArray.append(currentDay)
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

# function for drawing specific floor
def drawerByFloor(floorN):
    global allPoints2D, allObjects2D, allPoints2D_Doors, allObjects2D_Doors
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
    drawer(ax2D, allPoints2D,allPoints2D_Doors, allObjects2D, allObjects2D_Doors, False, alphaVal,lineWidthVal,True,floorChanger)

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


# for visualization infection cases
# TODO: update the function
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
                        if humans[i].humanID == j.between[0] and humans[i2].humanID == j.between[1]:
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

# continue animation function
def continueAnimation(anim):
    anim.event_source.start()

# pause animation function
def pauseAnimation(anim):
    anim.event_source.stop()



# program class
class program(tkinter.Tk):
    def __init__(self, *args, **kwargs):
        tkinter.Tk.__init__(self, *args, **kwargs)
        thisContainer = tkinter.Frame(self)
        thisContainer.pack(side="top", fill="both", expand=True)
        thisContainer.grid_rowconfigure(0, minsize=300, weight=1)
        thisContainer.grid_columnconfigure(0, minsize=300, weight=1)
        self.allFrames = self.initialization({}, thisContainer)
        self.frames(Menu)

    #method for initialization
    def initialization(self, frames, thisContainer):
        f = Menu(thisContainer, self)
        frames[Menu] = f
        f.grid(row=0, column=0, sticky='nsew')
        return frames
    # for frames
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
        b1 = tkinter.Button(self, text='Select IndoorGML file', font=fontName, relief='raised',command=lambda entryPath=entryPath: self.path(entryPath,'.gml'))
        b1.grid(padx=20, pady=20)
        entryPathSIMOGenData = tkinter.StringVar()
        entry2 = ttk.Entry(self, textvariable=entryPathSIMOGenData, font=fontName)
        entryPathSIMOGenData.set("")
        entry2.grid()
        b2 = tkinter.Button(self, text='Select SIMOGen movement data', font=fontName, relief='raised',command=lambda entryPathSIMOGenData=entryPathSIMOGenData: self.path(entryPathSIMOGenData,'.csv'))
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
        labelIncubationPeriod.set("Enter the incubation period(days):")
        labelIP = tkinter.Label(self, textvariable=labelIncubationPeriod, font=fontName, height=2)
        labelIP.grid()
        IP = tkinter.StringVar(None)
        IP.set("2")
        IPentry = tkinter.Entry(self, textvariable=IP, font=fontName, width=10)
        IPentry.grid()

        bGenerate = tkinter.Button(self, text="Generate", font=fontName, bg='green', fg='white',
                        command=lambda self=self, controller=controller,entryPath=entryPath, entryPathSIMOGenData=entryPathSIMOGenData,
                                       numberOfInfected=numberOfInfected, percentageInfection=percentageInfection,
                                       spreadD=spreadD, IP=IP: self.generate(controller, entryPath, entryPathSIMOGenData, numberOfInfected,
                                                                    percentageInfection, spreadD,IP))
        bGenerate.grid(padx=30, pady=15)


        bViz = tkinter.Button(self, text="Visualize", font=fontName, bg='blue', fg='white',
                        command=lambda self=self, controller=controller,entryPath=entryPath, entryPathSIMOGenData=entryPathSIMOGenData,
                                       numberOfInfected=numberOfInfected, percentageInfection=percentageInfection,
                                       spreadD=spreadD, IP=IP: self.visualizeVP(controller, entryPath, entryPathSIMOGenData, numberOfInfected,
                                                                    percentageInfection, spreadD,IP))
        bViz.grid(padx=30, pady=15)



    # for generating data
    def generate(self, controller, pathGML, pathSIMOGenMovData, numberOfInfected,percentageInfection, spreadD, IP):
        import struct
        print("python is ")
        print(struct.calcsize("P") * 8)
        print("Reading GML")
        myGML_3D(pathGML.get())
        print("start reading csv")
        import time
        now = time.time()
        global diff
        listDF, timeStart, timeEnd, diff = getData(pathSIMOGenMovData.get())

        spreadDistance = float(spreadD.get())
        print("finished reading csv")
        timeDiff = int(time.time() - now)
        print("TIME SPENT:")
        print(timeDiff)
        print("total number of people")
        print(len(listDF))
        print("start creating objects")
        now = time.time()
        for i, ival in enumerate(listDF):
            if i < (len(listDF)):
                listT = listDF[i].values.tolist()
                regularHuman = MovingObject(listT[0][0], listT[1][5])
                regularHuman.startTime = datetime.strptime(listDF[i]['startTime'].values[0], "%Y-%m-%dT%H:%M:%SZ")
                regularHuman.endTime = datetime.strptime(listDF[i]['startTime'].values[-1], "%Y-%m-%dT%H:%M:%SZ")
                regularHuman.path = listDF[i]['startCoord']
                temp = listDF[i]['startCoord'].str.split(" ")
                regularHuman.path = [[float(j) for j in i] for i in temp]
                humans.append(regularHuman)
                del listT
                i += 1
            else:
                pass
        print("finished creating objects")
        print("TIME SPENT:")
        timeDiff = int(time.time() - now)
        print(timeDiff)
        print("FINISH")
        print("start time min")
        print(timeStart)
        print("end time max")
        print(timeEnd)
        start_date = timeStart

        end_date = timeEnd
        delta = timedelta(seconds=1)

        infectedHumanNumber = int(numberOfInfected.get())

        dataToCSVInfection = []
        for i in range(infectedHumanNumber):
            humans[i].makeInfected()
            dataToCSVInfection.append([humans[i].id, 1])
            print("make initial infected")

        notMovingOvbjectsList = humans.copy()
        movingObjectsList = []

        import numpy as np

        global humansCountInfected
        now = time.time()
        colorsInfectedOrHealthy = []
        start_date2 = start_date
        initialStart_date = start_date

        day = 0

        print("Moving process start")

        import csv
        dataToCSV = []
        header = ['MovingObjectID', 'InfectedMovingObjectID', 'meeting_coordinate', 'meeting_room', 'meeting_day']

        headerInfection = ['InitandNewInfectedMovingObjectID', 'infected_day']
        for day in range(10):
            print("DAY " + str(day + 1))
            while start_date <= end_date:
                if len(notMovingOvbjectsList) >= 0:
                    for i, ival in enumerate(notMovingOvbjectsList):
                        if ival.startTime == start_date:
                            ival.isMoving = True
                            movingObjectsList.append(ival)
                            notMovingOvbjectsList.remove(ival)
                if len(movingObjectsList) >= 0:
                    # prev_obj = None
                    for j, jval in enumerate(movingObjectsList):
                        # print("None value")
                        if (jval.iterator >= len(jval.path)):
                            jval.isMoving = False
                            # if jval in movingObjectsList:
                            movingObjectsList.remove(jval)
                            notMovingOvbjectsList.append(jval)
                        else:
                            if jval.isInfected:
                                for j2, jval2 in enumerate(movingObjectsList):
                                    if jval2.id != jval.id and jval2.isHealthy and jval2.iterator < len(jval2.path):
                                        jval.currentFloor = jval.onWhichFloor(jval.path[jval.iterator][2])
                                        jval2.currentFloor = jval2.onWhichFloor(
                                            jval2.path[jval2.iterator][2])
                                        # check whether moving objects at the same floor
                                        if jval.currentFloor == jval2.currentFloor:
                                            valueOfRoomNumber = jval.checker()
                                            valueOfRoomNumber2 = jval2.checker()
                                            # check whether moving objects at the same room
                                            if valueOfRoomNumber == valueOfRoomNumber2:
                                                # find the distance between them
                                                d = jval.getD(jval2.path[jval2.iterator][0],
                                                              jval2.path[jval2.iterator][1])
                                                if d <= spreadDistance:
                                                    jval.inCaseOfMeeting(jval2, day + 1)
                                                    if [jval2.id, jval.id, jval2.path[jval2.iterator],
                                                        valueOfRoomNumber, day + 1] not in dataToCSV:
                                                        dataToCSV.append([jval2.id, jval.id, jval2.path[jval2.iterator],
                                                                          valueOfRoomNumber, day + 1])
                        jval.iterator += 1
                else:
                    pass
                start_date += delta
                print("time left of Day " + str(day + 1) + ":")
                print(str((end_date - start_date).total_seconds()))
            for ival, h in enumerate(notMovingOvbjectsList):
                if h.startInfection == True and h.alreadyInfected == False:
                    h.dayPassedAfterMeetingInfected += 1
                    h.InfectedDayChecker()
                    if h.becameNewInfected == True:
                        dataToCSVInfection.append([h.id, day + 1])

                h.iterator = 0
            start_date = initialStart_date
            currentDay = day + 1

            countInfected = 0
            global humansCountInfected
            humansCountInfected = notMovingOvbjectsList + movingObjectsList
            for i in range(len(humansCountInfected)):
                if (humansCountInfected[i].isInfected == True):
                    countInfected += 1
            print("final results is: ")
            print(countInfected)


            if countInfected >= 0.9 * len(humansCountInfected):
                print("finish infected")
                break

        with open('meetingWithInfectedPerson.csv', 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)

            # write the header
            writer.writerow(header)

            # write multiple rows
            writer.writerows(dataToCSV)

        with open('InfectionTimeline.csv', 'w', encoding='UTF8', newline='') as f2:
            writer = csv.writer(f2)

            # write the header
            writer.writerow(headerInfection)

            # write multiple rows
            writer.writerows(dataToCSVInfection)



    # returns the path of file
    def path(self, entryPath, inputType):
            f = tkinter.filedialog.askopenfilename(
                parent=self, initialdir='C:',
                title='Choose file',
                filetypes=[(inputType + ' files', inputType)]
            )
            entryPath.set(str(f))

    # close function
    def closeFunction(self, controller):
            global humans, infectionCase, floorChanger, infectedHumanNumber
            humans = []
            infectionCase = []
            floorChanger = 1
            infectedHumanNumber = 0
            if len(ax.collections) > 0:
                ax.collections.pop()
            else:
                pass
            top.destroy()
            controller.frames(Menu)

        # for generating data
    def visualizeVP(self, controller, pathGML, pathSIMOGenMovData, numberOfInfected, percentageInfection, spreadD, IP):
            listDF, timeStart, timeEnd, diff = getData(pathSIMOGenMovData.get())
            global top, spreadDistance, frameNew, ax, fig, fig2D, ax2D, currentDay, labelDay, IncubationVal, currentTime, labelTime, timeIncreaser, var2, label2, HumanCount, infectedHumanNumber, healthyHumanNumber, newObjectsList, initialStartDate
            top = tkinter.Toplevel()
            top.title("Virus propagation model")
            top.attributes('-fullscreen', True)
            button1 = tkinter.Button(top, text="Close", font=fontName,
                                     command=lambda self=self, controller=controller: self.closeFunction(controller))
            button1.pack(padx=1, pady=1)
            fig = Figure(figsize=(6, 6), dpi=150, facecolor='#F0F0F0')
            ax = Axes3D(fig, auto_add_to_figure=False)
            fig.add_axes(ax)
            fig2D = Figure(figsize=(5, 5), dpi=100, facecolor='#F0F0F0')
            ax2D = Axes3D(fig2D, auto_add_to_figure=False)
            fig2D.add_axes(ax2D)
            fig2D.suptitle("Floor " + str(floorChanger) + ":", fontsize=12)
            spreadDistance = float(spreadD.get())
            IncubationVal = int(IP.get())
            # parsing indoor gml data
            myGML_3D(pathGML.get())
            listDF, timeStart, timeEnd, increasetime = getData(pathSIMOGenMovData.get())
            canvas1 = tkinter.Canvas(top, highlightbackground="black", highlightcolor="black", highlightthickness=1)
            canvas1.pack(padx=5, pady=5, expand=True, fill="both", side="right")
            frame_top = tkinter.Frame(top, highlightbackground="black", highlightcolor="black", highlightthickness=1)
            frame_top.pack(side="top", padx=1, pady=1)
            varNew = tkinter.StringVar()
            labelNew = tkinter.Label(frame_top, textvariable=varNew, font=('Arial', 16))
            varNew.set("Virus propagation model in Indoor space")
            labelNew.pack(side="top", padx=5, pady=5)
            labelDay = tkinter.StringVar()
            labelDay.set("Day: " + str(currentDay))
            main_label = tkinter.Label(frame_top, textvariable=labelDay, font=('Arial 14 bold'))
            main_label.pack(side="top", padx=5, pady=1)
            labelTime = tkinter.StringVar()
            labelTime.set("Time: " + str(sometime))
            main_labelTime = tkinter.Label(frame_top, textvariable=labelTime, font=('Arial 14 bold'))
            main_labelTime.pack(side="top", padx=5, pady=1)
            frame_bottom = tkinter.Frame(frame_top)
            frame_bottom.pack(side="bottom", padx=5, pady=1)
            canvas = FigureCanvasTkAgg(fig, master=frame_top)
            canvas.get_tk_widget().pack(side="left", padx=5, pady=1)
            canvas.mpl_connect('button_press_event', ax.axes._button_press)
            canvas.mpl_connect('button_release_event', ax.axes._button_release)
            canvas.mpl_connect('motion_notify_event', ax.axes._on_move)

            secondFrame = tkinter.Frame(frame_top, highlightbackground="black", highlightcolor="black",
                                        highlightthickness=1)
            canvasScroll = tkinter.Canvas(secondFrame)
            scrollbar = tkinter.Scrollbar(secondFrame, orient="vertical", command=canvasScroll.yview)
            frameNew = tkinter.Frame(canvasScroll)
            frameNew.bind("<Configure>", lambda e: canvasScroll.configure(scrollregion=canvasScroll.bbox("all")))
            canvasScroll.create_window((0, 0), window=frameNew)
            canvasScroll.configure(yscrollcommand=scrollbar.set)
            tkinter.Label(frameNew, font=scrollFontBig, text="Events log").pack()
            tkinter.Label(frameNew, font=scrollFontBig, text="--------------------------").pack()


            infectedHumanNumber = int(numberOfInfected.get())
            print("start time min")
            print(timeStart)
            print("end time max")
            print(timeEnd)
            start_date = timeStart
            initialStartDate = timeStart
            end_date = timeEnd
            delta = timedelta(seconds=1)
            secondFrame.pack(padx=5, pady=5)
            buttonVisualize = tkinter.Button(secondFrame, text="Visualize", font=fontName,
                                             command=lambda pathGML=pathGML: visualize())
            buttonVisualize.pack(padx=10, pady=1, side="left")
            canvasScroll.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            thirdFrame = tkinter.Frame(frame_top, highlightbackground="black", highlightcolor="black",
                                       highlightthickness=1)
            tkinter.Label(thirdFrame, font=scrollFontBig, text="Infection case coordinates in each floor").pack(padx=1,
                                                                                                                pady=1)
            canvas2D = FigureCanvasTkAgg(fig2D, master=thirdFrame)
            thirdFrame.pack(padx=1, pady=1)
            fourthFrame = tkinter.Frame(thirdFrame, highlightbackground="black", highlightcolor="black",
                                        highlightthickness=1)
            fourthFrame.pack(side="left", padx=1, pady=1)
            canvas2D.get_tk_widget().pack(side="bottom", expand=True, padx=1, pady=1)
            canvas2D.mpl_connect('button_press_event', ax2D.axes._button_press)
            canvas2D.mpl_connect('button_release_event', ax2D.axes._button_release)
            canvas2D.mpl_connect('motion_notify_event', ax2D.axes._on_move)



            locationInfected = []
            locationHealthy = []

            for i, ival in enumerate(listDF):
                if i < (len(listDF)):
                    listT = listDF[i].values.tolist()
                    regularHuman = MovingObject(listT[0][0], listT[1][5])
                    regularHuman.startTime = datetime.strptime(listDF[i]['startTime'].values[0], "%Y-%m-%dT%H:%M:%SZ")
                    regularHuman.endTime = datetime.strptime(listDF[i]['startTime'].values[-1], "%Y-%m-%dT%H:%M:%SZ")
                    regularHuman.path = listDF[i]['startCoord']
                    temp = listDF[i]['startCoord'].str.split(" ")
                    regularHuman.path = [[float(j) for j in i] for i in temp]
                    humans.append(regularHuman)
                    del listT
                    i += 1
                else:
                    pass

            listOfTime = []
            end_date = timeEnd
            delta = timedelta(seconds=1)
            daystotalPassed = 1
            for dayThis in range(daystotalPassed):
                start_date2 = timeStart
                for ii, ival in enumerate(humans):
                    humans[ii].iterator2 = 0
                while start_date2 <= end_date:
                    for ii, ival in enumerate(humans):
                        if humans[ii].startTime <= start_date2 and humans[
                            ii].endTime >= start_date2 and humans[ii].iterator2 < len(
                            humans[ii].path):
                            x = humans[ii].path[humans[ii].iterator2][0]
                            y = humans[ii].path[humans[ii].iterator2][1]
                            z = humans[ii].path[humans[ii].iterator2][2]
                            if humans[ii].isInfected == True:
                                locationInfected.append([x, y, z])
                                locationHealthy.append([np.nan, np.nan, np.nan])
                            else:
                                locationHealthy.append([x, y, z])
                                locationInfected.append([np.nan, np.nan, np.nan])
                            humans[ii].iterator2 += 1
                        else:
                            locationInfected.append([np.nan, np.nan, np.nan])
                            locationHealthy.append([np.nan, np.nan, np.nan])
                    start_date2 += delta

            t = np.array([np.ones(len(humans)) * i for i in range(daystotalPassed*(diff + 1))], dtype=np.uint32).flatten()

            import matplotlib.animation
            import pandas as pd
            from cycler import cycler

            coord = np.array(locationHealthy, dtype=np.float32)
            coordInfected = np.array(locationInfected, dtype=np.float32)

            df = pd.DataFrame(
                {"time": t, "x": coord[:, 0], "y": coord[:, 1], "z": coord[:, 2], "xInfected": coordInfected[:, 0],
                 "yInfected": coordInfected[:, 1], "zInfected": coordInfected[:, 2]})

            thisColors = np.linspace(0, 1, len(humans)*(diff+1))
            print("this color length")
            print(len(thisColors))
            print("length of t")
            print(len(t))
            data = df[df['time'] == 0]

            graph, = ax.plot(data.x, data.y, data.z, c='green', marker='o', linestyle="",
                             markeredgecolor='black', markeredgewidth=0.5, markersize=4,label="Healthy moving object")
            new, = ax.plot(data.xInfected, data.yInfected, data.zInfected, color='red', marker='o', linestyle="",
                           markeredgecolor='black', markeredgewidth=0.5, markersize=4, label = "Infected moving object")
            # ax.set_prop_cycle(cycler('color', ['c', 'm', 'y', 'k']))

            timeIncreaser = 39600/(diff + 1)
            def animate(t):
                global  sometime, newTime, currentDay ,labelDay,labelTime,sometime
                global timeController
                data = df[df['time'] == t]
                graph.set_data(data.x, data.y)
                graph.set_3d_properties(data.z)
                new.set_data(data.xInfected, data.yInfected)
                new.set_3d_properties(data.zInfected)


                if timeController>(diff+1):

                    # print("run first")
                    currentDay+=1
                    labelDay.set("Day: " + str(currentDay))
                    sometime = time(8, 50)  # 8:50am
                    labelTime.set("Time: " + str(sometime))
                    #labelTime.set("Time: " + str(newTime.strftime("%H:%M:%S")))
                    timeController = 0
                else:
                    # print("run second")
                    newTime = (datetime.combine(date.today(), sometime) + timedelta(seconds=timeIncreaser)).time()
                    sometime = newTime
                    labelTime.set("Time: " + str(newTime.strftime("%H:%M:%S")))
                    timeController += 1

                return graph, new

            allPoints = []
            allPointsDoors = []
            allObjects = []
            allObjectsDoors = []

            allPoints2D = []
            allPoints2D_Doors = []
            allObjects2D = []
            allObjects2D_Doors = []
            lineWidthVal = []
            alphaVal = 0.3
            lineWidthVal = 0.05
            drawer(ax, allPoints, allPointsDoors, allObjects, allObjectsDoors, True, alphaVal, lineWidthVal, False,0)
            ax.set_axis_off()
            ax.set_xlim3d([0, max(highAndLowX)])
            ax.set_ylim3d([0, max(highAndLowY)])
            ax.set_zlim3d([0, max(highAndLowZ)])
            ax.set_box_aspect((max(highAndLowX), max(highAndLowY), max(highAndLowZ)))
            try:
                ax.set_aspect('equal')
            except NotImplementedError:
                pass
            ax.legend(loc="best")
            global animation

            HumanCount = len(humans)

            # create button for each floor
            for k, v in floorsAndValues.items():
                if k:
                    floorNumber = k
                    buttonF = tkinter.Button(fourthFrame, text="Floor" + str(k), font=fontName,
                                             command=lambda floorNumber=floorNumber: drawerByFloor(floorNumber))
                    buttonF.pack(side="top", fill="x", padx=10, pady=1)

            var1 = tkinter.StringVar()
            label1 = tkinter.Label(canvas1, textvariable=var1, font=('Arial', 14))
            var1.set("Total number of people: " + str(HumanCount))
            label1.pack(side="top", padx=5, pady=5)
            var2 = tkinter.StringVar()
            label2 = tkinter.Label(canvas1, textvariable=var2, font=('Arial', 14))
            var2.set("Number of infected people: " + str(infectedHumanNumber))
            label2.pack(side="top", padx=5, pady=5)
            labelNew = tkinter.Label(canvas1, justify='center')
            labelNew.pack()
            alphaVal = 0.3
            lineWidthVal = 0.05
            lineWidthVal2 = 0.0
            alphaVal = 0.7
            lineWidthVal = 1
            drawer(ax2D, allPoints2D, allPoints2D_Doors, allObjects2D, allObjects2D_Doors, False, alphaVal,
                   lineWidthVal, False, 0)
            ax.set_axis_off()
            ax2D.set_axis_off()
            ax2D.view_init(90)
            global ct, timeArray, f, c, axPie
            ct = [infectedHumanNumber, infectedHumanNumber]
            timeArray = [0, currentDay]
            f = plt.figure(figsize=(5, 4))
            c = f.add_subplot(1, 1, 1)
            c.axis([1, 20, 0, HumanCount])
            caja = plt.Rectangle((0, 0), 100, 100, fill=True)
            cvst, = c.plot(infectedHumanNumber, color="red", label="Infected people")
            c.legend(handles=[cvst])
            c.set_xlabel("Time (days)")
            c.set_ylabel("Infections")
            healthyHumanNumber = len(humans)-infectedHumanNumber
            dataProportion = np.array([healthyHumanNumber, infectedHumanNumber])
            # Creating pie
            myPie, axPie = plt.subplots(figsize=(5, 5))
            axPie.pie(dataProportion, autopct=lambda val: updaterOfValuesAndPercentage(val, dataProportion),
                      explode=explode, labels=labelCondition, shadow=True, colors=colors, wedgeprops=wedgeProp)
            update(ct, timeArray, infectedHumanNumber, healthyHumanNumber)
            Graph(canvas1, f).pack(side="bottom", padx=5, pady=5)
            Graph(canvas1, myPie).pack(side="bottom", padx=5, pady=5)
            canvas.draw()
            canvas2D.draw()


            animation = matplotlib.animation.FuncAnimation(fig, animate, daystotalPassed*(diff + 1), interval=0.0001, blit=True, repeat=True)
            # plt.draw()
            buttonPausingMov = tkinter.Button(frame_bottom, text="Pause simulation", bg='brown', fg='white',
                                              font=fontName, command=lambda animation=animation: pauseAnimation(animation))
            buttonPausingMov.pack(padx=2, pady=2, side="left")
            buttonStartingMov = tkinter.Button(frame_bottom, text="Continue simulation", bg='green', fg='white',
                                               font=fontName, command=lambda animation=animation: continueAnimation(animation))
            buttonStartingMov.pack(padx=2, pady=2, side="left")


# main function
def main():
    app = program()
    app.mainloop()

if __name__ == "__main__":
    main()

