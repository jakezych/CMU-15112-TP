from cmu_112_graphics import *
from tkinter import *
from broad_categories import *
import nltk
import string
#handles the creation of the clue/category data structure
#also used to update and reformat the clue/category file

#CITATION: Jeopardy Clues from http://j-archive.com/
class Clue(object):
    def __init__(self, clueId, gameNum, date, level, value, 
                 category, question, answer, broadCategory):
        self.clueId = clueId
        self.gameNum = gameNum
        self.date = date
        self.level = level 
        self.value = value 
        self.category = category
        self.question = question
        self.answer = answer
        self.broadCategory = broadCategory
        self.isAnswered = False
        self.correct = None

#returns a lowercase string of just alphabetical characters
def stripText(s):
    result = ''
    for c in s:
        if(not c in string.whitespace and not c in string.punctuation):
            result += c
    return result.lower()

#checks if clue is unable to be answered without picture or video hint
def checkForMedia(line):
    strippedText = stripText(line)
    if('seenhere' in strippedText or 'heardhere' in strippedText or 'shownhere' in strippedText):
        return True

#repairs the clues and categories of the dataset by fixing the number of quotes
def standardizeQuotes(s):
    s = s[1: len(s) - 1] #removing outer layer of parentheses
    result = ''
    for i in range(len(s) - 1):
        curChar = s[i]
        nextChar = s[i + 1]
        if(curChar == '\"' and nextChar == curChar):
            pass
        else:
            result += curChar
    result += s[len(s) - 1]
    return result

#checks if airdate is pre-point value changes 
def checkDate(airdate):
    if(not airdate[0] in string.digits):
        return False
    year = int(airdate[0:4])
    month = int(airdate[5:7])
    day = int(airdate[8:9])
    #date that values were doubled: 11-26-2001
    return (year <= 2001 and month <= 11 and day < 26)

#standardizes a line of the dataset for play
def repairLine(L):
    if(checkForMedia(L[6])): #if the clue has inaccesible media associated 
        return True
    if('\"' in L[5]):
        L[5] = standardizeQuotes(L[5].strip())
    if('\"' in L[6]):
        L[6] = standardizeQuotes(L[6].strip())
    if('\"' in L[7]):
        L[7] = standardizeQuotes(L[7].strip())
    if(checkDate(L[2])): #all values after 11-26-2001 are doubled
        temp = int(L[4])
        temp *= 2
        L[4] = str(temp)

#creates the clue dictionary reading from a file
def initializeClueList(update):
    f = open('updated_master.txt', 'r+')
    contents = f.read() #storing the clue database in a string to read from
    f.close()
    clueDict = dict()
    broadCategoriesDict = dict()
    if(update): #only update the dataset if user requests 
        updateDataSet()
    for line in contents.splitlines():
        #L[0] = clueID L[1] = gameNum L[2] = date L[3] = level L[4] = value
        #L[5] = category L[6] = question L[7] = answer L[8] = broadCategory
        L = line.split('\t')        
        clue = Clue(L[0], L[1], L[2], L[3], L[4], L[5], L[6], L[7], L[8])
        #map broad category to list of specific category name 
        if(L[8] not in broadCategoriesDict):
            broadCategoriesDict[L[8]] = [L[5]]
        else:
            broadCategoriesDict[L[8]].append(L[5])
        #nested dictionary: each category key maps to a dictionary who's
        #keys are dates. The values of the date keys are the clue lists
        if(L[5] not in clueDict): 
            clueDict[L[5]] = dict() 
            if(L[2] not in clueDict[L[5]]):
                clueDict[L[5]][L[2]] = [clue]
        else:
            if(L[2] not in clueDict[L[5]]):
                clueDict[L[5]][L[2]] = [clue]
            else:
                clueDict[L[5]][L[2]].append(clue)
    return clueDict, broadCategoriesDict

#changes the daily double value to what it would have been if regular game
def fixDailyDoubleValues():
    for category in clueDict:
        for date in clueDict[category]:
            clueList = clueDict[category][date]
            #unnecessary to fix values if clues will not be used in game
            #if(len(clueList) < 5): 
                #continue
            #setting the increment value for the clues
            if(clueList[0].level == '1'):
                step = 200
            else:
                step = 400
            for i in range(len(clueList)):
                correctValue = (i+1)*step 
                #update values in if incorrect value
                if(clueList[i].value != correctValue):
                    clueList[i].value = correctValue

#standardizes the dataset and writes to a new file which will be used to 
def updateDataSet():
    f = open('old_master.txt', 'r')
    w = open('updated_master.txt', 'w+')
    contents = f.read() 
    f.close()
    for line in contents.splitlines():
        L = line.split('\t')   
        broadCategory = assignBroadCategory(L[5])
        if(repairLine(L)): #skips media clues
            continue  
        L.append(broadCategory)
        repaired = '\t'.join(L)
        w.write(repaired + '\n')
    w.close() 

#returns the broad category name of a specific category
def assignBroadCategory(category):
    category = category.lower()
    categoryTokens = nltk.word_tokenize(category)
    #any category with quotes in it is considered word play
    if("\"" in category):
        return "Word Play"
    #iterate through each tuple containing set of key words and label
    for (broadCategory, name) in broadCategories: 
        #check if any of the tokens match a key word in the set
        for token in categoryTokens:
            if(token in broadCategory):
                return name
    return "Misc."

update = False
clueDict, broadCategoriesDict = initializeClueList(update)
fixDailyDoubleValues()
