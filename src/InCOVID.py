import tkinter
from tkinter import ttk
import tkinter.filedialog
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation
from src import gmlParser
from src.constants import *
from src.gmlParser import *
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import networkx as nx
from sklearn.neighbors import NearestNeighbors
from scipy.spatial import distance
import matplotlib.animation
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import time as clock
from datetime import timedelta, datetime, date, time
from src.InpReader import getData
from src.MovingObject import MovingObject
from src.gmlParser import myGML_3D


matplotlib.use('agg')

totalTime = 0
IncubationVal = 0
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
infectionCase = []
floorChanger = 1
infectedHumanNumber = 0
currentDay = 0
currentTime = 0
timeIncreaser = 0
meetingCase = []
valX=[]
valY=[]
valZ=[]
allInfected = []
eachDayInfected = []
totalDays = 0

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


# function for updating graph, pie chart, and label values
def updateGraphs(ct, timeArray, infN, hN):
        c.clear()
        ct.append(infN)
        timeArray.append(int(currentDay+1))
        c.plot(timeArray, ct,color="red")
        plt.ion()
        cvst, = c.plot(int(infN), color="red", label="Infected moving object")
        c.legend(handles=[cvst])
        axPie.clear()
        dataProportion = np.array([hN, infN])
        axPie.pie(dataProportion, autopct=lambda val: updaterOfValuesAndPercentage(val, dataProportion),
                  explode=explode, labels=labelCondition, shadow=True, colors=colors)
        c.set_xlabel("Time (days)")
        c.set_ylabel("Infected moving object")


# for visualization IndoorGML data
def drawer(ax,allPoints,allObjects,v3d,alphaVal,lineWidthVal,FloorCheck,floorN):
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
    for i in range(len(allObjects)):
            for j in range(len(allObjects[i])):
                    newlist.append(allObjects[i][j])
            newlist.append([np.nan,np.nan,np.nan])
    inputList = [newlist]
    thisIndoor = ax.add_collection3d(Poly3DCollection(inputList, edgecolors='k', alpha=alphaVal,
                                                      linewidth=lineWidthVal))

# function for updating the values and the percentage in the pie chart
def updaterOfValuesAndPercentage(this, thisValues):
    output = int(this / 99.999*np.sum(thisValues))
    return "{:.1f}%\n({:d})".format(this, output)

# function for drawing specific floor
def drawerByFloor(floorN):
    global allPoints2D, allObjects2D
    ax2D.collections.pop()
    allPoints2D = []
    allObjects2D = []
    global floorChanger
    floorChanger = floorN
    fig2D.suptitle("Floor "+str(floorChanger)+":", fontsize=12)
    alphaVal = 0.7
    lineWidthVal = 1
    drawer(ax2D, allPoints2D, allObjects2D, False, alphaVal,lineWidthVal,True,floorChanger)

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
        percentageInfection.set("0.9")
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
        IP.set("1")
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
        # reading indoorGML file
        myGML_3D(pathGML.get())
        global diff, totalTime, HumanCount, totalDays
        listDF, timeStart, timeEnd, diff = getData(pathSIMOGenMovData.get())
        spreadDistance = float(spreadD.get())
        import csv
        dataToCSV = []
        dataToCSVInfection = []
        header = ['MO_ID', 'InfectedMO_ID', 'meetingCoordinate', 'meetingRoom', 'meetingDay', 'meetingTime']
        headerInfection = ['InfectedMO_ID', 'infectedDay']
        HumanCount = len(listDF)
        for i, ival in enumerate(listDF):
            if i < (len(listDF)):
                listT = listDF[i].values.tolist()
                regularHuman = MovingObject(listT[0][0], listT[1][5])
                regularHuman.startTime = datetime.strptime(listDF[i]['startTime'].values[0], "%Y-%m-%dT%H:%M:%SZ")
                regularHuman.endTime = datetime.strptime(listDF[i]['startTime'].values[-1], "%Y-%m-%dT%H:%M:%SZ")
                regularHuman.path = listDF[i]['startCoord']
                temp = listDF[i]['startCoord'].str.split(" ")
                regularHuman.path = [[float(j) for j in i] for i in temp]
                regularHuman.incubationVal = int(IP.get())+1
                regularHuman.defaultInfectionProbability = float(percentageInfection.get())
                humans.append(regularHuman)
                del listT
                i += 1
            else:
                pass

        end_date = timeEnd
        delta = timedelta(seconds=1)
        # default value how many days passed for simulation of infection
        daystotalPassed = 100000
        totalTime = 0

        global allInfected
        infectedHumanNumber = int(numberOfInfected.get())
        countInfected = int(numberOfInfected.get())
        for i in range(infectedHumanNumber):
            humans[i].makeInfected()
            dataToCSVInfection.append([humans[i].id, 1])
            allInfected.append(humans[i].id)

        start_date2 = timeStart
        while start_date2 <= end_date:
                for v, ival in enumerate(humans):
                    if humans[v].startTime <= start_date2 and humans[v].endTime >= start_date2 and humans[v].iterator2 < len(humans[v].path):
                        x = humans[v].path[humans[v].iterator2][0]
                        y = humans[v].path[humans[v].iterator2][1]
                        z = humans[v].path[humans[v].iterator2][2]
                        humans[v].trajectory.append((x, y))
                        humans[v].trajectoryZ.append(z)
                    else:
                        humans[v].trajectory.append((np.nan, np.nan))
                        humans[v].trajectoryZ.append(np.nan)
                    humans[v].iterator2 += 1
                start_date2 += delta
                totalTime += 1

        timeIncreaser = 39600 / (diff + 1)
        someTime = time(8, 50)  # 8:50AM
        currTime = time(8, 50)  # 8:50AM

        timeNow = clock.time()
        for dayCurrent in range(daystotalPassed):
            for t in range(totalTime):
                tempAllLocation = []
                for i, v in enumerate(humans):
                    tempAllLocation.append(humans[i].trajectory[t])
                for i, v in enumerate(humans):
                    if humans[i].isInfected == True:
                        # find euclidean distance between moving objects at current timestamp
                        answer = distance.cdist([humans[i].trajectory[t]], tempAllLocation, 'euclidean')
                        ansToList = answer[0].tolist()
                        for f in range(len(ansToList)):
                            # exclude current moving object
                            if (humans[f].id != humans[i].id and humans[f].isHealthy==True):
                                # if the distance between the infected moving object and healthy moving object is less than spread distance
                                if ansToList[f]!=None and ansToList[f] <= spreadDistance:
                                    # find out the floor where the two moving object are located
                                    floorVal = humans[f].checkAtWhichFloor(humans[f].trajectoryZ[t])
                                    floorVal2 = humans[i].checkAtWhichFloor(humans[i].trajectoryZ[t])
                                    # find out the cell where two moving objects are located
                                    valueOfRoomNumber = humans[f].checker(humans[f].trajectory[t],floorVal)
                                    valueOfRoomNumber2 = humans[i].checker(humans[i].trajectory[t],floorVal2)
                                    # if two moving objects are in the same room
                                    if  valueOfRoomNumber == valueOfRoomNumber2:
                                        humans[f].metWithInfectedMO(humans[i],dayCurrent)
                                        tempV = [humans[f].id, humans[i].id, (float(humans[f].trajectory[t][0]),float(humans[f].trajectory[t][1]),float(humans[f].trajectoryZ[t])),
                                                              valueOfRoomNumber, dayCurrent + 1,str(currTime.strftime("%H:%M:%S"))]
                                        if tempV not in dataToCSV:
                                            dataToCSV.append(tempV)
                                        else:
                                            pass
                currTime = (datetime.combine(date.today(), someTime) + timedelta(seconds=timeIncreaser)).time()
                someTime = currTime
                print("percentage of infection: " + str(float(countInfected/HumanCount*100))+"%")
            someTime = time(8, 50)
            for ival, h in enumerate(humans):
                if h.startInfection == True and h.alreadyInfected == False:
                    h.dayPassedAfterMeetingInfected += 1
                    h.InfectedDayChecker()
                    if h.becameNewInfected == True:
                        dataToCSVInfection.append([h.id, dayCurrent + 1])
                        countInfected += 1
            totalDays += 1

            if countInfected >= 0.9 * len(humans):
                print("More than 90% of MO were infected")
                timeAfter = clock.time()
                print("Required time: "+str(timeAfter-timeNow)+" seconds")
                break

        with open('meetingWithMO.csv', 'w', encoding='UTF8', newline='') as f:
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
            chunk = pd.read_csv("InfectionTimeline.csv", header=0,
                                usecols=['InfectedMO_ID', 'infectedDay'],
                                dtype={'InfectedMO_ID': str, 'infectedDay': int}, chunksize=1000)
            df = pd.concat(chunk)
            uniqueDays = df['infectedDay'].unique()
            maxDay = int(max(uniqueDays))
            infectedIDs = df['InfectedMO_ID'].tolist()
            df_list = [d for _, d in df.groupby(['infectedDay'])]

            global top, spreadDistance, frameNew, ax, fig, fig2D, ax2D, currentDay, labelDay, IncubationVal, currentTime, labelTime, timeIncreaser, var2, label2, newObjectsList, initialStartDate
            global allInfected, totalDays
            top = tkinter.Toplevel()
            top.title("Virus propagation model")
            top.attributes('-fullscreen', True)
            button1 = tkinter.Button(top, text="Close", font=fontName,command=lambda self=self, controller=controller: self.closeFunction(controller))
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
            canvas1 = tkinter.Canvas(top, highlightbackground="black", highlightcolor="black", highlightthickness=1)
            canvas1.pack(padx=5, pady=5, expand=True, fill="both", side="right")
            frame_top = tkinter.Frame(top, highlightbackground="black", highlightcolor="black", highlightthickness=1)
            frame_top.pack(side="top", padx=1, pady=1)
            varNew = tkinter.StringVar()
            labelNew = tkinter.Label(frame_top, textvariable=varNew, font=('Arial', 16))
            varNew.set("Virus propagation model in Indoor space")
            labelNew.pack(side="top", padx=5, pady=5)
            labelDay = tkinter.StringVar()
            labelDay.set("Day: " + str(currentDay+1))
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
            secondFrame = tkinter.Frame(frame_top, highlightbackground="black", highlightcolor="black", highlightthickness=1)
            canvasScroll = tkinter.Canvas(secondFrame)
            scrollbar = tkinter.Scrollbar(secondFrame, orient="vertical", command=canvasScroll.yview)
            frameNew = tkinter.Frame(canvasScroll)
            frameNew.bind("<Configure>", lambda e: canvasScroll.configure(scrollregion=canvasScroll.bbox("all")))
            canvasScroll.create_window((0, 0), window=frameNew)
            canvasScroll.configure(yscrollcommand=scrollbar.set)
            tkinter.Label(frameNew, font=scrollFontBig, text="Events log").pack()
            tkinter.Label(frameNew, font=scrollFontBig, text="--------------------------").pack()
            secondFrame.pack(padx=5, pady=5)
            buttonVisualize = tkinter.Button(secondFrame, text="Visualize", font=fontName,command=lambda pathGML=pathGML: visualize())
            buttonVisualize.pack(padx=10, pady=1, side="left")
            canvasScroll.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            thirdFrame = tkinter.Frame(frame_top, highlightbackground="black", highlightcolor="black", highlightthickness=1)
            tkinter.Label(thirdFrame, font=scrollFontBig, text="Infection case coordinates in each floor").pack(padx=1,pady=1)
            canvas2D = FigureCanvasTkAgg(fig2D, master=thirdFrame)
            thirdFrame.pack(padx=1, pady=1)
            fourthFrame = tkinter.Frame(thirdFrame, highlightbackground="black", highlightcolor="black",highlightthickness=1)
            fourthFrame.pack(side="left", padx=1, pady=1)
            canvas2D.get_tk_widget().pack(side="bottom", expand=True, padx=1, pady=1)
            canvas2D.mpl_connect('button_press_event', ax2D.axes._button_press)
            canvas2D.mpl_connect('button_release_event', ax2D.axes._button_release)
            canvas2D.mpl_connect('motion_notify_event', ax2D.axes._on_move)
            locationHealthy = []
            locationInfected = []
            dayChecker = []
            day = 1
            dayA = 0

            while day<=(totalDays):
                if dayA < len(df_list):
                    dayList = df_list[dayA]['infectedDay'].tolist()
                    infday = dayList[0]
                    if day==infday and day not in dayChecker:
                        dayChecker.append(day)
                        infList = df_list[dayA]['InfectedMO_ID'].tolist()
                        print("correct infdays")
                        print(infday)
                        print("infected number of people")
                        print(len(infList))

                        # adding new infected to the list
                        dayA += 1
                        day += 1
                        for x in range(len(infList)):
                                if str(infList[x]) not in allInfected:
                                    allInfected.append(str(infList[x]))
                        eachDayInfected.append(len(allInfected))
                        for cTime in range(totalTime):
                            for i, ival in enumerate(humans):
                                if humans[i].id in allInfected:
                                    locationInfected.append([humans[i].trajectory[cTime][0], humans[i].trajectory[cTime][1], humans[i].trajectoryZ[cTime]])
                                    locationHealthy.append([np.nan, np.nan, np.nan])
                                else:
                                    locationHealthy.append([humans[i].trajectory[cTime][0], humans[i].trajectory[cTime][1],humans[i].trajectoryZ[cTime]])
                                    locationInfected.append([np.nan, np.nan, np.nan])
                    elif day != infday and day not in dayChecker:
                        dayChecker.append(day)
                        eachDayInfected.append(len(allInfected))
                        day += 1
                        for cTime in range(totalTime):
                            for i, ival in enumerate(humans):
                                if humans[i].id in allInfected:
                                    locationInfected.append([humans[i].trajectory[cTime][0], humans[i].trajectory[cTime][1],
                                                             humans[i].trajectoryZ[cTime]])
                                    locationHealthy.append([np.nan, np.nan, np.nan])
                                else:
                                    locationHealthy.append([humans[i].trajectory[cTime][0], humans[i].trajectory[cTime][1],
                                                            humans[i].trajectoryZ[cTime]])
                                    locationInfected.append([np.nan, np.nan, np.nan])
                    else:
                        pass

            print(dayChecker)
            print(eachDayInfected)


            coord = np.array(locationHealthy, dtype=np.float32)
            coordInfected = np.array(locationInfected, dtype=np.float32)
            t = np.array([np.ones(len(humans)) * i for i in range(totalTime*len(dayChecker))], dtype=np.uint32).flatten()
            df = pd.DataFrame(
                {"time": t, "x": coord[:, 0], "y": coord[:, 1], "z": coord[:, 2], "xInfected": coordInfected[:, 0],
                 "yInfected": coordInfected[:, 1], "zInfected": coordInfected[:, 2]})
            data = df[df['time'] == 0]
            graph, = ax.plot(data.x, data.y, data.z, c='green', marker='o', linestyle="",
                             markeredgecolor='black', markeredgewidth=0.5, markersize=4,label="Healthy moving object")
            new, = ax.plot(data.xInfected, data.yInfected, data.zInfected, color='red', marker='o', linestyle="",
                           markeredgecolor='black', markeredgewidth=0.5, markersize=4, label = "Infected moving object")
            timeIncreaser = 39600/(diff + 1)
            def animate(t):
                global  sometime, newTime, currentDay ,labelDay, labelTime,timeArray
                global timeController
                data = df[df['time'] == t]
                graph.set_data(data.x, data.y)
                graph.set_3d_properties(data.z)
                new.set_data(data.xInfected, data.yInfected)
                new.set_3d_properties(data.zInfected)
                if timeController>(totalTime*1) and currentDay<=maxDay:
                    currentDay+=1
                    labelDay.set("Day: " + str(currentDay+1))
                    sometime = time(8, 50)  # 8:50am
                    labelTime.set("Time: " + str(sometime))
                    var2.set("Number of infected people: " + str(eachDayInfected[currentDay]))
                    updateGraphs(ct, timeArray, eachDayInfected[currentDay], int(len(humans))-eachDayInfected[currentDay])
                    timeController = 0
                elif timeController<=(totalTime*1) and currentDay<=maxDay:
                    newTime = (datetime.combine(date.today(), sometime) + timedelta(seconds=timeIncreaser)).time()
                    sometime = newTime
                    labelTime.set("Time: " + str(newTime.strftime("%H:%M:%S")))
                    timeController += 1
                return graph, new

            allPoints = []
            allObjects = []
            allPoints2D = []
            allObjects2D = []
            alphaVal = 0.3
            lineWidthVal = 0.05
            drawer(ax, allPoints, allObjects, True, alphaVal, lineWidthVal, False,0)
            ax.set_axis_off()
            ax.set_xlim3d([0, max(highAndLowX)])
            ax.set_ylim3d([0, max(highAndLowY)])
            ax.set_zlim3d([0, max(highAndLowZ)])
            ax.set_box_aspect((max(highAndLowX), max(highAndLowY), max(highAndLowZ)))
            ax2D.set_axis_off()
            ax2D.set_xlim3d([0, max(highAndLowX)])
            ax2D.set_ylim3d([0, max(highAndLowY)])
            ax2D.set_zlim3d([0, max(highAndLowZ)])
            ax2D.set_box_aspect((max(highAndLowX), max(highAndLowY), max(highAndLowZ)))
            ax.legend(loc="best")
            ax2D.legend(loc="best")
            global animation
            # create button for each floor
            for k, v in floorsAndValues.items():
                if k:
                    floorNumber = k
                    buttonF = tkinter.Button(fourthFrame, text="Floor" + str(k), font=fontName,
                                             command=lambda floorNumber=floorNumber: drawerByFloor(floorNumber))
                    buttonF.pack(side="top", fill="x", padx=10, pady=1)
            var1 = tkinter.StringVar()
            label1 = tkinter.Label(canvas1, textvariable=var1, font=('Arial', 14))
            var1.set("Total number of moving object: " + str(HumanCount))
            label1.pack(side="top", padx=5, pady=5)
            var2 = tkinter.StringVar()
            label2 = tkinter.Label(canvas1, textvariable=var2, font=('Arial', 14))
            var2.set("Number of infected moving object: " + str(eachDayInfected[currentDay]))
            label2.pack(side="top", padx=5, pady=5)
            labelNew = tkinter.Label(canvas1, justify='center')
            labelNew.pack()
            alphaVal = 0.7
            lineWidthVal = 1
            drawer(ax2D, allPoints2D, allObjects2D, False, alphaVal, lineWidthVal, False, 0)
            ax.set_axis_off()
            ax2D.set_axis_off()
            ax2D.view_init(90)
            global ct, timeArray, f, c, axPie
            ct = [eachDayInfected[currentDay],eachDayInfected[currentDay]]
            timeArray = [0,1]
            f = plt.figure(figsize=(5, 4))
            c = f.add_subplot(1, 1, 1)
            c.axis([1, 20, 0, int(len(humans))])
            caja = plt.Rectangle((0, 0), 100, 100, fill=True)
            cvst, = c.plot(eachDayInfected[currentDay], color="red", label="Infected moving object")
            c.legend(handles=[cvst])
            c.set_xlabel("Time (days)")
            c.set_ylabel("Infected moving object")
            dataProportion = np.array([int(len(humans))-eachDayInfected[currentDay],eachDayInfected[currentDay]])
            # Creating pie
            myPie, axPie = plt.subplots(figsize=(5, 5))
            axPie.pie(dataProportion, autopct=lambda val: updaterOfValuesAndPercentage(val, dataProportion), explode=explode, labels=labelCondition, shadow=True, colors=colors, wedgeprops=wedgeProp)
            updateGraphs(ct, timeArray, eachDayInfected[currentDay], int(len(humans))-eachDayInfected[currentDay])
            Graph(canvas1, f).pack(side="bottom", padx=5, pady=5)
            Graph(canvas1, myPie).pack(side="bottom", padx=5, pady=5)
            animation = matplotlib.animation.FuncAnimation(fig, animate, (len(dayChecker)+1) * (totalTime), interval=0.0001, blit=True, repeat=False)
            buttonPausingMov = tkinter.Button(frame_bottom, text="Pause simulation", bg='brown', fg='white', font=fontName, command=lambda animation=animation: pauseAnimation(animation))
            buttonPausingMov.pack(padx=2, pady=2, side="left")
            buttonStartingMov = tkinter.Button(frame_bottom, text="Continue simulation", bg='green', fg='white', font=fontName, command=lambda animation=animation: continueAnimation(animation))
            buttonStartingMov.pack(padx=2, pady=2, side="left")


# main function
def main():
    app = program()
    app.mainloop()

if __name__ == "__main__":
    main()