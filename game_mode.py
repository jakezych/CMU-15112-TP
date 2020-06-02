from cmu_112_graphics import *
from tkinter import *
from nltk.corpus import wordnet
from broad_categories import *
from clue_dictionary import *
from animation_helpers import *
from menu_mode import *
import nltk
import string
import random
import time

#handles all of the logic and animation for the regular game mode
class Game(object):
    def __init__(self):
        self.rows = 6
        self.cols = 6
        self.board = [[None] * self.cols for rows in range(self.rows)]
        self.initializeRound('1')
        self.finalClue = None
        self.initializeFinalClue()

    #initializes the board with clues from the selected round (1,2,3)
    def initializeRound(self, curLevel):
        self.board = [[None] * self.cols for rows in range(self.rows)]
        j = 0
        while(j < 6):
            categoryList = list(clueDict)
            randCategoryIndex = random.randint(0, len(categoryList) - 1)
            randCategory = categoryList[randCategoryIndex]
            dateList = list(clueDict[randCategory])
            randDateIndex = random.randint(0, len(dateList) - 1)
            randDate = dateList[randDateIndex] 
            clueList = clueDict[randCategory][randDate]
            if(len(clueList) < 5 or 
               (clueList[0].level != curLevel and 
               clueList[len(clueList) - 1] != curLevel)): 
               #unplayable if there are not 5 clues or if none of the clues 
               #are of the correct round
                continue
            else:
                #first element in col is the category name
                self.board[0][j] = clueList[0].category 
                i = 1
                #handles the case where the same category is used twice in 
                #one airdate. AKA clue list contains clues of multiple rounds
                while(i < 6):
                    for clueIndex in range(1, len(clueList) + 1):
                        if(clueList[clueIndex - 1].level == curLevel):
                            self.board[i][j] = clueList[clueIndex - 1]
                            i += 1
                j += 1

    #selects the final round clue
    def initializeFinalClue(self):
        while True:
            categoryList = list(clueDict)
            randCategoryIndex = random.randint(0, len(categoryList) - 1)
            randCategory = categoryList[randCategoryIndex]
            dateList = list(clueDict[randCategory])
            randDateIndex = random.randint(0, len(dateList) - 1)
            randDate = dateList[randDateIndex] 
            clueList = clueDict[randCategory][randDate]
            if(clueList[0].level == '3'):
                self.finalClue = clueList[0]   
                return

class GameMode(Mode):
    def appStarted(mode):
        mode.gray = rgbString(192, 192, 192) 
        mode.darkBlue = rgbString(3, 0, 199)
        mode.gold = rgbString(255, 215, 0)
        mode.vanilla = rgbString(245, 231, 186) 
        mode.margin = 35
        mode.quitButton = Button(mode.width - 64, mode.height - 28,
                                 mode.width - 8, mode.height - 6)
        mode.returnButton = Button(mode.width / 2 - mode.width / 6, 
                                mode.height - mode.height / 6,
                                mode.width / 2 + mode.width / 6,
                                mode.height - mode.height / 12)
        mode.overrideButton = Button(8, mode.height - 28, 86, mode.height - 6)

    def initializeGame(mode, profile):
        mode.game = Game()
        mode.round = 1
        mode.inClue = False
        mode.inFinalRound = False
        mode.inFinalScreen = False
        mode.clueRow = -1
        mode.clueCol = -1
        #keeps track of score throughout game
        mode.scoreDict = mode.initializeScoreDict()
        mode.profile = profile
        mode.score = (0,0)

    def initializeScoreDict(mode):
        scoreDict = dict()
        for broadCategory in broadCategoryNames:
            #tuple is (number of correct, number of attempted)
            scoreDict[broadCategory] = [0,0]
        return scoreDict

    def mousePressed(mode, event):
        mode.quitButton.updateCoordinates(mode.width - 64, mode.height - 28,
                                 mode.width - 8, mode.height - 6)
        mode.returnButton.updateCoordinates(mode.width / 2 - mode.width / 6, 
                                mode.height - mode.height / 6,
                                mode.width / 2 + mode.width / 6,
                                mode.height - mode.height / 12)
        mode.overrideButton.updateCoordinates(8, mode.height - 28, 
                                              86, mode.height - 6)   
        if(not mode.inClue):
            #quit button bounds check
            if(event.x > mode.quitButton.x0 and event.x < mode.quitButton.x1 and
               event.y > mode.quitButton.y0 and event.y < mode.quitButton.y1):
                mode.inFinalScreen = True
                mode.updateProfileScore()
                mode.calculateScore()
            #override button bounds check
            if(event.x > mode.overrideButton.x0 and event.x < mode.overrideButton.x1 and
               event.y > mode.overrideButton.y0 and event.y < mode.overrideButton.y1):
               currentClue = mode.game.board[mode.clueRow][mode.clueCol]
               currentClue.correct = True
               #update score dictionary
               mode.scoreDict[currentClue.broadCategory][0] += 1
            mode.clueRow, mode.clueCol = mode.getCell(event.x, event.y)
            #clue clicked on check
            if(mode.clueRow >= 1 and mode.clueCol >= 0 and 
              not mode.game.board[mode.clueRow][mode.clueCol].isAnswered and 
              not mode.inFinalScreen):
                mode.inClue = True
                mode.processAnswer()
        if(mode.inFinalScreen):
            #return button bounds check
            if(event.x > mode.returnButton.x0 and event.x < mode.returnButton.x1 
               and event.y > mode.returnButton.y0 and 
               event.y < mode.returnButton.y1):
               mode.app.setActiveMode(mode.app.menuMode)

    #from http://www.cs.cmu.edu/~112/notes/notes-animations-part1.html#mvc
    def pointInGrid(mode, x, y):
        #return True if (x, y) is inside the grid defined by mode.
        return ((mode.margin <= x <= mode.width-mode.margin) and
                (mode.margin <= y <= mode.height-mode.margin))

    #from http://www.cs.cmu.edu/~112/notes/notes-animations-part1.html#mvc
    def getCell(mode, x, y):
        #return (row, col) in which (x, y) occurred or (-1, -1) if outside grid.
        if (not mode.pointInGrid(x, y)):
            return (-1, -1)
        cellWidth  = (mode.width - mode.margin * 2) / mode.game.cols
        cellHeight = (mode.height - mode.margin * 2) / mode.game.rows 
        row = int((y - mode.margin) / cellHeight)
        col = int((x - mode.margin) / cellWidth)
        return (row, col)

    #from http://www.cs.cmu.edu/~112/notes/notes-animations-part1.html#mvc
    def getCellBounds(mode, row, col):
        #returns (x0, y0, x1, y1) corners/bounding box of given cell in grid
        columnWidth =  (mode.width - mode.margin * 2) / mode.game.cols 
        rowHeight = (mode.height - mode.margin * 2) / mode.game.rows
        x0 = mode.margin + col * columnWidth
        x1 = mode.margin + (col + 1) * columnWidth
        y0 = mode.margin + row * rowHeight
        y1 = mode.margin + (row + 1) * rowHeight
        return (x0, y0, x1, y1)

    #change each tag into either noun (n), verb(v), adjective(a), or adverb (r) 
    #so that it can be interpreted by synset
    def updateTokenLabels(mode, tokens):
        for i in range(len(tokens)):
            currentTag = tokens[i][1]
            if(currentTag[0] == "V"):
                tokens[i] = (tokens[i][0], "v")
            #can only use singular nouns for synset comparisons
            elif(currentTag == "NN"):
                tokens[i] = (tokens[i][0], "n")
            elif(currentTag[0] == "J"):
                tokens[i] = (tokens[i][0], "a")
            elif(currentTag[0] == "R"):
                tokens[i] = (tokens[i][0], "r")
        return tokens

    #extract a standardized string from a list of tokens ignoring determiners
    def detokenize(mode, tokens):
        result = ""
        for i in range(len(tokens)):
            if(tokens[i][1] == "DT"):
                pass
            else:
                result += stripText(tokens[i][0])
        return result

    #checks similarity values of two token lists to see if they are similar
    #enough to be consider correct
    def checkSimilarity(mode, userAnswerTokens, correctAnswerTokens):
        i = 0
        j = 0
        currentUserToken = None
        currentCorrectToken = None
        userSynTokens = mode.updateTokenLabels(userAnswerTokens)
        correctSynTokens = mode.updateTokenLabels(correctAnswerTokens)
        while(i < len(userSynTokens) and j < len(correctSynTokens)):
            if(userSynTokens[i][1] in ["n", "v", "r", "a"]):
                currentUserToken = userSynTokens[i][0]
                #create a synonym net based on token and tag
                try:
                    userNet = wordnet.synset(currentUserToken + '.' + 
                                             userSynTokens[i][1] + '.01')
                except:
                    return False
            else:
                i += 1
            if(correctSynTokens[j][1] in ["n", "v", "r", "a"]):
                currentCorrectToken = correctSynTokens[j][0]
                #create a synonym net based on token and tag
                try:
                    correctNet = wordnet.synset(currentCorrectToken + '.' + 
                                                correctSynTokens[j][1] + '.01')
                except:
                    return False
            else:
                j += 1
            if(currentUserToken != None and currentCorrectToken != None):
                #value between [0-1] with 1 being exactly the same and 
                #0 being completely not similar
                similarityRating = correctNet.wup_similarity(userNet)
                if(similarityRating == None or similarityRating < .95):
                    return False
                #if there are other words to compare with each other,
                #increase index, otherwise increase index of both to terminate 
                #loop
                if(i + 1 < len(userSynTokens)):
                    i += 1
                elif(j + 1 < len(correctSynTokens)):
                    j += 1
                else:
                    i += 1
                    j += 1
        #if comparisons were made and false was never returned, they are similar
        if(currentUserToken != None and currentCorrectToken != None):
            return True

    #handles checking if user and correct answer are same/similar
    def checkCorrectness(mode, userAnswerTokens, correctAnswerTokens, 
                        hasDigit, hasProperNoun):
        #incorrect if player does not answer
        if(userAnswerTokens == []):
            return False
        #check if the answer is exactly correct only if there is a proper noun
        #or digits are involved
        userAnswer = mode.detokenize(userAnswerTokens)
        correctAnswer = mode.detokenize(correctAnswerTokens)
        if(userAnswer == correctAnswer):
            return True
        else: 
            #if not exactly correct and is proper noun or digit, similarity 
            #should not be checked. Proper nouns and numbers do not have synonym
            if(hasProperNoun or hasDigit):
                return False
            else:
                isSimilar = mode.checkSimilarity(userAnswerTokens,
                                                 correctAnswerTokens)
                if(isSimilar):
                    return True
                else:
                    return False

    #handles asking,saving, and processing the user's answer to a clue 
    def processAnswer(mode):
        time.sleep(.1)
        userAnswer = simpledialog.askstring(" ", "Answer:")
        if(userAnswer == None):
            userAnswer = ''
        if(not mode.inFinalRound):
            correctAnswer = mode.game.board[mode.clueRow][mode.clueCol].answer
        else:
            correctAnswer = mode.game.finalClue.answer
        #process the user answer and correct answer into lists of labeled tokens
        userAnswerTokens = nltk.word_tokenize(userAnswer)
        userLabeledTokens = nltk.pos_tag(userAnswerTokens)
        correctAnswerTokens = nltk.word_tokenize(correctAnswer)
        correctLabeledTokens = nltk.pos_tag(correctAnswerTokens)
        #check answer after processing
        mode.checkAnswer(userLabeledTokens, correctLabeledTokens)

    #checks if the answer is correct for rounds 1 and 2
    def checkAnswer(mode, userAnswerTokens, correctAnswerTokens):
        hasProperNoun = False
        hasDigit = False            
        #check if proper noun or digit is in correct answer
        for i in range(len(correctAnswerTokens)):
            currentTag = correctAnswerTokens[i][1]
            if(currentTag == "NNP" or currentTag == "NNPS"):
                hasProperNoun = True
            elif(currentTag == "CD"):
                hasDigit = True
        #if clue contains quotes, then the answer must be exactly correct
        if('\"' in mode.game.board[mode.clueRow][mode.clueCol].category):
            hasProperNoun = True
        isCorrect = mode.checkCorrectness(userAnswerTokens, correctAnswerTokens, 
                                    hasDigit, hasProperNoun)
        currentClue = mode.game.board[mode.clueRow][mode.clueCol]
        if(isCorrect):
            currentClue.correct = True
            #increase the correctly answered in the score dictionary
            mode.scoreDict[currentClue.broadCategory][0] += 1
        else:
            currentClue.correct = False
        #increase the number of attempted in the score dictionary
        mode.scoreDict[currentClue.broadCategory][1] += 1
        currentClue.isAnswered = True
        mode.inClue = False
        mode.checkForNewRound()

    #check for and process round endings
    def checkForNewRound(mode):        
        if(mode.inFinalRound):
            mode.game.finalClue.isAnswered = True
            mode.inFinalRound = False
            mode.inFinalScreen = True
            mode.updateProfileScore()
            mode.calculateScore()
        elif(mode.checkFinished()):
            mode.round += 1
            #change view type for final jeopardy
            if(mode.round == 3):
                mode.inFinalRound = True
                mode.processAnswer()
            else:
                mode.game.initializeRound(str(mode.round))

    #checks if all the clues in the round have been answered
    def checkFinished(mode):
        for i in range(1, len(mode.game.board)):
            for j in range(len(mode.game.board[i])):
                #if there exists a single not answered clue, game is not done
                if(not mode.game.board[i][j].isAnswered):
                    return False
        return True

    #updates the current profiles score and then adds back all the other profiles
    #to the profiles file
    def updateProfileScore(mode):
        #no profile is selected, so score is not updated
        if(mode.profile[0] == "User"):
            return
        f = open("profiles.txt", "r+")
        contents = f.read()
        f.close()
        w = open("profiles.txt", "w+")
        #determines if you are currently in the necessary profile
        inProfile = False
        oldScoresDict, oldHighScoreLine = mode.oldScores(contents)
        for line in contents.splitlines():
            if(line == f"{mode.profile[0]},{mode.profile[1]}"):
                inProfile = True
                #skip to next line
                continue
            if(inProfile):
                w.write(f"{mode.profile[0]},{mode.profile[1]}" + "\n")
                for category in mode.scoreDict:
                    correct, answered = mode.scoreDict[category]
                    oldCorrect, oldAnswered = oldScoresDict[category]
                    totalCorrect = int(correct) + int(oldCorrect)
                    totalAnswered = int(answered) + int(oldAnswered)
                    w.write(f"{category},{str(totalCorrect)},{str(totalAnswered)}" + "\n")
                inProfile = False
        w.write(oldHighScoreLine)
        w.close()
        mode.addRestOfProfiles(contents)

    #returns a dictionary mapping each category to the old scores 
    #and the old high score for lightning mode
    def oldScores(mode, contents):
        oldScoresDict = dict()
        #find the starting line for the profile
        lineIndex = 0
        highScoreIndex = 0 
        for line in contents.splitlines():
            if(line == f"{mode.profile[0]},{mode.profile[1]}"):
                lineIndex = contents.splitlines().index(line)
                highScoreIndex = lineIndex + len(broadCategoryNames) + 1
                break
        currentProfile = contents.splitlines()[lineIndex + 1: highScoreIndex]
        highScoreLine = contents.splitlines()[highScoreIndex]
        #for each line corresponding to a category, add its data to the dict
        for line in currentProfile:
            lineData = line.split(",")
            oldScoresDict[lineData[0]] = (lineData[1], lineData[2])
        return oldScoresDict, highScoreLine

    #add back rest of profiles and data after updating the selected profile
    def addRestOfProfiles(mode, contents):
        a = open("profiles.txt", "a+")
        contentsList = contents.splitlines()
        for line in contentsList:
            #find the index of the old profile
            if(line == f"{mode.profile[0]},{mode.profile[1]}"):
                lineIndex = contentsList.index(line)
                break
        #remove the profile and its associated data
        contentsList = (contentsList[:lineIndex] + 
                       contentsList[lineIndex + len(broadCategoryNames) + 2:])
        a.write("\n")
        a.write("\n".join(contentsList))
        a.write("\n")
        a.close()

    #calculates the score for the game based on the scoreDict
    def calculateScore(mode):
        totalAnswered = 0
        totalRight = 0
        for category in mode.scoreDict:
            totalRight += mode.scoreDict[category][0]
            totalAnswered += mode.scoreDict[category][1]
        mode.score = (totalRight, totalAnswered)

    def drawFinalScreen(mode, canvas):
        mode.returnButton.updateCoordinates(mode.width / 2 - mode.width / 6, 
                                mode.height - mode.height / 6,
                                mode.width / 2 + mode.width / 6,
                                mode.height - mode.height / 12)
        canvas.create_rectangle(0, 0, mode.width, mode.height, fill = mode.vanilla)
        canvas.create_rectangle(mode.width / 2 - mode.width / 4, 
                                mode.height / 2 - 50,
                                mode.width / 2 + mode.width / 4,
                                mode.height - mode.height / 4,
                                fill = 'white', width = '2')
        canvas.create_text(mode.width / 2, mode.height / 2, 
        text = f"Correct: {mode.score[0]}",
        fill = "black", font = 'Helvetica 40 bold')
        canvas.create_text(mode.width / 2, mode.height / 2 + 50, 
        text = f"Answered: {mode.score[1]}",
        fill = "black", font = 'Helvetica 40 bold')
        if(mode.score[1] == 0):
            accuracy = 0.0
        else:
            accuracy = (int(mode.score[0]) / int(mode.score[1])) * 100
        canvas.create_text(mode.width / 2, mode.height / 2 + 100, 
        text = f"Accuracy: {str(round(accuracy, 2))}%",
        fill = "black", font = 'Helvetica 40 bold')
        canvas.create_rectangle(mode.returnButton.x0, mode.returnButton.y0,
                                mode.returnButton.x1, mode.returnButton.y1, 
                                width = '5', fill = 'pink')
        canvas.create_text(mode.width / 2, mode.height - mode.height / 8, 
        text = "Return to Menu", font = 'Helvetica 32 bold')
        if(mode.game.finalClue.isAnswered):
            size = 12 + len(mode.game.finalClue.answer) // 24
            canvas.create_text(mode.width / 2, mode.height / 4, 
            text = "Correct Final Jeopardy Answer: " + mode.game.finalClue.answer,
            fill = "black", font = 'Helvetica 40 bold')
    
    def drawFinalRound(mode, canvas):
        canvas.create_rectangle(0, 0, mode.width, mode.height, fill = mode.gray)
        canvas.create_rectangle(mode.margin, mode.margin, 
                            mode.width - mode.margin, mode.height - mode.margin, 
                            fill = mode.darkBlue, width = 10)
        clueText = mode.game.finalClue.question.upper()
        textSize = 26 + int(500 / len(clueText)) #dynamically sized
        canvas.create_text(mode.width / 2, mode.height / 2, text = clueText, 
                        fill = 'white', width = mode.width - mode.margin - 350,
                        font = f'Helvetica {textSize} bold', justify = 'center')
        canvas.create_text(mode.width / 2, mode.height / 4, fill = mode.gold,
                           text = "FINAL JEOPARDY:", justify = 'center',
                           font = 'Helvetica 50 bold')

    def drawClue(mode, canvas):
        canvas.create_rectangle(0, 0, mode.width, mode.height, fill = mode.gray)
        canvas.create_rectangle(mode.margin, mode.margin, 
                            mode.width - mode.margin, mode.height - mode.margin, 
                            fill = mode.darkBlue, width = 10)
        clueText = mode.game.board[mode.clueRow][mode.clueCol].question.upper()
        textSize = 26 + int(500 / len(clueText)) #dynamically sized
        canvas.create_text(mode.width / 2, mode.height / 2, text = clueText, 
                        fill = 'white', width = mode.width - mode.margin - 350,
                        font = f'Helvetica {textSize} bold', justify = 'center')

    def drawBoard(mode, canvas):
        cellWidth = (mode.width - mode.margin * 2) / mode.game.cols 
        for i in range(len(mode.game.board)):
            for j in range(len(mode.game.board[0])):
                cellFill = mode.gold
                x0, y0, x1, y1 = mode.getCellBounds(i, j)
                canvas.create_rectangle(x0, y0, x1, y1, width = 10, 
                                        fill = mode.darkBlue)
                midX = (x0 + x1) / 2
                midY = (y0 + y1) / 2
                if(i == 0):
                    #set text and size for category
                    categoryText = mode.game.board[i][j] 
                    textSize = int(cellWidth / 9) + len(categoryText) // 50
                else:
                    #set text and size for clue cells
                    if(mode.game.board[i][j].isAnswered):
                        categoryText = mode.game.board[i][j].answer
                        textSize = int(cellWidth / 8) + len(categoryText) // 36
                        if(mode.game.board[i][j].correct):
                            cellFill = rgbString(53, 179, 34)
                        else:
                            cellFill = rgbString(179, 34, 34)
                    else:
                        categoryText = '$' + str(mode.game.board[i][j].value)
                        textSize = int(cellWidth / 4)
                canvas.create_text(midX, midY, text = categoryText,  
                                   fill = cellFill, width = cellWidth - 15,
                                   font = f"Helvetica {textSize} bold",
                                   justify = "center")

    def redrawAll(mode, canvas):   
        mode.quitButton.updateCoordinates(mode.width - 64, mode.height - 28,
                                 mode.width - 8, mode.height - 6)   
        mode.overrideButton.updateCoordinates(8, mode.height - 28, 86, 
                                              mode.height - 6)
        canvas.create_rectangle(0, 0, mode.width, mode.height, 
                                fill = mode.gray)
        canvas.create_rectangle(mode.quitButton.x0, mode.quitButton.y0, 
                                mode.quitButton.x1, mode.quitButton.y1, 
                                fill = 'pink', width = '2')
        canvas.create_text(mode.width - 36, mode.height - 17, text = "QUIT",
                           font = "Helvetica 16 bold")
        canvas.create_rectangle(mode.overrideButton.x0, mode.overrideButton.y0,
                                mode.overrideButton.x1, mode.overrideButton.y1,
                                fill = rgbString(53, 179, 34), width = '2')
        canvas.create_text(46, mode.height - 17, text = "OVERRIDE",
                           font = "Helvetica 13 bold", justify = "center")
        mode.drawBoard(canvas)
        if(mode.inClue):
            mode.drawClue(canvas)
        elif(mode.inFinalRound):
            mode.drawFinalRound(canvas)
        elif(mode.inFinalScreen):
            mode.drawFinalScreen(canvas)
 