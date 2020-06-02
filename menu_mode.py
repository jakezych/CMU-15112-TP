from cmu_112_graphics import *
from tkinter import *
from nltk.corpus import wordnet
from broad_categories import *
from clue_dictionary import *
from animation_helpers import *
from game_mode import *
import nltk
import string
import random
import time
#handles all of the mode switching and provides a user interface for navigating through all of the modes

class MenuMode(Mode):
    def appStarted(mode):
        mode.lightBlue = rgbString(115, 178, 255)
        mode.vanilla = rgbString(245, 231, 186) 
        mode.gameButton = Button(mode.width / 2 - mode.width / 8, 
                                 mode.height / 5, 
                                 mode.width / 2 + mode.width / 8,
                                 mode.height / 5 + mode.height / 8)
        mode.createProfileButton = Button(mode.width - mode.width / 6, 
                            mode.height - 45, mode.width - 10, mode.height - 10)
        mode.loadProfileButton = Button(mode.width - mode.width / 6, 
                            mode.height - 90, mode.width - 10, mode.height - 55)
        mode.practiceModeButton = Button(mode.width / 2 - mode.width / 8, 
                                         mode.height / 3 + 20,
                                         mode.width / 2 + mode.width / 8,
                                         mode.height / 3 + mode.height / 8 + 20)
        mode.statisticsButton = Button(mode.width / 2 - mode.width / 8, 
                                       mode.height / 2 + 20, 
                                       mode.width / 2 + mode.width / 8,
                                       mode.height / 2 + mode.height / 8 + 20)
        mode.regularGameButton = Button(mode.width / 2 - mode.width / 8,
                                        mode.height / 3,
                                        mode.width / 2 + mode.width / 8,
                                        mode.height / 3 + mode.height / 8)
        mode.lightningModeButton = Button(mode.width / 2 - mode.width / 8,
                                          mode.height / 2 + 20,
                                          mode.width / 2 + mode.width / 8,
                                          mode.height / 2 + mode.height / 8 + 20)
        mode.backButton = Button(mode.width - mode.width / 6, 
                                 mode.height - mode.height / 10,
                                 mode.width - 15,
                                 mode.height - 15)
        mode.infoButton = Button(10, mode.height - 40, 80, mode.height - 10)
        mode.inGameSubMenu = False
        mode.currentProfile = ("User", "Password")

    def checkGameButtonPressed(mode, event):
        mode.gameButton.updateCoordinates(mode.width / 2 - mode.width / 8, 
                                 mode.height / 5, 
                                 mode.width / 2 + mode.width / 8,
                                 mode.height / 5 + mode.height / 8)
        if(event.x > mode.gameButton.x0 and event.x < mode.gameButton.x1 and
           event.y > mode.gameButton.y0 and event.y < mode.gameButton.y1):
           mode.inGameSubMenu = True

    def checkPracticeModeButtonPressed(mode, event):
        mode.practiceModeButton.updateCoordinates(mode.width / 2 - mode.width / 8, 
                                         mode.height / 3 + 20,
                                         mode.width / 2 + mode.width / 8,
                                         mode.height / 3 + mode.height / 8 + 20)
        if(event.x > mode.practiceModeButton.x0 and event.x < mode.practiceModeButton.x1 and
           event.y > mode.practiceModeButton.y0 and event.y < mode.practiceModeButton.y1):
            personalization = messagebox.askyesno("Personalization",
            "Would you like the practice clues to be personalized according to your current statistics?")
            if(personalization):
                if(mode.currentProfile == ("User", "Password")):
                    messagebox.showinfo("Error", "Please Select a Profile for Personalized Mode")
                    return
                mode.app.practiceMode.initializePracticeMode("personalized", mode.currentProfile)
            else:
                mode.app.practiceMode.initializePracticeMode("random", mode.currentProfile)
            mode.app.setActiveMode(mode.app.practiceMode)

    def checkStatisticsButtonPressed(mode, event):
        mode.statisticsButton.updateCoordinates(mode.width / 2 - mode.width / 8, 
                                       mode.height / 2 + 20, 
                                       mode.width / 2 + mode.width / 8,
                                       mode.height / 2 + mode.height / 8 + 20)
        if(event.x > mode.statisticsButton.x0 and event.x < mode.statisticsButton.x1 and
           event.y > mode.statisticsButton.y0 and event.y < mode.statisticsButton.y1):
           mode.app.statisticsMode.initializeProfile(mode.currentProfile)
           mode.app.setActiveMode(mode.app.statisticsMode)
        
    def checkCreateProfilePressed(mode, event):
        mode.createProfileButton.updateCoordinates(mode.width - mode.width / 6, 
                            mode.height - 45, mode.width - 10, mode.height - 10)
        if(event.x > mode.createProfileButton.x0 and 
           event.x < mode.createProfileButton.x1 and 
           event.y > mode.createProfileButton.y0 and 
           event.y < mode.createProfileButton.y1):
           mode.createProfile()

    def checkLoadProfilePressed(mode, event):
        mode.loadProfileButton.updateCoordinates(mode.width - mode.width / 6, 
                            mode.height - 90, mode.width - 10, mode.height - 55)
        if(event.x > mode.loadProfileButton.x0 and 
           event.x < mode.loadProfileButton.x1 and 
           event.y > mode.loadProfileButton.y0 and 
           event.y < mode.loadProfileButton.y1):
           mode.loadProfile()

    def checkRegularGameButtonPressed(mode, event):
        mode.regularGameButton.updateCoordinates(mode.width / 2 - mode.width / 8,
                                                mode.height / 3,
                                                mode.width / 2 + mode.width / 8,
                                                mode.height / 3 + mode.height / 8)
        if(event.x > mode.regularGameButton.x0 and 
           event.x < mode.regularGameButton.x1 and 
           event.y > mode.regularGameButton.y0 and 
           event.y < mode.regularGameButton.y1):
            mode.app.gameMode.initializeGame(mode.currentProfile)
            mode.app.setActiveMode(mode.app.gameMode)

    def checkLightningModeButtonPressed(mode, event):
        mode.lightningModeButton.updateCoordinates(mode.width / 2 - mode.width / 8,
                                                mode.height / 2 + 20,
                                                mode.width / 2 + mode.width / 8,
                                                mode.height / 2 + mode.height / 8 + 20)
        if(event.x > mode.lightningModeButton.x0 and 
           event.x < mode.lightningModeButton.x1 and 
           event.y > mode.lightningModeButton.y0 and 
           event.y < mode.lightningModeButton.y1):
            mode.app.lightningMode.initializeGame(mode.currentProfile)
            mode.app.setActiveMode(mode.app.lightningMode)

    def checkBackButtonPressed(mode, event):
        mode.backButton.updateCoordinates(mode.width - mode.width / 6, 
                                        mode.height - mode.height / 10,
                                        mode.width - 15,
                                        mode.height - 15)
        if(event.x > mode.backButton.x0 and 
           event.x < mode.backButton.x1 and 
           event.y > mode.backButton.y0 and 
           event.y < mode.backButton.y1):
            mode.inGameSubMenu = False

    def checkInfoButtonPressed(mode, event):
        mode.infoButton.updateCoordinates(10, mode.height - 40, 80, mode.height - 10)
        if(event.x > mode.infoButton.x0 and 
           event.x < mode.infoButton.x1 and 
           event.y > mode.infoButton.y0 and 
           event.y < mode.infoButton.y1):
            mode.app.setActiveMode(mode.app.infoMode)

    def mousePressed(mode, event):
        if(mode.inGameSubMenu):
            mode.checkRegularGameButtonPressed(event)
            mode.checkLightningModeButtonPressed(event)
            mode.checkBackButtonPressed(event)
        else:
            mode.checkGameButtonPressed(event)
            mode.checkCreateProfilePressed(event)
            mode.checkLoadProfilePressed(event)
            mode.checkPracticeModeButtonPressed(event)
            mode.checkStatisticsButtonPressed(event)
            mode.checkInfoButtonPressed(event)

    def createProfile(mode):
        f = open("profiles.txt", "r+")
        currentData = f.read()
        f.close()
        w = open("profiles.txt", "a+")
        userName = simpledialog.askstring("username:", "Enter a username [3 - 12] characters:")
        if(userName == None):
            messagebox.showinfo("Error", "Please enter a username")
            return
        userPassword = simpledialog.askstring("password", "Enter a password [3 - 12] characters:")
        if(userPassword == None):
            messagebox.showinfo("Error", "Please enter a password")
            return
        userName = userName.strip()
        userPassword = userPassword.strip()
        #if profile is not valid return
        if(not mode.checkProfileAllowed(userName, userPassword, currentData)):
            w.close()
            return 
        w.write(f"{userName}" + "," +f"{userPassword}" + "\n")
        #add template for future data updates
        for name in broadCategoryNames:
            w.write(name + ",0,0" + "\n")
        w.write("0" + "\n") #highest score in lightning mode
        w.close()
        mode.currentProfile = (userName, userPassword)

    #checks if the profile the user attempted to create is valid
    def checkProfileAllowed(mode, username, password, data):
        if(username.lower() in broadCategoryNames or username.lower() == "user"):
            messagebox.showinfo("Error", "Username not allowed")
            return False
        elif(len(username) < 3 or len(username) > 12 or 
                 len(password) < 3 or len(password) > 12):
            messagebox.showinfo("Error", "Usernames and passwords must be between 3 and 12 characters")
            return False
        for line in data.splitlines():
            L = line.split(",")
            if(username == L[0] and password == L[1]):
                messagebox.showinfo("Error", "Profile Already Exists")
                return False
        return True

    def loadProfile(mode):
        f = open("profiles.txt", "r+")
        currentData = f.read()
        f.close()
        userName = simpledialog.askstring("username:", "Enter your username:")
        if(userName == None):
            return
        userName = userName.strip()
        userPassword = simpledialog.askstring("password", "Enter your password:")
        userPassword = userPassword.strip()
        for line in currentData.splitlines():
            L = line.split(",")
            if(userName.lower() in broadCategoryNames):
                 messagebox.showinfo("Failed", "Could not find account. Try again")
                 return
            if(userName == L[0] and userPassword == L[1]):
                messagebox.showinfo("Success", "Login successful")
                mode.currentProfile = (userName, userPassword)
                return 
        messagebox.showinfo("Failed", "Could not find account. Try again")

    def drawGameButton(mode, canvas):
        mode.gameButton.updateCoordinates(mode.width / 2 - mode.width / 8, 
                                 mode.height / 5, 
                                 mode.width / 2 + mode.width / 8,
                                 mode.height / 5 + mode.height / 8)
        canvas.create_rectangle(mode.gameButton.x0, mode.gameButton.y0, 
                                mode.gameButton.x1, mode.gameButton.y1, 
                                fill = mode.lightBlue, width = '5')
        canvas.create_text(mode.width / 2, 
                           mode.gameButton.y0 + 
                           (mode.gameButton.y1 - mode.gameButton.y0) / 2, 
                           text = "Play Game", font = "times 30 bold",
                           justify = "center")

    def drawPracticeModeButton(mode, canvas):
        mode.practiceModeButton.updateCoordinates(mode.width / 2 - mode.width / 8, 
                                         mode.height / 3 + 20,
                                         mode.width / 2 + mode.width / 8,
                                         mode.height / 3 + mode.height / 8 + 20)
        canvas.create_rectangle(mode.practiceModeButton.x0, 
                                mode.practiceModeButton.y0, 
                                mode.practiceModeButton.x1,
                                mode.practiceModeButton.y1, 
                                fill = mode.lightBlue, width = '5')
        canvas.create_text(mode.width / 2, mode.practiceModeButton.y0 + 
                           (mode.practiceModeButton.y1 - mode.practiceModeButton.y0) / 2,
                           text = "Practice Mode", font = "times 30 bold",
                           justify = "center")

    def drawStatisticsButton(mode, canvas):
        mode.statisticsButton.updateCoordinates(mode.width / 2 - mode.width / 8, 
                                       mode.height / 2 + 20, 
                                       mode.width / 2 + mode.width / 8,
                                       mode.height / 2 + mode.height / 8 + 20)
        canvas.create_rectangle(mode.statisticsButton.x0, 
                                mode.statisticsButton.y0, 
                                mode.statisticsButton.x1,
                                mode.statisticsButton.y1, 
                                fill = mode.lightBlue, width = '5')
        canvas.create_text(mode.width / 2, mode.statisticsButton.y0 + 
                           (mode.statisticsButton.y1 - mode.statisticsButton.y0) / 2,
                           text = "Statistics", font = "times 30 bold",
                           justify = "center")

    def drawCreateProfileButton(mode, canvas):
        mode.createProfileButton.updateCoordinates(mode.width - mode.width / 6, 
                            mode.height - 45, mode.width - 10, mode.height - 10)
        canvas.create_rectangle(mode.createProfileButton.x0, 
                                mode.createProfileButton.y0, 
                                mode.createProfileButton.x1,
                                mode.createProfileButton.y1, 
                                fill = mode.lightBlue, width = '5')
        canvas.create_text((mode.createProfileButton.x0 + 
                           mode.createProfileButton.x1) / 2, mode.height - 28,
                           text = "Create Profile", font = "times 18 bold",
                           justify = "center")
        canvas.create_text((mode.createProfileButton.x0 + 
                           mode.createProfileButton.x1) / 2 - mode.width / 5 + 5, 
                           mode.height - 28, 
                           text = f"Current Profile: {mode.currentProfile[0]}", 
                           font = "times 18 bold", justify = "center")

    def drawLoadProfileButton(mode, canvas):
        mode.loadProfileButton.updateCoordinates(mode.width - mode.width / 6, 
                    mode.height - 90, mode.width - 10, mode.height - 55)
        canvas.create_rectangle(mode.loadProfileButton.x0, 
                                mode.loadProfileButton.y0, 
                                mode.loadProfileButton.x1,
                                mode.loadProfileButton.y1, 
                                fill = mode.lightBlue, width = '5')
        canvas.create_text((mode.loadProfileButton.x0 + 
                           mode.loadProfileButton.x1) / 2, mode.height - 72,
                           text = "Load Profile", font = "times 18 bold",
                           justify = "center")

    def drawRegularGameButton(mode, canvas):
        mode.regularGameButton.updateCoordinates(mode.width / 2 - mode.width / 8,
                                        mode.height / 3,
                                        mode.width / 2 + mode.width / 8,
                                        mode.height / 3 + mode.height / 8)
        canvas.create_rectangle(mode.regularGameButton.x0, 
                                mode.regularGameButton.y0, 
                                mode.regularGameButton.x1,
                                mode.regularGameButton.y1, 
                                fill = mode.lightBlue, width = '5')
        canvas.create_text(mode.width / 2, mode.regularGameButton.y0 + 
                           (mode.regularGameButton.y1 - mode.regularGameButton.y0) / 2,
                           text = "Regular Game", font = "times 30 bold",
                           justify = "center")
    def drawLightningModeButton(mode, canvas):
        mode.lightningModeButton.updateCoordinates(mode.width / 2 - mode.width / 8,
                                        mode.height / 2 + 20,
                                        mode.width / 2 + mode.width / 8,
                                        mode.height / 2 + mode.height / 8 + 20)
        canvas.create_rectangle(mode.lightningModeButton.x0, 
                                mode.lightningModeButton.y0, 
                                mode.lightningModeButton.x1,
                                mode.lightningModeButton.y1, 
                                fill = mode.lightBlue, width = '5')
        canvas.create_text(mode.width / 2, mode.lightningModeButton.y0 + 
                           (mode.lightningModeButton.y1 - mode.lightningModeButton.y0) / 2,
                           text = "Lightning Mode", font = "times 30 bold",
                           justify = "center")

    def drawBackButton(mode, canvas):
        mode.backButton.updateCoordinates(mode.width - mode.width / 6, 
                                 mode.height - mode.height / 10,
                                 mode.width - 15,
                                 mode.height - 15)
        canvas.create_rectangle(mode.backButton.x0, 
                                mode.backButton.y0, 
                                mode.backButton.x1,
                                mode.backButton.y1, 
                                fill = mode.lightBlue, width = '5')
        canvas.create_text((mode.backButton.x1 + mode.backButton.x0) / 2, 
                           mode.backButton.y0 + (mode.backButton.y1 - mode.backButton.y0) / 2,
                           text = "Back", font = "times 22 bold",
                           justify = "center")

    def drawInfoButton(mode, canvas):
        mode.infoButton.updateCoordinates(10, mode.height - 40, 80, mode.height - 10)
        canvas.create_rectangle(mode.infoButton.x0, 
                                mode.infoButton.y0, 
                                mode.infoButton.x1,
                                mode.infoButton.y1, 
                                fill = mode.lightBlue, width = '5')
        canvas.create_text((mode.infoButton.x1 + mode.infoButton.x0) / 2, 
                           mode.infoButton.y0 + (mode.infoButton.y1 - mode.infoButton.y0) / 2,
                           text = "Info", font = "times 20 bold",
                           justify = "center")

    def redrawAll(mode, canvas):
        canvas.create_rectangle(0, 0, mode.width, mode.height, fill = mode.vanilla)
        canvas.create_text(mode.width / 2, mode.height / 12, 
                           text = "J! Trainer", font = "times 50 bold italic",
                           justify = "center")
        mode.drawGameButton(canvas)
        mode.drawPracticeModeButton(canvas)
        mode.drawStatisticsButton(canvas)
        mode.drawCreateProfileButton(canvas)
        mode.drawLoadProfileButton(canvas)
        mode.drawInfoButton(canvas)
        if(mode.inGameSubMenu):
            canvas.create_rectangle(0, 0, mode.width, mode.height, fill = mode.vanilla)
            canvas.create_text(mode.width / 2, mode.height / 12, 
                               text = "Select Game Mode", font = "times 50 bold italic",
                               justify = "center")
            mode.drawRegularGameButton(canvas)
            mode.drawLightningModeButton(canvas)
            mode.drawBackButton(canvas)