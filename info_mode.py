from cmu_112_graphics import *
from tkinter import *
from animation_helpers import *
#description page for the project 

class InfoMode(Mode):
    def appStarted(mode):
        mode.vanilla = rgbString(245, 231, 186) 
        mode.lightBlue = rgbString(115, 178, 255)
        mode.introText = "Welcome to J! Trainer. This is an interactive Jeopardy! training app. In order to make use of the statistics feature and personalized practice mode, please create a profile. Usernames and passwords must be between 3 and 12 characters."
        mode.bodyText = "After you've created a profile, J! Trainer will keep track of your accuracy in each broad category when you play the game and display it in the Statistics page. If you would like to practice your worst categories, you can use the personalization option in Practice Mode. If you are looking for a challenge, you can also check out Lightning Mode."
        mode.body2Text = "In Lightning Mode, you begin with one minute on your timer. Your goal is the get the highest score possible. Each clue you answer correctly gives you more time, and each clue you answer incorrectly subtracts from your time."
        mode.endText = "All categories and clues are property of Jeopardy! and taken from http://j-archive.com/. \n J! Trainer is not affliated with Jeopardy! in any way."
        mode.backButton = Button(mode.width - mode.width / 6, 
                                 mode.height - mode.height / 10,
                                 mode.width - 15,
                                 mode.height - 15)
    def mousePressed(mode, event):
        mode.backButton.updateCoordinates(mode.width - mode.width / 6, 
                                        mode.height - mode.height / 10,
                                        mode.width - 15,
                                        mode.height - 15)
        if(event.x > mode.backButton.x0 and 
           event.x < mode.backButton.x1 and 
           event.y > mode.backButton.y0 and 
           event.y < mode.backButton.y1):
            mode.app.setActiveMode(mode.app.menuMode)

    def redrawAll(mode, canvas):
        mode.backButton.updateCoordinates(mode.width - mode.width / 6, 
                                 mode.height - mode.height / 10,
                                 mode.width - 15,
                                 mode.height - 15)
        canvas.create_rectangle(0, 0, mode.width, mode.height, fill = mode.vanilla)
        canvas.create_text(mode.width / 2, mode.height / 6, text = mode.introText,
                           width = mode.width / 2 + 100, font = "times 20 bold")
        canvas.create_text(mode.width / 2, mode.height / 2 - 50, text = mode.bodyText,
                           width = mode.width / 2 + 100, font = "times 20 bold")
        canvas.create_text(mode.width / 2, mode.height / 2 + 100, 
                           text = mode.body2Text, width = mode.width / 2 + 100,
                           font = "times 20 bold")
        canvas.create_text(mode.width / 2, mode.height / 2 + 225, text = mode.endText,
                           width = mode.width / 2 + 100, font = "times 20 bold")
        canvas.create_rectangle(mode.backButton.x0, 
                                mode.backButton.y0, 
                                mode.backButton.x1,
                                mode.backButton.y1, 
                                fill = mode.lightBlue, width = '5')
        canvas.create_text((mode.backButton.x1 + mode.backButton.x0) / 2, 
                           mode.backButton.y0 + (mode.backButton.y1 - mode.backButton.y0) / 2,
                           text = "Back", font = "times 22 bold",
                           justify = "center")