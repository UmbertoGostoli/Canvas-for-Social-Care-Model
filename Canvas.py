# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 12:17:23 2019

@author: Umberto Gostoli
"""
from collections import OrderedDict
from person import Person
from person import Population
from house import House
from house import Town
from house import Map
import Tkinter
import pylab
import pandas as pd
import os
import time
import pickle


def init_params():
    """Set up the simulation parameters."""

    p = OrderedDict()
    p['startYear'] = 1860
    p['num5YearAgeClasses'] = 25
    p['numCareLevels'] = 5
    p['pixelsInPopPyramid'] = 2000
    p['pixelsPerTown'] = 56
    p['mapGridXDimension'] = 8
    p['mapGridYDimension'] = 12
    p['careLevelColour'] = ['blue','green','yellow','orange','red']
    p['houseSizeColour'] = ['blue','green','yellow','orange','red', 'lightgrey']
    p['mainFont'] = 'Helvetica 18'
    p['fontColour'] = 'white'
    p['dateX'] = 70
    p['dateY'] = 20
    p['popX'] = 70
    p['popY'] = 50
    p['delayTime'] = 0.0
    p['maxTextUpdateList'] = 22
    
    return p

class PopPyramid:
    """Builds a data object for storing population pyramid data in."""
    def __init__ (self, ageClasses, careLevels):
        self.maleData = pylab.zeros((int(ageClasses), int(careLevels)),dtype=int)
        self.femaleData = pylab.zeros((int(ageClasses), int(careLevels)),dtype=int)

    def update(self, year, ageClasses, careLevels, pixelFactor, people):
        ## zero the two arrays
        for a in range (int(ageClasses)):
            for c in range (int(careLevels)):
                self.maleData[a,c] = 0
                self.femaleData[a,c] = 0
        ## tally up who belongs in which category
        for i in people:
            ageClass = ( year - i.birthdate ) / 5
            if ageClass > ageClasses - 1:
                ageClass = ageClasses - 1
            careClass = i.careNeedLevel
            if i.sex == 'male':
                self.maleData[int(ageClass), int(careClass)] += 1
            else:
                self.femaleData[int(ageClass), int(careClass)] += 1

        ## normalize the totals into pixels
        total = len(people)        
        for a in range (int(ageClasses)):
            for c in range (int(careLevels)):
                self.maleData[a,c] = pixelFactor * self.maleData[a,c] / total
                self.femaleData[a,c] = pixelFactor * self.femaleData[a,c] / total


def initializeCanvas(year):
    """Put up a TKInter canvas window to animate the simulation."""
    canvas.pack()
    
    ## Draw some numbers for the population pyramid that won't be redrawn each time
    for a in range(0,25):
        canvas.create_text(170, 385 - (10 * a), 
                           text=str(5*a) + '-' + str(5*a+4),
                           font='Helvetica 6',
                           fill='white')

    ## Draw the overall map, including towns and houses (occupied houses only)
    for y in range(p['mapGridYDimension']):
        for x in range(p['mapGridXDimension']):
            xBasic = 580 + (x * p['pixelsPerTown'])
            yBasic = 15 + (y * p['pixelsPerTown'])
            canvas.create_rectangle(xBasic, yBasic,
                                    xBasic+p['pixelsPerTown'],
                                    yBasic+p['pixelsPerTown'],
                                    outline='grey',
                                    state = 'hidden' )
    houses = []
    occupiedHouses = []
    for index, row in mapData[0].iterrows():
        xBasic = 580 + (row['town_x']*p['pixelsPerTown'])
        yBasic = 15 + (row['town_y']*p['pixelsPerTown'])
        xOffset = xBasic + 2 + (row['x']*2)
        yOffset = yBasic + 2 + (row['y']*2)
        
        outlineColour = fillColour = p['houseSizeColour'][row['size']]
        width = 1
        if row['size'] > 0:
            occupiedHouses.append(1)
        else:
            occupiedHouses.append(0)
        houses.append(canvas.create_rectangle(xOffset,yOffset,
                                xOffset + width, yOffset + width,
                                outline=outlineColour,
                                fill=fillColour,
                                state = 'normal'))

    canvas.update()
    time.sleep(0.5)
    canvas.update()

    for h in houses:
        canvas.itemconfig(h, state='hidden')
        if occupiedHouses[houses.index(h)] == 1:
            canvas.itemconfig(h, state='normal')
            
    canvas.update()
    updateCanvas(0, year, ['Events Log'], houses)
    
    return houses

def updateCanvas(n, year, textUpdateList, houses):
    """Update the appearance of the graphics canvas."""
    
    ## First we clean the canvas off; some items are redrawn every time and others are not
    canvas.delete('redraw')

    ## Now post the current year and the current population size
    canvas.create_text(p['dateX'],
                       p['dateY'],
                       text='Year: ' + str(year),
                       font = p['mainFont'],
                       fill = p['fontColour'],
                       tags = 'redraw')
    canvas.create_text(p['popX'],
                       p['popY'],
                       text='Pop: ' + str(outputs.loc[outputs['year'] == year, 'currentPop'].values[0]),
                       font = p['mainFont'],
                       fill = p['fontColour'],
                       tags = 'redraw')

    canvas.create_text(p['popX'],
                       p['popY'] + 30,
                       text='Ever: ' + str(outputs.loc[outputs['year'] == year, 'popFromStart'].values[0]),
                       font = p['mainFont'],
                       fill = p['fontColour'],
                       tags = 'redraw')

    ## Also some other stats, but not on the first display
    if year > p['startYear']:
        canvas.create_text(350,20, 
                           text='Avg household: ' + str(round(outputs.loc[outputs['year'] == year, 'averageHouseholdSize'].values[0], 2)),
                           font = 'Helvetica 11',
                           fill = 'white',
                           tags = 'redraw')
        canvas.create_text(350,40,     
                           text='Marriages: ' + str(outputs.loc[outputs['year'] == year, 'marriageTally'].values[0]),
                           font = 'Helvetica 11',
                           fill = 'white',
                           tags = 'redraw')
        canvas.create_text(350,60,
                           text='Divorces: ' + str(outputs.loc[outputs['year'] == year, 'divorceTally'].values[0]),
                           font = 'Helvetica 11',
                           fill = 'white',
                           tags = 'redraw')
        canvas.create_text(350,100,
                           text='Total care need: ' + str(round(outputs.loc[outputs['year'] == year, 'totalSocialCareNeed'].values[0],0)),
                           font = 'Helvetica 11',
                           fill = 'white',
                           tags = 'redraw')
        canvas.create_text(350,120,
                           text='Num taxpayers: ' + str(round(outputs.loc[outputs['year'] == year, 'taxPayers'].values[0],0)),
                           font = 'Helvetica 11',
                           fill = 'white',
                           tags = 'redraw')
        canvas.create_text(350,140,
                           text='Family care ratio: ' + str(round(100.0*outputs.loc[outputs['year'] == year, 'familyCareRatio'].values[0],0)) + "%",
                           font = 'Helvetica 11',
                           fill = 'white',
                           tags = 'redraw')
        canvas.create_text(350,160,
                           text='Tax burden: ' + str(round(outputs.loc[outputs['year'] == year, 'taxBurden'].values[0],0)),
                           font = 'Helvetica 11',
                           fill = 'white',
                           tags = 'redraw')
        canvas.create_text(350,180,
                           text='Marriage prop: ' + str(round(100.0*outputs.loc[outputs['year'] == year, 'marriagePropNow'].values[0],0)) + "%",
                           font = 'Helvetica 11',
                           fill = 'white',
                           tags = 'redraw')
    
    occupiedHouses = []
    outlineColour = []
    fillColour = []
    for index, row in mapData[n].iterrows():
        colorIndex = -1
        size = row['size']
        if size == 0:
            colorIndex = 5
        else:
            if size > 4:
                colorIndex = 4
            else:
                colorIndex = size
        outlineColour.append(p['houseSizeColour'][colorIndex])
        fillColour.append(p['houseSizeColour'][colorIndex])
        if row['size'] > 0:
            occupiedHouses.append(1)
        else:
            occupiedHouses.append(0)
            
            
    for h in houses:
        if occupiedHouses[houses.index(h)] == 0:
            canvas.itemconfig(h, state='hidden')
        else:
            canvas.itemconfig(h, outline=outlineColour[houses.index(h)], fill=fillColour[houses.index(h)], state='normal')

    ## Draw the population pyramid split by care categories
    for a in range(0, p['num5YearAgeClasses']):
        malePixel = 153
        femalePixel = 187
        for c in range(0, p['numCareLevels']):
            numPeople = outputs.loc[outputs['year'] == year, 'currentPop'].values[0]
            mWidth = p['pixelsInPopPyramid']*maleData[c].loc[maleData[c]['year'] == year, 'Class Age ' + str(a)].values[0]/numPeople
            fWidth = p['pixelsInPopPyramid']*femaleData[c].loc[femaleData[c]['year'] == year, 'Class Age ' + str(a)].values[0]/numPeople

            if mWidth > 0:
                canvas.create_rectangle(malePixel, 380 - (10*a),
                                        malePixel - mWidth, 380 - (10*a) + 9,
                                        outline= p['careLevelColour'][c],
                                        fill= p['careLevelColour'][c],
                                        tags = 'redraw')
            malePixel -= mWidth
            
            if fWidth > 0:
                canvas.create_rectangle(femalePixel, 380 - (10*a),
                                        femalePixel + fWidth, 380 - (10*a) + 9,
                                        outline=p['careLevelColour'][c],
                                        fill=p['careLevelColour'][c],
                                        tags = 'redraw')
            femalePixel += fWidth
    
    
    
    ## Draw in the display house and the people who live in it
    
#    if len(displayHouse.occupants) < 1:
#        ## Nobody lives in the display house any more, choose another
#        if nextDisplayHouse != None:
#            displayHouse = nextDisplayHouse
#            nextDisplayHouse = None
#        else:
#            displayHouse = random.choice(pop.livingPeople).house
#            self.textUpdateList.append(str(self.year) + ": Display house empty, going to " + self.displayHouse.name + ".")
#            messageString = "Residents: "
#            for k in self.displayHouse.occupants:
#                messageString += "#" + str(k.id) + " "
#            self.textUpdateList.append(messageString)
    
    # print 'House size: ' + str(houseData.loc[houseData['year'] == year, 'size'].values[0])
    size = houseData.loc[houseData['year'] == year, 'size'].values[0]
    colorIndex = -1
    if size == 0:
        colorIndex = 5
    else:
        if size > 4:
            colorIndex = 4
        else:
            colorIndex = size
    outlineColour = p['houseSizeColour'][colorIndex]
    canvas.create_rectangle(50, 450, 300, 650,
                            outline = outlineColour,
                            tags = 'redraw' )
    canvas.create_text (60, 660,
                        text="Display house " + houseData.loc[houseData['year'] == year, 'House name'].values[0],
                        font='Helvetica 10',
                        fill='white',
                        anchor='nw',
                        tags='redraw')
                              

    ageBracketCounter = [ 0, 0, 0, 0, 0 ]

    for index, row in householdData[n].iterrows():
        age = row['Age']
        ageBracket = int(age/20)
        if ageBracket > 4:
            ageBracket = 4
        careClass = row['Health']
        sex = row['Sex']
        idNumber = row['ID']
        drawPerson(age,ageBracket,ageBracketCounter[ageBracket],careClass,sex,idNumber)
        ageBracketCounter[ageBracket] += 1

    ## Draw in some text status updates on the right side of the map
    ## These need to scroll up the screen as time passes

    if len(textUpdateList) > p['maxTextUpdateList']:
        excess = len(textUpdateList) - p['maxTextUpdateList']
        textUpdateList = textUpdateList[excess:excess+p['maxTextUpdateList']]
        

    baseX = 1035
    baseY = 30
    for i in textUpdateList:
        canvas.create_text(baseX,baseY,
                           text=i,
                           anchor='nw',
                           font='Helvetica 9',
                           fill = 'white',
                           width = 265,
                           tags = 'redraw')
        baseY += 30

    ## Finish by updating the canvas and sleeping briefly in order to allow people to see it
    canvas.update()
    if p['delayTime'] > 0.0:
        time.sleep(p['delayTime'])

def drawPerson(age, ageBracket, counter, careClass, sex, idNumber):
    baseX = 70 + ( counter * 30 )
    baseY = 620 - ( ageBracket * 30 )

    fillColour = p['careLevelColour'][careClass]

    canvas.create_oval(baseX,baseY,baseX+6,baseY+6,
                       fill=fillColour,
                       outline=fillColour,tags='redraw')
    if sex == 'male':
        canvas.create_rectangle(baseX-2,baseY+6,baseX+8,baseY+12,
                                fill=fillColour,outline=fillColour,tags='redraw')
    else:
        canvas.create_polygon(baseX+2,baseY+6,baseX-2,baseY+12,baseX+8,baseY+12,baseX+4,baseY+6,
                              fill=fillColour,outline=fillColour,tags='redraw')
    canvas.create_rectangle(baseX+1,baseY+13,baseX+5,baseY+20,
                            fill=fillColour,outline=fillColour,tags='redraw')
        
        
        
    canvas.create_text(baseX+11,baseY,
                       text=str(age),
                       font='Helvetica 6',
                       fill='white',
                       anchor='nw',
                       tags='redraw')
    canvas.create_text(baseX+11,baseY+8,
                       text=str(idNumber),
                       font='Helvetica 6',
                       fill='grey',
                       anchor='nw',
                       tags='redraw')

def from_IDs_to_Agents(pop, space):
    for person in pop.allPeople:
        if person.motherID != -1:
            person.mother = [x for x in pop.allPeople if x.id == person.motherID][0]
        else:
            person.mother = None
        if person.fatherID != -1:
            person.father = [x for x in pop.allPeople if x.id == person.fatherID][0]
        else:
            person.father = None
            
        person.children = [x for x in pop.allPeople if x.id in person.childrenID]
        
    for person in pop.allPeople:
        person.house = [x for x in space.allHouses if x.id == person.houseID][0]
        if person in pop.livingPeople:
            person.house.occupants.append(person)
            
    return pop

def onclickButton1(evt):
    yearLog = []
    
    timeOnStart = time.time()
    
    for i in range(periods):
        startYear = time.time()
        
#        pop = popSim[i] #popID = pickle.load(open(directoryPop + '/save.p_' + str(year), 'rb')) # 
#        space = mapSim[i] # space = pickle.load(open(directoryMap + '/save.m_' + str(year), 'rb')) #
#        pop = from_IDs_to_Agents(popID, space)
#        if i == 0:
#            initializeCanvas(year, pop, space)
#            
#        pyramid.update(year, p['num5YearAgeClasses'], p['numCareLevels'], p['pixelsInPopPyramid'], pop.livingPeople)
        
        year = i + initialYear
        yearLog.extend(list(log.loc[log['year'] == year, 'message']))
        updateCanvas(i, year, yearLog, houses)
        
        endYear = time.time()
        
        print 'Year execution time: ' + str(endYear - startYear)
        
    endOfRendering = time.time()
    print ''
    print 'Total execution time: ' + str(endOfRendering - timeOnStart)
        

if __name__ == "__main__":
    
    p = init_params()
    
    window = Tkinter.Tk()
    canvas = Tkinter.Canvas(window,
                        width=1300,
                        height=700,
                        background='black')
    
    # Stat and destroy button code
    button1 = Tkinter.Button(window, text='start')
    button1.config(height=2, width=10)
    button1.bind("<Button-1>", onclickButton1)
    button2 = Tkinter.Button(window, text='stop', command=window.destroy)
    button2.config(height=2, width=10)
    canvas.create_window(950, 30 + 10, window=button1)
    canvas.create_window(950, 30 + 60, window=button2)
    
    pyramid = PopPyramid(p['num5YearAgeClasses'], p['numCareLevels'])
    
    # import data
    
    startYear = time.time()
    
    initialYear = 1860
    policyFolder = 'N:/Social Care Model for QQR/Simulations_Folder/2019_09_02-13_02_10/Rep_0/Scenario_0/Policy_0'
    outputs = pd.read_csv(policyFolder + '/Outputs.csv', sep=',', header=0)
    log = pd.read_csv(policyFolder + '/Log.csv', sep=',', header=0)
    houseData = pd.read_csv(policyFolder + '/HouseData.csv', sep=',', header=0)
    maleData = []
    for i in range(p['numCareLevels']):
        fileName = '/Pyramid_Male_' + str(i) + '.csv'
        maleData.append(pd.read_csv(policyFolder + fileName, sep=',', header=0))
    femaleData = []
    for i in range(p['numCareLevels']):
        fileName = '/Pyramid_Female_' + str(i) + '.csv'
        femaleData.append(pd.read_csv(policyFolder + fileName, sep=',', header=0))
    
    householdFolder = policyFolder + '/DataHousehold'
    periods = len([name for name in os.listdir(householdFolder) if os.path.isfile(os.path.join(householdFolder, name))])
    householdData = []
    for i in range(periods):
        year = i + initialYear
        fileName = '/DataHousehold_' + str(year) + '.csv'
        householdData.append(pd.read_csv(householdFolder + fileName, sep=',', header=0))
        
    mapFolder = policyFolder + '/DataMap'
    mapData = []
    for i in range(periods):
        year = i + initialYear
        fileName = '/DataMap_' + str(year) + '.csv'
        mapData.append(pd.read_csv(mapFolder + fileName, sep=',', header=0))
    
    endYear = time.time()
    print 'Time to load data: ' + str(endYear - startYear)
    
    houses = initializeCanvas(initialYear)
    
#    yearLog = []
#    for i in range(periods):
#        startYear = time.time()
#        year = i + initialYear
#        popID = popSim[i] #popID = pickle.load(open(directoryPop + '/save.p_' + str(year), 'rb')) # 
#        space = mapSim[i] # space = pickle.load(open(directoryMap + '/save.m_' + str(year), 'rb')) #
#        pop = from_IDs_to_Agents(popID)
#        if i == 0:
#            initializeCanvas(year)
#            
#        pyramid.update(year, p['num5YearAgeClasses'], p['numCareLevels'], p['pixelsInPopPyramid'], pop.livingPeople)
#        
#        yearLog.extend(list(log.loc[log['year'] == year, 'message']))
#        updateCanvas(year, yearLog)
#        
#        endYear = time.time()
#        
#        print 'Year execution time: ' + str(endYear - startYear)
    
    window.mainloop()
    
    
    