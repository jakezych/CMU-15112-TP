from cmu_112_graphics import *
from tkinter import *
from broad_categories import *
from clue_dictionary import *
from animation_helpers import *
from game_mode import *
from menu_mode import *
from practice import *
import random
#draws and organizes all of the useful statistics to display to the user

class StatisticsMode(Mode):
    def appStarted(mode):
        mode.gray = rgbString(192, 192, 192) 
        mode.margin = 15
        mode.quitButton = Button(mode.width - 80, mode.height - 40, mode.width - 10,
                                 mode.height - 10)
    
    def initializeProfile(mode, profile):
        mode.colors = getColorsList()
        mode.statisticsProfile = profile
        mode.profileStats, mode.highScore = mode.initializeProfileStats()
        mode.topScores = mode.initializeTopScores()
        mode.topColors = mode.initializeTopColors()
        mode.totalAnswered, mode.totalAccuracy = mode.calculateTotals()
    
    #initializes the top 5 or less scores depending on how many have been answered
    def initializeTopScores(mode):
        scores = []
        for category in mode.profileStats:
            if(int(mode.profileStats[category][1]) == 0):
                continue
            else:
                accuracy = int(mode.profileStats[category][0]) / int(mode.profileStats[category][1])
                scores.append((category, accuracy))
        #sort by the accuracy values in descending order
        scores.sort(key = lambda tup: tup[1], reverse = True)
        topScores = scores[0: 5]
        return topScores

    def initializeTopColors(mode):
        topColors = []
        for i in range(len(mode.topScores)):
            randIndex = random.randint(0, len(mode.colors) - 1)
            topColors.append(mode.colors[randIndex])
        return topColors

    def calculateTotals(mode):
        totalAnswered = 0
        totalCorrect = 0
        for category in mode.profileStats:
            totalAnswered += int(mode.profileStats[category][1])
            totalCorrect += int(mode.profileStats[category][0])
        if(totalAnswered == 0):
            totalAccuracy = 0.0
        else:
            totalAccuracy = (totalCorrect / totalAnswered) * 100
        return totalAnswered, totalAccuracy

    #reads scores of given profile and stores them locally in a dictionary
    def initializeProfileStats(mode):
        f = open("profiles.txt", "r+")
        contents = f.read()
        stats = mode.initializeKeys()
        highScore = 0
        inProfile = False
        for line in contents.splitlines():
            if(line == f"{mode.statisticsProfile[0]},{mode.statisticsProfile[1]}"):
                inProfile = True
                #skip to next line
                continue
            if(inProfile):
                L = line.split(",")
                stats[L[0]][0] = L[1] #number of answered
                stats[L[0]][1] = L[2] #number of correct
                if(int(L[2]) != 0):
                    accuracy = int(L[1]) / int(L[2])
                else:
                    accuracy = 0.0
                stats[L[0]][2] = mode.getColorAccuracy(accuracy)
                if(L[0] == "Misc."):
                    contentsList = contents.splitlines()
                    currentIndex = contentsList.index(line)
                    highScore = contentsList[currentIndex + 1] 
                    inProfile = False
        return stats, highScore
    
    #returns what color the category should be displayed as based on accuracy
    def getColorAccuracy(mode, accuracy):
        if(accuracy >= .80): 
            return rgbString(17, 156, 9) #green
        elif(accuracy >= .60):
            return rgbString(0, 140, 255) #blue
        elif(accuracy >= .40):
            return rgbString(150, 75, 0) #brown
        elif(accuracy >= .20):
            return rgbString(230, 180, 0) #orange
        else:
            return rgbString(235, 23, 23) #red
        
    #create all the key values for the stats dictionary
    def initializeKeys(mode):
        counter = 0
        stats = dict()
        for broadCategory in broadCategoryNames:
            color = "black"
            #tuple is (number of correct, number of attempted)
            stats[broadCategory] = [0,0, color]
        return stats

    def mousePressed(mode, event):
        mode.quitButton.updateCoordinates(mode.width - 80, mode.height - 40, mode.width - 10,
                                          mode.height - 10)  
        if(event.x > mode.quitButton.x0 and event.x < mode.quitButton.x1 and
               event.y > mode.quitButton.y0 and event.y < mode.quitButton.y1):
            mode.app.setActiveMode(mode.app.menuMode)
        
    def drawStats(mode, canvas):
        #calculate the height of the rectangle where stats are drawn
        totalHeight = mode.height - 2*mode.margin 
        totalWidth = mode.width / 2 - mode.margin
        #divide the height by how many broad categories there are 
        step = totalHeight / (len(broadCategoryNames) + 1)
        counter =  1
        for category in mode.profileStats:
            if(int(mode.profileStats[category][1]) == 0):
                percentage = 0.0
            else:
                percentage = (int(mode.profileStats[category][0]) / int(mode.profileStats[category][1])) * 100
            canvas.create_text(totalWidth / 2, mode.margin + step * counter, 
                               text = category + ": " + str(round(percentage, 2)) + "%", 
                               fill = mode.profileStats[category][2],
                               font = "times 20 bold")
            counter += 1
        canvas.create_text(mode.margin + 60, mode.margin + step, 
                           text = "Accuracy:", font = "times 20 bold")

    #draws the total accuracy and total number of clues answered
    def drawTotals(mode, canvas):
        height = (mode.height / 2 + mode.height / 6 + mode.height - mode.height / 10) / 2
        canvas.create_text(mode.width / 2 + mode.width / 8, height - 25, 
                           text = "Total Accuracy: " + str(round(mode.totalAccuracy, 2)) + "%",
                           font = "times 22 bold")
        canvas.create_text(mode.width - mode.width / 8 - mode.margin, height - 25, 
                           text = "Total Answered: " + str(mode.totalAnswered),
                           font = "times 22 bold") 
        canvas.create_text(mode.width / 2 + mode.width / 4, height + 25,
                           text = "Lightning Mode High Score: $" + str(mode.highScore),
                           font = "times 22 bold")
        
    def drawGraph(mode, canvas):
        #top left point, origin points, and bottom right point of axes
        yAxisYPos = mode.margin + 30
        originX = mode.width / 2 + 50
        originY = mode.height / 2 + mode.height / 6 - mode.margin - 40
        xAxisXPos = mode.width - mode.margin - 50
        #y-axis
        canvas.create_line(originX, yAxisYPos, originX, originY, width = '2')
        #x-axis
        canvas.create_line(originX, originY, xAxisXPos, originY, width = '2')
        #split the x-axis line into however many top scores there are (max 5)
        step = 0 
        if(len(mode.topScores) != 0):
            step = (xAxisXPos - originX) / len(mode.topScores)
        counter = 1
        #draw bars
        for (category, accuracy) in mode.topScores:
            scale = 1 - accuracy
            canvas.create_line(mode.width / 2 + step*counter, originY, 
                               mode.width / 2 + step*counter, 
                               yAxisYPos + (originY - yAxisYPos) * scale, width = '30', 
                               fill = mode.topColors[counter - 1])
            canvas.create_text(mode.width / 2 + step*counter, originY + 15,
                               text = category, width = 75, font = "times 12 bold")
            counter += 1
        #title
        canvas.create_text((originX + xAxisXPos) / 2, mode.margin + 20,
                            text = "Top Scores", font = "times 18 bold")
    def redrawAll(mode, canvas):
        mode.quitButton.updateCoordinates(mode.width - 80, mode.height - 40, mode.width - 10,
                                          mode.height - 10)                 
        canvas.create_rectangle(0, 0, mode.width, mode.height, fill = mode.gray)
        canvas.create_rectangle(mode.margin, mode.margin, 
                                mode.width / 2 - mode.margin, mode.height - mode.margin,
                                fill = "white", width = '5')
        mode.drawStats(canvas)
        canvas.create_rectangle(mode.width / 2, mode.height / 2 + mode.height / 6,
                                mode.width - mode.margin, mode.height - mode.height / 10,
                                fill = "white", width = '5')
        mode.drawTotals(canvas)
        canvas.create_rectangle(mode.width / 2, mode.margin, mode.width - mode.margin,
                                mode.height / 2 + mode.height / 6 - mode.margin, 
                                fill = "white", width = '5')
        mode.drawGraph(canvas)
        canvas.create_rectangle(mode.quitButton.x0, mode.quitButton.y0,
                                mode.quitButton.x1, mode.quitButton.y1, 
                                fill = "pink", width = '3')
        canvas.create_text((mode.quitButton.x0 + mode.quitButton.x1) / 2,
                           (mode.quitButton.y0 + mode.quitButton.y1) / 2,
                           text = "QUIT", font = "Helvetica 16 bold")