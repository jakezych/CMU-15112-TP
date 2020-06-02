from cmu_112_graphics import *
from tkinter import *
from nltk.corpus import wordnet
from broad_categories import *
from clue_dictionary import *
from animation_helpers import *
from menu_mode import *
from game_mode import *
from threading import Timer,Thread,Event
import nltk
import string
import random
import time
#handles all of the logic and animation for lightning mode

#separate thread used to keep track of the player's time left
class gameTimer(Thread):
    def __init__(self, timeLeft):
        Thread.__init__(self)
        self.timeLeft = timeLeft #in milliseconds
        self.exit = False
    
    #updates the current time every second
    def run(self):
        while self.timeLeft > 0:
            time.sleep(1)
            self.timeLeft -= 1000
            if(self.exit):
                return
        return

    #pauses the timer
    def pause(self, pauseTime):
        time.sleep(pauseTime)

    #adds time to timer
    def addTime(self, newTime):
        self.timeLeft += newTime

    #removes time from timer
    def decreaseTime(self, newTime):
        self.timeLeft -= newTime

    #ends the timer
    def end(self):
        self.exit = True

class LightningMode(Mode):
    def appStarted(mode):
        mode.gray = rgbString(192, 192, 192) 
        mode.purple = rgbString(77, 18, 161)
        mode.gold = rgbString(255, 215, 0)
        mode.vanilla = rgbString(245, 231, 186) 
        mode.margin = 40
        mode.wpm = 200 #average reading speed for a human
        mode.quitButton = Button(mode.width - 64, mode.height - 28,
                                 mode.width - 8, mode.height - 6)
        mode.returnButton = Button(mode.width / 2 - mode.width / 6, 
                                mode.height - mode.height / 6,
                                mode.width / 2 + mode.width / 6,
                                mode.height - mode.height / 12)

    def initializeGame(mode, profile):
        mode.game = Game()
        mode.round = 1
        mode.inClue = False
        mode.inFinalScreen = False
        mode.clueRow = -1
        mode.clueCol = -1
        mode.gameTimer = gameTimer(10000*6)
        mode.gameTimer.start()
        mode.readingPeriod = None #how long the user is given to read a clue
        mode.totalPeriod = None
        mode.score = 0
        mode.answerable = False #if the user is able to buzz in
        mode.profile = profile
        mode.leaderboard = [] #list of tuples (username, score)

    #gets the current time left and returns it as a string in the form of (minute:seconds)
    def currentTime(mode, currentTime):
        seconds = currentTime // 1000
        minutes = seconds // 60
        seconds = seconds - 60*minutes
        if(seconds < 10):
            return str(minutes) + ":0" + str(seconds)
        else:
            return str(minutes) + ":" + str(seconds)

    #calculates the number of words in a clue in order to determine how long the
    #timer should be paused.
    def calculateWords(mode, clue):
        clueText = clue.question
        clueTokens = nltk.word_tokenize(clueText)
        count = 0
        for token in clueTokens:
            if(token[0] in string.ascii_letters or token[0] in string.digits):
                count += 1
        return count

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

    def mousePressed(mode, event):
        mode.quitButton.updateCoordinates(mode.width - 64, mode.height - 28,
                                 mode.width - 8, mode.height - 6)           
        mode.returnButton.updateCoordinates(mode.width / 2 - mode.width / 6, 
                                mode.height - mode.height / 6,
                                mode.width / 2 + mode.width / 6,
                                mode.height - mode.height / 12)     
        if(not mode.inClue):
            #quit button bounds check
            if(event.x > mode.quitButton.x0 and event.x < mode.quitButton.x1 and
               event.y > mode.quitButton.y0 and event.y < mode.quitButton.y1):
                mode.inFinalScreen = True
                mode.gameTimer.end()
                mode.updateProfileScore()
                mode.initializeLeaderboard()
            mode.clueRow, mode.clueCol = mode.getCell(event.x, event.y)
            #clue clicked on check
            if(mode.clueRow >= 1 and mode.clueCol >= 0 and 
              not mode.game.board[mode.clueRow][mode.clueCol].isAnswered and 
              not mode.inFinalScreen):
                mode.inClue = True
                wordCount = mode.calculateWords(mode.game.board[mode.clueRow][mode.clueCol])
                #1 second is given at the very least
                #time based off the average reading speed of a human
                mode.readingPeriod = int((wordCount / mode.wpm) * 1000 * 60) + 1000 #milliseconds
                mode.totalPeriod = mode.readingPeriod
        if(mode.inFinalScreen):
            #return button bounds check
            if(event.x > mode.returnButton.x0 and event.x < mode.returnButton.x1 
               and event.y > mode.returnButton.y0 and 
               event.y < mode.returnButton.y1):
               mode.app.setActiveMode(mode.app.menuMode)

    def keyPressed(mode, event):
        if(mode.answerable and event.key == "Enter"):
            mode.processAnswer()
            mode.answerable = False

    def timerFired(mode):
        if(mode.gameTimer.timeLeft == 0):
            mode.inFinalScreen = True
            mode.gameTimer.end()
            mode.updateProfileScore()
            if(mode.leaderboard == []):
                mode.initializeLeaderboard()
        #decrement time in reading period
        if(mode.readingPeriod != None):
            time.sleep(1)
            mode.readingPeriod -= 1000
            if(mode.readingPeriod <= 0):
                mode.readingPeriod = None
                #add back the reading period to the timer
                mode.gameTimer.addTime(mode.totalPeriod)
                mode.answerable = True

    #initializes leaderboard list with tuples of top 5 scores and the profile name
    def initializeLeaderboard(mode):
        f = open("profiles.txt", "r+")
        contents = f.read()
        f.close()
        contentsList = contents.splitlines()
        step = len(broadCategoryNames) + 2
        #step is determined by the number of lines between each profile
        for i in range(0, len(contentsList), step):
            profileLine = contentsList[i].split(',')
            profileName = profileLine[0]
            profileScore = contentsList[i + (step - 1)]
            mode.leaderboard.append((profileName, int(profileScore)))
        mode.leaderboard.sort(key = lambda tup: tup[1], reverse = True)
        if(len(mode.leaderboard) > 5):
            mode.leaderboard = mode.leaderboard[:5]

    #updates the profile file with the user's new score
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
        oldScoresDict, oldHighScore = mode.oldScores(contents)
        for line in contents.splitlines():
            if(line == f"{mode.profile[0]},{mode.profile[1]}"):
                inProfile = True
                #skip to next line
                continue
            if(inProfile):
                w.write(f"{mode.profile[0]},{mode.profile[1]}" + "\n")
                for category in oldScoresDict:
                    oldCorrect, oldAnswered = oldScoresDict[category]
                    w.write(f"{category},{str(oldCorrect)},{str(oldAnswered)}" + "\n")
                inProfile = False
        if(mode.score > int(oldHighScore)):
            w.write(str(mode.score) + "\n")
        else:
            w.write(oldHighScore + "\n")
        w.close()
        mode.addRestOfProfiles(contents)

    #returns a dictionary mapping each category to the old scores and the old score
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
        a.write("\n".join(contentsList))
        a.write("\n")
        a.close()

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
        userAnswer = simpledialog.askstring(" ", "Answer:")
        if(userAnswer == None):
            userAnswer = ''
        correctAnswer = mode.game.board[mode.clueRow][mode.clueCol].answer
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
            mode.score += int(currentClue.value)
            mode.changeTime(currentClue.value, "add")
        else:
            currentClue.correct = False
            mode.changeTime(currentClue.value, "subtract")
        currentClue.isAnswered = True
        mode.inClue = False
        mode.checkForNewRound()

    #check for and process round endings
    def checkForNewRound(mode):        
        if(mode.checkFinished()):
            #alternate rounds 
            if(mode.round == 1):
                mode.game.initializeRound('2')
                mode.round = 2
            else:
                mode.game.initializeRound('1')
                mode.round = 1

    #checks if all the clues in the round have been answered
    def checkFinished(mode):
        for i in range(1, len(mode.game.board)):
            for j in range(len(mode.game.board[i])):
                #if there exists a single not answered clue, game is not done
                if(not mode.game.board[i][j].isAnswered):
                    return False
        return True

    #changes time on the timer based on value of clue
    def changeTime(mode, value, direction):
        time = 0 #milliseconds
        # $200, $400
        if(value <= 400):
            time = 2000
        # $600, $800
        elif(value <= 800):
            time = 3000
        # $1000, $1200
        elif(value <= 1200):
            time = 4000
        # $1600, $20009
        else:
            time = 5000
        if(direction == "add"):
            mode.gameTimer.addTime(time)
        else:
            #decrease the time by 1 less than you would normally add
            mode.gameTimer.decreaseTime(time - 1000)

    def drawClue(mode, canvas):
        canvas.create_rectangle(0, 0, mode.width, mode.height, fill = mode.gray)
        canvas.create_rectangle(mode.margin, mode.margin, 
                            mode.width - mode.margin, mode.height - mode.margin, 
                            fill = mode.purple, width = 10)
        clueText = mode.game.board[mode.clueRow][mode.clueCol].question.upper()
        textSize = 26 + int(500 / len(clueText)) #dynamically sized
        canvas.create_text(mode.width / 2, mode.height / 2, text = clueText, 
                        fill = 'white', width = mode.width - mode.margin - 350,
                        font = f'Helvetica {textSize} bold', justify = 'center')
        if(mode.readingPeriod == None):
            canvas.create_rectangle(5, mode.height - 6, 145, mode.height - 32, 
                                width = '2', fill = 'white')
            canvas.create_text(75, mode.height - 19,
                            text = "TIME LEFT " + mode.currentTime(mode.gameTimer.timeLeft),
                            font = "Helvetica 18 bold")
            canvas.create_text(mode.width / 2, mode.height / 2 + mode.height / 4,
                                text = "PRESS ENTER TO BUZZ IN",
                                fill = 'white', font = 'Helvetica 24 bold')
        if(mode.readingPeriod != None):
            canvas.create_text(mode.width / 2, mode.height / 2 + mode.height / 4,
                                text = "READING PERIOD: " + mode.currentTime(mode.readingPeriod),
                                fill = 'white', font = 'Helvetica 26 bold')


    def drawBoard(mode, canvas):
        cellWidth = (mode.width - mode.margin * 2) / mode.game.cols 
        for i in range(len(mode.game.board)):
            for j in range(len(mode.game.board[0])):
                cellFill = mode.gold
                x0, y0, x1, y1 = mode.getCellBounds(i, j)
                canvas.create_rectangle(x0, y0, x1, y1, width = 10, 
                                        fill = mode.purple)
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

    def drawLeaderboard(mode, canvas):
        #leaderboard box
        canvas.create_text(mode.width / 2, mode.height / 18, text = "LEADERBOARD",
                            font = 'Helvetica 32 bold')
        canvas.create_rectangle(mode.width / 3, mode.height / 10, 
                                mode.width - mode.width / 3,
                                mode.height - mode.height / 3, fill = 'white',
                                width = '3')
        #side bar
        canvas.create_line(mode.width / 2 + mode.width / 12, mode.height / 10,
                           mode.width / 2 + mode.width / 12, mode.height - mode.height / 3, 
                           width = '3')
        boxHeight = mode.height - mode.height / 3 - mode.height / 10
        boxStep = boxHeight / 6
        #dividing lines
        for i in range(6):
            canvas.create_line(mode.width / 3, mode.height / 10 + i*boxStep,
                               mode.width - mode.width / 3, mode.height / 10 + i*boxStep,
                               width = '3')
        #description text
        canvas.create_text((mode.width / 3 + mode.width / 2 + mode.width / 12) / 2, 
                           mode.height / 10 + boxStep / 2,
                           text = "Player:", font = 'Helvetica 30 bold')
        canvas.create_text((mode.width - mode.width / 3 + mode.width / 2 + mode.width / 12) / 2,
                            mode.height / 10 + boxStep / 2,
                            text = "$$$", font = 'Helvetica 30 bold')
        #player scores
        for i in range(len(mode.leaderboard)):
            name, score = mode.leaderboard[i]
            canvas.create_text((mode.width / 3 + mode.width / 2 + mode.width / 12) / 2, 
                           mode.height / 10 + (i+1)*boxStep + boxStep / 2,
                           text = name, font = 'Helvetica 30 bold')
            canvas.create_text((mode.width - mode.width / 3 + mode.width / 2 + mode.width / 12) / 2,
                            mode.height / 10 + (i+1)*boxStep + boxStep / 2,
                            text = "$" + str(score), font = 'Helvetica 26 bold')

    def drawFinalScreen(mode, canvas):
        mode.returnButton.updateCoordinates(mode.width / 2 - mode.width / 6, 
                                mode.height - mode.height / 6,
                                mode.width / 2 + mode.width / 6,
                                mode.height - mode.height / 12)
        canvas.create_rectangle(0, 0, mode.width, mode.height, fill = mode.vanilla)
        #user score at bottom
        canvas.create_text(mode.width / 2, mode.height - mode.height / 4,
                           text = mode.profile[0] + ": $" + str(mode.score),
                           font = 'Helvetica 32 bold')
        #return button
        canvas.create_rectangle(mode.returnButton.x0, mode.returnButton.y0,
                                mode.returnButton.x1, mode.returnButton.y1, 
                                width = '5', fill = 'pink')
        canvas.create_text(mode.width / 2, mode.height - mode.height / 8, 
        text = "Return to Menu", font = 'Helvetica 32 bold')
        mode.drawLeaderboard(canvas)

    def redrawAll(mode, canvas):
        mode.quitButton.updateCoordinates(mode.width - 64, mode.height - 28,
                                 mode.width - 8, mode.height - 6)  
        canvas.create_rectangle(0, 0, mode.width, mode.height, 
                                fill = mode.gray)
        canvas.create_rectangle(mode.quitButton.x0, mode.quitButton.y0, 
                                mode.quitButton.x1, mode.quitButton.y1, 
                                fill = 'pink', width = '2')
        canvas.create_text(mode.width - 36, mode.height - 17, text = "QUIT",
                           font = "Helvetica 16 bold")
        canvas.create_rectangle(5, mode.height - 6, 145, mode.height - 32, 
                                width = '2', fill = 'white')
        canvas.create_text(75, mode.height - 19,
                           text = "TIME LEFT " + mode.currentTime(mode.gameTimer.timeLeft),
                           font = "Helvetica 18 bold")
        canvas.create_rectangle(mode.width / 2 - 70, mode.height - 6, 
                                mode.width / 2 + 70, mode.height - 32,
                                width = '2', fill = 'white')
        canvas.create_text(mode.width / 2, mode.height - mode.margin / 2,
                           text = "SCORE: $" + str(mode.score),
                           font = "Helvetica 18 bold")
        mode.drawBoard(canvas)
        if(mode.inClue):
            mode.drawClue(canvas)
        elif(mode.inFinalScreen):
            mode.drawFinalScreen(canvas)