from cmu_112_graphics import *
from tkinter import *
from broad_categories import *
from clue_dictionary import *
from animation_helpers import *
from game_mode import *
from menu_mode import *
from statistics import *
import random
#handles all of the logic and animation for the practice mode

class PracticeMode(Mode):
    def appStarted(mode):
        mode.gray = rgbString(192, 192, 192) 
        mode.backgroundColor = rgbString(3, 0, 199)
        mode.forestGreen = rgbString(53, 179, 34)
        mode.darkRed = rgbString(179, 34, 34)
        mode.margin = 25
        mode.rightButton = Button(mode.margin + 15, mode.height - mode.height // 6, mode.width // 5,
                                mode.height - mode.margin - 15)
        mode.wrongButton = Button(mode.width / 5 + 15, mode.height - mode.height / 6,
                                mode.width / 5 + 15 + (mode.width / 5 - mode.margin - 15), 
                                mode.height - mode.margin - 15)
        mode.quitButton = Button(mode.width - mode.margin - 80, 
                                mode.height - mode.margin - 40, mode.width - mode.margin - 10,
                                mode.height - mode.margin - 10)

    def initializePracticeMode(mode, version, profile):
        #either random or personalized
        mode.version = version
        mode.practiceProfile = profile    
        #how many clues answered correctly in a row   
        mode.streak = 0
        mode.currentClue = None
        mode.getNextClue()
        #determines whether to display instructions
        mode.hasInteracted = False
        mode.showAnswer = False
        
    def getNextClue(mode):
        if(mode.version == "random"):
            mode.currentClue = mode.getRandomClue()
        else:
            mode.currentClue = mode.getPersonalizedClue()

    #pulls a completely random clue from the master dictionary of all possible clues
    def getRandomClue(mode):
        categoryList = list(clueDict)
        randCategoryIndex = random.randint(0, len(categoryList) - 1)
        randCategory = categoryList[randCategoryIndex]
        dateList = list(clueDict[randCategory])
        randDateIndex = random.randint(0, len(dateList) - 1)
        randDate = dateList[randDateIndex] 
        clueList = clueDict[randCategory][randDate]
        return mode.selectValue(clueList)

    #returns a clue based on the player's worst categories and their current streak
    def getPersonalizedClue(mode):
        worstBroadCategories = mode.getWorstCategories()
        categorySubList = mode.getCategorySubList(worstBroadCategories)
        #if sublist is not populated, pull from any category, otherwise select a broad category
        if(len(categorySubList) == 0):
            mode.getRandomClue()
        elif(len(categorySubList) > 1):
            randIndex = random.randint(0, len(categorySubList) - 1)
            broadCategory = categorySubList[randIndex][0]
        else:
            broadCategory = categorySubList[0][0]
        #get a list of all potential specific categories given a broad category
        specificCategoryList = broadCategoriesDict[broadCategory]
        categoryIndex = random.randint(0, len(specificCategoryList) - 1)
        randomSpecificCategory = specificCategoryList[categoryIndex]
        listOfDates = list(clueDict[randomSpecificCategory])
        randDateIndex = random.randint(0, len(listOfDates) - 1)
        randDate = listOfDates[randDateIndex] 
        clueList = clueDict[randomSpecificCategory][randDate]
        return mode.selectValue(clueList)

    #chooses a clue from a given category based on the current streak
    #clue value is determined based on how many correct in answered in a row
    def selectValue(mode, clueList):
        #float [0-1)
        roll = random.random()
        chosenValue = None
        if(mode.streak <= 1): 
            mode.backgroundColor = rgbString(3, 0, 199)
            #0-1 correct: 80% chance $200, 20% chance $400 
            if(roll >= 0 and roll <= .80):
                chosenValue = 200
            else:
                chosenValue = 400
        elif(mode.streak in [2,3]): 
            #dark purple
            mode.backgroundColor = rgbString(83, 25, 209)
            #2-3 correct: 35% chance $200, 50% chance $400, 15% chance $600
            if(roll >= 0 and roll <= .35):
                chosenValue = 200
            elif(roll > .35 and roll <= .85):
                chosenValue = 400
            else:
                chosenValue = 600
        elif(mode.streak in [4,5,6]): 
            #darker cyan
            mode.backgroundColor = rgbString(38, 158, 152)
            #4-6 correct: 25% chance $400, 65% chance $600, 10% chance $800
            if(roll >= 0 and roll <= .25):
                chosenValue = 400
            elif(roll > .25 and roll <= .90):
                chosenValue = 600
            else:
                chosenValue = 800
        elif(mode.streak in [7,8,9]): 
            #dark pink
            mode.backgroundColor = rgbString(189, 89, 164)
            #7+ correct: 20% chance $600, 45% chance $800, 35% chance $1000
            if(roll >= 0 and roll <= .20):
                chosenValue = 600
            elif(roll > .20 and roll <= .65):
                chosenValue = 800
            else:
                chosenValue = 1000
        elif(mode.streak >= 10):
            #maroon
            mode.backgroundColor = rgbString(135, 0, 11)
            #10+ correct 35% chance $800, 65% chance $1000
            if(roll >= 0 and roll <= .35):
                chosenValue = 800
            else:
                chosenValue = 1000
        possibleValues = []
        #if a clue matches the value return it, otherwise add to list of other possible values
        for clue in clueList:
            currentValue = clue.value
            #double jeopardy values are standardized to [200 - 1000]
            if(clue.level == '2'):
                currentValue //= 2
            #assign final jeopardy clues as the chosen value
            elif(clue.level == '3'):
                currentValue = chosenValue
            if(chosenValue == int(currentValue)):
                return clue
            else:
                possibleValues.append((clue, int(currentValue)))
        #sort by clue values
        possibleValues.sort(key = lambda tup: tup[1])
        #find the clue with the closest value to the chosen one
        return mode.findClosestValue(chosenValue, possibleValues)
    
    #returns the clue with the closest value to the chosen value from a list of clues
    def findClosestValue(mode, chosenValue, possibleValues):
        bestDifference = None
        bestClue = None
        for (clue, value) in possibleValues:
            currentDifference = abs(chosenValue - value)
            if(bestDifference == None or currentDifference < bestDifference):
                bestDifference = currentDifference
                bestClue = clue
        return bestClue

    #gets the broad category to be selected from next
    def getCategorySubList(mode, worstBroadCategories):
        #float [0-1)
        rollCategory = random.random()
        #40% chance to be from worst category
        if(rollCategory >= 0.0 and rollCategory <= .40):
            categorySubList = worstBroadCategories[0]
        #35% chance to be from 2nd worst category
        elif(rollCategory > .40 and rollCategory <= .75):
            categorySubList = worstBroadCategories[1]
        #15% chance to be from 3rd worst category
        elif(rollCategory > .75 and rollCategory <= .90):
            categorySubList = worstBroadCategories[2]
        #7.5% chance to be from 4th worst category
        elif(rollCategory > .90 and rollCategory <= .975):
            categorySubList = worstBroadCategories[3]
        #2.5% chance to be from 5th worst category
        elif(rollCategory > .975 and rollCategory <= 1):
            categorySubList = worstBroadCategories[4]
        return categorySubList

    #returns a list of sets of up to the 5 worst categories (of those that have been attempted before)
    def getWorstCategories(mode):
        stats = mode.initializeProfileStats()
        #reads from stats dictionary and creates list of tuples (category, accuracy) for the attempted broad categories
        scores = []
        for category in stats:
            if(int(stats[category][1]) == 0):
                continue
            else:
                accuracy = int(stats[category][0]) / int(stats[category][1])
                scores.append((category, accuracy))
        #sort by the accuracy values
        scores.sort(key = lambda tup: tup[1])
        #create list of sublists of 5 worst categories, same accuracies go into same sublists
        worstScores = [[] for i in range(5)]
        currentIndex = 0
        for (category, accuracy) in scores:
            #worstScores[currentIndex][-1][1] is the previous accuracy
            #put into same sublist of accuracy is same or it is not yet populated
            if(len(worstScores[currentIndex]) == 0 or worstScores[currentIndex][-1][1] == accuracy):
                worstScores[currentIndex].append((category, accuracy))
            else:
                #if sublist populated and accuracy not same, move onto next sublist
                currentIndex += 1
                if(currentIndex == 5):
                    break
                else:
                    worstScores[currentIndex].append((category, accuracy))
        return worstScores

    #reads scores of given profile and stores them locally in a dictionary
    def initializeProfileStats(mode):
        f = open("profiles.txt", "r+")
        contents = f.read()
        stats = mode.initializeKeys()
        inProfile = False
        for line in contents.splitlines():
            if(line == f"{mode.practiceProfile[0]},{mode.practiceProfile[1]}"):
                inProfile = True
                #skip to next line
                continue
            if(inProfile):
                L = line.split(",")
                stats[L[0]][0] = L[1] #number of answered
                stats[L[0]][1] = L[2] #number of correct
                if(L[0] == "Misc."):
                    inProfile = False
        return stats

    #create all the key values for the stats dictionary
    def initializeKeys(mode):
        stats = dict()
        for broadCategory in broadCategoryNames:
            #tuple is (number of correct, number of attempted)
            stats[broadCategory] = [0,0]
        return stats

    def keyPressed(mode, event):
        mode.hasInteracted = True
        if(event.key == "n"):
            #skipping a clue while on streak decrements it 
            if(mode.streak > 0):
                mode.streak -= 1
            mode.getNextClue()
            mode.showAnswer = False
        elif(event.key == "m"):
            mode.showAnswer = True

    def mousePressed(mode, event):
        mode.rightButton.updateCoordinates(mode.margin + 15, mode.height - mode.height // 6, mode.width // 5,
                                mode.height - mode.margin - 15)
        mode.wrongButton.updateCoordinates(mode.width / 5 + 15, mode.height - mode.height / 6,
                                mode.width / 5 + 15 + (mode.width / 5 - mode.margin - 15), 
                                mode.height - mode.margin - 15)
        mode.quitButton.updateCoordinates(mode.width - mode.margin - 80, 
                                mode.height - mode.margin - 40, mode.width - mode.margin - 10,
                                mode.height - mode.margin - 10)
        if(event.x > mode.quitButton.x0 and event.x < mode.quitButton.x1 and
            event.y > mode.quitButton.y0 and event.y < mode.quitButton.y1):  
            mode.app.setActiveMode(mode.app.menuMode)                     
        #if buttons are present
        if(mode.showAnswer):
            #if player is correct, increment streak and show next clue
            if(event.x > mode.rightButton.x0 and event.x < mode.rightButton.x1 and
               event.y > mode.rightButton.y0 and event.y < mode.rightButton.y1):
                mode.streak += 1
                mode.getNextClue()
                mode.showAnswer = False
            #if player is incorrect, reset their streak
            if(event.x > mode.wrongButton.x0 and event.x < mode.wrongButton.x1 and
               event.y > mode.wrongButton.y0 and event.y < mode.wrongButton.y1):
                mode.streak = 0
                mode.getNextClue()
                mode.showAnswer = False

    #draws the informational text
    def drawOverlay(mode, canvas):
        categoryText = mode.currentClue.category.upper()
        if(mode.currentClue.level == '2'):
            value = int(mode.currentClue.value) // 2
        else:
            value = mode.currentClue.value
        valueText =  str(value)
        broadCategoryText= mode.currentClue.broadCategory
        #broad category text
        canvas.create_text(125, 55, 
                          text = "Broad Category: ",
                          fill = 'white', font = 'Helvetica 22 bold') 
        canvas.create_text(275 + len(broadCategoryText), 55, text = broadCategoryText,
                          width = 250, fill = 'white', font = 'Helvetica 22 bold')
        #specific category text
        canvas.create_text(90, 110, 
                          text = "Category: ",
                          fill = 'white', font = 'Helvetica 22 bold')
        canvas.create_text(275 + len(categoryText), 110, text = categoryText,
                        width = 300, fill = 'white', font = 'Helvetica 22 bold')
        #value of clue text 
        canvas.create_text(99, 165, text = "Value: $" + valueText,
                          fill = 'white', font = 'Helvetica 22 bold')
        #streak text
        canvas.create_text(85, 225, text = "Streak: " + str(mode.streak),
                          fill = 'white', font = 'Helvetica 22 bold')
        #instructions text
        if(not mode.hasInteracted):
            canvas.create_text(mode.width - 200, 55, text = "Press \"n\" to Display Next Clue",
                            fill = 'white', font = 'Helvetica 22 bold')
            canvas.create_text(mode.width - 208, 90, text = "Press \"m\" to Display Answer",
                            fill = 'white', font = 'Helvetica 22 bold')

    def drawPracticeClue(mode, canvas):
        clueText = mode.currentClue.question.upper()
        textSize = 26 + int(500 / len(clueText)) #dynamically sized
        #clue text
        canvas.create_text(mode.width / 2, mode.height / 2 - mode.height / 16, text = clueText, 
                        fill = 'white', width = mode.width - mode.margin - 350,
                        font = f'Helvetica {textSize} bold', justify = 'center')

    def drawAnswer(mode, canvas):
        answerText = mode.currentClue.answer
        textSize = 32 + int(100 / len(answerText)) #dynamically sized
        canvas.create_text(mode.width / 2, mode.height / 2 + mode.height / 6, text = answerText, 
                        fill = 'white', width = mode.width - mode.margin - 350,
                        font = f'Helvetica {textSize} bold', justify = 'center')

    #draws the right and wrong buttons
    def drawButtons(mode, canvas):
        mode.rightButton.updateCoordinates(mode.margin + 15, mode.height - mode.height // 6, mode.width // 5,
                                mode.height - mode.margin - 15)
        mode.wrongButton.updateCoordinates(mode.width / 5 + 15, mode.height - mode.height / 6,
                                mode.width / 5 + 15 + (mode.width / 5 - mode.margin - 15), 
                                mode.height - mode.margin - 15)
        #right button
        canvas.create_rectangle(mode.rightButton.x0, mode.rightButton.y0,
                                mode.rightButton.x1, mode.rightButton.y1,
                                fill = mode.forestGreen, width = '5')
        canvas.create_text((mode.rightButton.x0 + mode.rightButton.x1) / 2,
            (mode.rightButton.y0 + mode.rightButton.y1) / 2, text = "Correct",
            font = "times 24 bold")
        #wrong button
        canvas.create_rectangle(mode.wrongButton.x0, mode.wrongButton.y0,
                                mode.wrongButton.x1, mode.wrongButton.y1,
                                fill = mode.darkRed, width = '5')
        canvas.create_text((mode.wrongButton.x0 + mode.wrongButton.x1) / 2,
            (mode.wrongButton.y0 + mode.wrongButton.y1) / 2, text = "Incorrect",
            font = "times 24 bold")

    def redrawAll(mode, canvas):
        mode.quitButton.updateCoordinates(mode.width - mode.margin - 80, 
                                mode.height - mode.margin - 40, mode.width - mode.margin - 10,
                                mode.height - mode.margin - 10)
        canvas.create_rectangle(0, 0, mode.width, mode.height, fill = mode.gray)
        canvas.create_rectangle(mode.margin, mode.margin, 
                            mode.width - mode.margin, mode.height - mode.margin, 
                            fill = mode.backgroundColor, width = 10)
        canvas.create_rectangle(mode.quitButton.x0, mode.quitButton.y0,
                                mode.quitButton.x1, mode.quitButton.y1, fill = 'pink',
                                width = '3')
        canvas.create_text((mode.quitButton.x0 + mode.quitButton.x1) / 2,
            (mode.quitButton.y0 + mode.quitButton.y1) / 2, text = "QUIT",
            font = "times 16 bold")
        mode.drawPracticeClue(canvas)
        mode.drawOverlay(canvas)
        if(mode.showAnswer):
            mode.drawAnswer(canvas)
            mode.drawButtons(canvas)