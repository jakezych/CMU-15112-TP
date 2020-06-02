#contains useful methods and classes used to help make some of the animation code
#look cleaner

#CITATION: Taken from http://www.cs.cmu.edu/~112/notes/notes-graphics-part2.html
def rgbString(red, green, blue):
    return "#%02x%02x%02x" % (red, green, blue)

#returns a list of 25 distinct colors
def getColorsList():
    rgbs = [(230, 25, 75), (60, 180, 75), (255, 225, 25), (0, 130, 200), 
            (245, 130, 48), (145, 30, 180), (70, 240, 240), (240, 50, 230), 
            (210, 245, 60), (250, 190, 190), (0, 128, 128), (230, 190, 255), 
            (170, 110, 40), (128, 0, 0), (170, 255, 195), (128, 128, 0), 
            (255, 215, 180), (0, 0, 128), (128, 128, 128), (42, 99, 37),
            (141, 151, 199), (145, 38, 136), (207, 155, 0), (154, 189, 87)]
    colors = []
    for elem in rgbs:
        colors.append(rgbString(elem[0], elem[1], elem[2]))
    return colors

#keeps track of the coordinates of a rectangle that acts as a button. 
class Button(object):
    def __init__(self, x0, y0, x1, y1):
        self.updateCoordinates(x0, y0, x1, y1)
    
    def updateCoordinates(self, x0, y0, x1, y1):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1