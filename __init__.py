from cmu_112_graphics import *
from tkinter import *
from broad_categories import *
from clue_dictionary import *
from animation_helpers import *
from game_mode import *
from lightning_mode import *
from menu_mode import *
from statistics import *
from practice import *
from info_mode import *
#File that must be run to start the app. Imports from all other files and creates the modes

#CITATION: Modal App and cmu_112_graphics from http://www.cs.cmu.edu/~112/notes/notes-animations-part2.html
#CITATION: Jeopardy Clues from http://j-archive.com/
class Jeopardy(ModalApp):
    def appStarted(app):
        app.menuMode = MenuMode()
        app.gameMode = GameMode()
        app.lightningMode = LightningMode()
        app.practiceMode = PracticeMode()
        app.statisticsMode = StatisticsMode() 
        app.infoMode = InfoMode()
        app.setActiveMode(app.menuMode)

Jeopardy(width = 1000, height = 600)