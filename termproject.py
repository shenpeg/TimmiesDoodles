############################################
# Peggy Shen (peggys)
# 15-112 Term Project Fall 2020
# "Timmie's Doodles"
# tp3.py
############################################

from cmu_112_graphics import *
import PIL, requests
import random, math
from pygame import mixer

# cmu graphics framework: 
# # http://www.cs.cmu.edu/~112/notes/notes-graphics.html

def paintApps(app):
    app.drawProtag = False
    app.drawAntag = False
    app.toolSize = 8
    app.pen = dict()
    app.penX, app.penY = app.width//2, app.height//2
    app.penColor = "black"
    app.penDown = False
    app.bucket = False
    app.fill = dict()
    app.eraser = False
    app.clear = False
    app.next = False
    app.shapeMode = False
    app.shapes = dict()
    app.type = "rectangle"
    app.shapeX1, app.shapeY1 = -1, -1
    app.shapeX2, app.shapeY2 = -1, -1

def resetAntag(app):
    # antagonist defaults; randomized position and spell to defeat it
    for i in range(app.numOfAntags):
        antagX = app.width + random.randint(0,100)
        antagY = random.randint(30, app.height - 30)
        antagSpell = []
        for i in range(app.numOfAntags):
            randomIndex = random.randint(0, len(app.allSpells) - 1)
            antagSpell.append(app.allSpells[randomIndex])
        antagdx = app.dx 
        antagdy = app.dx * (app.protagY - antagY) / (app.protagX - antagX)
        app.antags.append([antagX, antagY, antagSpell, antagdx, antagdy])

def gameApps(app):
    app.protagX = 70
    app.protagY = app.height//2
    app.dx = 2
    app.antags = []
    app.spellPen = []
    app.spellPenColor = "black"
    app.allSpells = ["—", "|", "V", "Λ"]
    app.spellType = None
    app.spellValid = True
    app.gameLevel = 1
    app.numOfAntags = 1 + app.gameLevel
    resetAntag(app)
    app.lives = 3
    app.score = 0
    app.game = False
    app.paused = False
    app.gameOver = False
    app.gameWon = False
    # protag and antag images:  
    app.protagImage = app.loadImage("protag.png")
    app.antagImage = app.loadImage("antag.png")
    app.protagPic = app.scaleImage(app.protagImage, 1/12)
    app.antagPic = app.scaleImage(app.antagImage, 1/12)

def appStarted(app):
    app.splash = True
    app.splashimage = app.loadImage("splash_page.png")
    app.splashDrawing = app.scaleImage(app.splashimage, 4/9)
    app.instructions = False
    app.instructImage = app.loadImage("instructions.png")
    app.instructPic = app.scaleImage(app.instructImage, 1/5)
    paintApps(app)
    gameApps(app)

def mousePressed(app, event):
    if (app.splash and app.width//2 - 31 <= event.x <= app.width//2 + 31 and 
        app.height//2 + 60 <= event.y <= app.height//2 + 85):
        app.splash = False
        app.drawProtag = True
        app.penDown = True
    elif (app.splash and app.width//2 - 60 <= event.x <= app.width//2 + 50 and
        app.height//2 + 100 <= event.y <= app.height//2 + 160):
        app.instructions = True
    elif app.instructions:
        app.instructions = not app.instructions
    elif app.drawProtag:
        checkMousePressedPosition(app, event.x, event.y)
        if app.next == True:
            app.next = False
            app.drawProtag = False
            app.drawAntag = True
            app.penDown = True
            app.pen = dict()
            app.shapes = dict()
            app.fill = dict()
    elif app.drawAntag:
        checkMousePressedPosition(app, event.x, event.y)
        if app.next == True:
            app.next = False
            app.drawAntag = False
            app.penDown = False
            app.game = True
    elif app.game and not app.paused and not app.gameOver:
        pass


#######################################
# PAINT MECHANICS

def checkMousePressedPosition(app,x,y):
    # user presses respective buttons (colors, shapes, eraser, clear)
    buttonWidth = 35
    if (x >= 30 and x <= 110 and y >= app.height - 45 and y <= app.height - 15):
        changePenColor(app, x, y)   # switch colors
    elif (x >= 175 - buttonWidth and x <= 175 + buttonWidth and 
        y >= app.height - 45 and y <= app.height - 15):
        app.penDown = False
        app.bucket = False
        app.eraser = False
        app.shapeMode = True
        changeShapeType(app, x, y)  # switch shapes
    elif (x >= 260 - buttonWidth and x <= 260 + buttonWidth and 
        y >= app.height - 45 and y <= app.height - 15):
        app.penDown = True          # draw with pen
        app.bucket = False
        app.eraser = False
        app.shapeMode = False
    elif (x >= 320 - buttonWidth and x <= 320 + buttonWidth and 
        y >= app.height - 45 and y <= app.height - 15):
        app.bucket = True           # fill whitespaces
        app.penDown = False
        app.eraser = False
        app.shapeMode = False
    elif (x >= 390 - buttonWidth and x <= 390 + buttonWidth and 
        y >= app.height - 45 and y <= app.height - 15):
        app.bucket = False              
        app.eraser = True           # erase pen and shapes
        app.penDown = False
        app.shapeMode = False
    elif (x >= 460 - buttonWidth and x <= 460 + buttonWidth and 
        y >= app.height - 45 and y <= app.height - 15):
        app.pen = dict()
        app.shapes = dict()       # clear the canvas
        app.fill = dict()
        app.bucket = False
        app.eraser = False
        app.penDown = True
        app.shapeMode = False
    elif (x >= 550 - buttonWidth and x <= 550 + buttonWidth and 
        y >= app.height - 45 and y <= app.height - 15):
        app.bucket = False
        app.eraser = False
        app.penDown = False
        app.shapeMode = False
        app.next = True             # next button
    elif (x >= 60-buttonWidth and x <= 60+buttonWidth and y >= 55 and y <= 85):
        saveCanvas(app)
    elif x>30 and x <app.width-30 and y >60 and y < app.height-60 and app.bucket:
        #check x,y is in any shapes
        selectlst = shapeSelected(app, x, y)
        for item in selectlst:
            typ, color, fill = app.shapes[item]
            app.shapes[item] = (typ, color, app.penColor)
        if len(selectlst)== 0 :
            # only do floodFill if no shapes found and (x,y) in the area
            # caution: if there is no closed area floodFill 
            # will fill the whole screen and slow down everything.
            floodFill(app, x, y)
    
def changePenColor(app, x, y):
    #app.penDown = True
    if x >= 30 and x <= 50 and y >= app.height - 50 and y <= app.height - 30:
        app.penColor = "red"
    elif x >= 50 and x <= 70 and y >= app.height - 50 and y <= app.height - 30:
        app.penColor = "orange"
    elif x >= 70 and x <= 90 and y >= app.height - 50 and y <= app.height - 30:
        app.penColor = "yellow"
    elif x >= 90 and x <= 110 and y >= app.height - 50 and y <= app.height - 30:
        app.penColor = "green"
    elif x >= 30 and x <= 50 and y >= app.height - 30 and y <= app.height - 10:
        app.penColor = "blue"
    elif x >= 50 and x <= 70 and y >= app.height - 30 and y <= app.height - 10:
        app.penColor = "purple"
    elif x >= 70 and x <= 90 and y >= app.height - 30 and y <= app.height - 10:
        app.penColor = "pink"
    elif x >= 90 and x <= 110 and y >= app.height - 30 and y <= app.height - 10:
        app.penColor = "black"

def changeShapeType(app, x, y):
    app.shapeMode = True
    if x >= 130 and x <= 170:
        app.type = "rectangle"
    else:
        app.type = "circle"

def saveCanvas(app):
    app.saveSnapshot()

def rgbString(r, g, b):
    # http://www.cs.cmu.edu/~112/notes/notes-graphics.html
    # may delete later or use after tp2
    return f'#{r:02x}{g:02x}{b:02x}'

def pen(app, canvas):
    if app.drawProtag or app.drawAntag:
        for points in app.pen:
            penX, penY = points
            color = app.pen[points]
            canvas.create_oval(penX - 2, penY - 2, penX + 2, 
                           penY + 2, fill = color, 
                           outline = color, width = app.toolSize)
        for pixels in app.fill:
            pixelX, pixelY = pixels
            fillColor = app.fill[pixels]
            canvas.create_oval(pixelX - 2, pixelY - 2, pixelX + 2, pixelY + 2, 
                                fill = fillColor, outline = fillColor, 
                                width = app.toolSize)

def floodFill(app, x, y):
    bucketFill = set()
    count = 0
    bucketFill.add((x, y))
    while not len(bucketFill) == 0 and count < 300000: # num of screen pixels
        (x0, y0) = bucketFill.pop()
        boundary = False
        for i in range(x0 - 8, x0 + 9):
            for j in range(y0 - 8, y0 + 9):
                # search before and after where mouse is pressed
                if (i, j) in app.pen:
                    boundary = True         # don't fill

        if boundary == False:           # fill the boundary:
            app.fill[(x0, y0)] = app.penColor
            # check if its within canvas dimensions and hasn't been filled:
            if (x0 - 2, y0) not in app.fill and x0 - 2 > 30:
                bucketFill.add((x0 - 2, y0))
            if (x0 + 2, y0) not in app.fill and x0 + 2 < app.width - 30:
                bucketFill.add((x0 + 2, y0))
            if (x0, y0 - 2) not in app.fill and y0 - 2 > 60:
                bucketFill.add((x0, y0 - 2))
            if (x0, y0 + 2) not in app.fill and y0 + 2 < app.height - 60:
                bucketFill.add((x0, y0 + 2))
        count += 1

def shapeSelected(app, x, y):
    selectlst = set()
    for shape in app.shapes:
        x1, y1, x2, y2 = shape
        typ, color, fill = app.shapes[shape]
        if typ == "rectangle":
            if (x >= min(x1, x2) and x <= max(x1, x2) and y >= min(y1, y2) and 
                y <= max(y1, y2)):
                #inside or on the rectangle
                selectlst.add((x1,y1,x2,y2))
        elif typ == "circle":
            cX = (x1+x2)/2
            cY = (y1+y2)/2
            a = abs(x2-x1)/2
            b = abs(y2-y1)/2
            p=math.pow((x-cX),2)/math.pow(a,2) + math.pow((y-cY),2)/math.pow(b,2)
            if p <= 1: #inside or on the elipse
                selectlst.add((x1,y1,x2,y2))
    return selectlst

def drawShapes(app, canvas):
    if app.drawProtag or app.drawAntag:
        if app.type == "rectangle":
            canvas.create_rectangle(app.shapeX1, app.shapeY1, app.shapeX2, 
                                    app.shapeY2, outline="black")
        elif app.type == "circle":
            canvas.create_oval(app.shapeX1, app.shapeY1, app.shapeX2, 
                                app.shapeY2, outline="black")
        for shape in app.shapes:
            x1, y1, x2, y2 = shape
            typ, color, fill = app.shapes[shape]
            if typ == "rectangle":
                canvas.create_rectangle(x1, y1, x2, y2, outline = "black", 
                                        width = 2, fill = fill)
            elif typ =="circle":
                canvas.create_oval(x1, y1, x2, y2, outline = "black", 
                                    width = 2, fill = fill)

def drawCanvas(app, canvas):
    font = "fixedsys 17 bold"
    nextFont = "fixedsys 19 bold underline"
    canvas.create_rectangle(30, 60, app.width - 30, app.height - 60, 
                            fill = "white", outline = "white")
    canvas.create_text(60, 70, text = "SAVE", font = font, fill = "blue")
    drawColorButtons(app, canvas)
    drawShapesButton(app, canvas)
    if app.penDown:
        canvas.create_rectangle(260 - 25, app.height - 45, 260 + 25, 
                                app.height - 15, fill='cyan')
        canvas.create_text(260, app.height - 30, text = "PEN", font = font, 
                            fill = "red")
    else:
        canvas.create_text(260, app.height - 30, text = "PEN", font = font, 
                        activefill = "red")
    if app.bucket:
        canvas.create_rectangle(320 - 25, app.height - 45, 320 + 25, 
                                app.height - 15, fill = 'cyan')
        canvas.create_text(320, app.height - 30, text = "FILL", font = font, 
                            fill = "red")
    else:
        canvas.create_text(320, app.height - 30, text = "FILL", font = font, 
                            activefill = "red")
    if app.eraser:  
        canvas.create_rectangle(390 - 30, app.height - 45, 390 + 30, 
                                app.height - 15, fill = 'cyan')
        canvas.create_text(390, app.height - 30, text = "ERASE", font = font, 
                            fill = "red")
    else:                  
        canvas.create_text(390, app.height - 30, text = "ERASE", font = font, 
                            activefill = "red")
                        
    canvas.create_text(460, app.height - 30, text = "CLEAR", font = font, 
                        activefill = "red")
    canvas.create_text(550, app.height - 30, text = "NEXT", font = nextFont, 
                        activefill = "red", fill = "green")

def drawColorButtons(app, canvas):
    canvas.create_rectangle(30, app.height - 50, 48, app.height - 31, 
                            outline ="cyan", fill = "red", width = 3 
                            if app.penColor == "red" else 0)
    canvas.create_rectangle(50, app.height - 50, 68, app.height - 31, 
                            outline ="cyan", fill = "orange", width = 3 
                            if app.penColor == "orange" else 0)
    canvas.create_rectangle(70, app.height - 50, 88, app.height - 31, 
                            outline ="cyan", fill = "yellow",width = 3 
                            if app.penColor == "yellow" else 0)
    canvas.create_rectangle(90, app.height - 50, 108, app.height - 31, 
                            outline ="cyan", fill = "green", width = 3 
                            if app.penColor == "green" else 0)
    canvas.create_rectangle(30, app.height - 29, 48, app.height - 10, 
                            outline ="cyan", fill = "blue",width = 3 
                            if app.penColor == "blue" else 0)
    canvas.create_rectangle(50, app.height - 29, 68, app.height - 10, 
                            outline ="cyan", fill = "purple",width = 3 
                            if app.penColor == "purple" else 0)
    canvas.create_rectangle(70, app.height - 29, 88, app.height - 10, 
                            outline ="cyan", fill = "pink",width = 3 
                            if app.penColor == "pink" else 0)
    canvas.create_rectangle(90, app.height - 29, 108, app.height - 10, 
                            outline ="cyan", fill = "black",width = 3 
                            if app.penColor == "black" else 0)

def drawShapesButton(app, canvas):
    if app.shapeMode and app.type == "rectangle":
        canvas.create_rectangle(130, app.height - 50, 170, app.height - 10, 
                            fill = "cyan", outline = "black")
        canvas.create_rectangle(140, app.height - 45, 160, app.height - 15, 
                            outline = "black")
    else:
        canvas.create_rectangle(130, app.height - 50, 170, app.height - 10, 
                            fill = "tan", outline = "black", activefill = "red")
        canvas.create_rectangle(140, app.height - 45, 160, app.height - 15, 
                            outline = "black")
    if app.shapeMode and app.type == "circle":
        canvas.create_rectangle(180, app.height - 50, 220, app.height - 10, 
                            fill = "cyan", outline = "black")
        canvas.create_oval(185, app.height - 45, 215, app.height - 15, 
                            outline = "black")
    else:
        canvas.create_rectangle(180, app.height - 50, 220, app.height - 10, 
                            fill = "tan", outline = "black", activefill = "red")
        canvas.create_oval(185, app.height - 45, 215, app.height - 15, 
                            outline = "black")

def drawProtagText(app, canvas):
    if app.drawProtag:
        font = "fixedsys 17 bold"
        title = "draw your hero protagonist:"
        canvas.create_text(app.width/2, 25, text = title, font = font)
        drawCanvas(app, canvas)
        
def drawAntagText(app, canvas):
    if app.drawAntag:
        font = "fixedsys 17 bold"
        title = "now draw your enemy antagonist:"
        canvas.create_text(app.width/2, 25, text = title, font = font)
        drawCanvas(app, canvas)


###############################################

def mouseDragged(app, event):
    # using pen:
    if (app.drawProtag or app.drawAntag) and app.penDown:
        if (event.x >= 30 and event.x <= app.width - 30 and event.y >= 60 
            and event.y <= app.height - 60):
            app.pen[(event.x, event.y)] = app.penColor
    # using eraser:
    elif (app.drawProtag or app.drawAntag) and app.eraser:
        for i in range(event.x - 8, event.x + 9):
            for j in range(event.y - 8, event.y + 9):
                if (i,j) in app.pen:  # erase pen trace
                    app.pen.pop((i,j))
                if (i,j) in app.fill: # erase fill
                    app.fill.pop((i,j))
        # check whether shapes has been selected
        selectlst = shapeSelected(app, event.x, event.y)
        for item in selectlst:
            app.shapes.pop(item)
    # using shapes function:
    elif (app.drawProtag or app.drawAntag) and app.shapeMode:
        if (app.shapeX1, app.shapeY1) == (-1, -1):
            app.shapeX1 = event.x
            app.shapeY1 = event.y
        app.shapeX2 = event.x
        app.shapeY2 = event.y
    # drawing spell in-game:
    elif app.game and not app.gameOver and not app.paused:
        if (event.x >= 0 and event.x <= app.width and event.y >= 0 
            and event.y <= app.height):
            app.spellPen.append((event.x, event.y))

def mouseReleased(app,event):
    # make sure shape stays on the canvas after releasing mouse (captures x, y)
    if app.shapeMode:
        if (app.shapeX1 != -1 and app.shapeY1 != -1 and app.shapeX2 != -1 and
            app.shapeY2 != -1):
            app.shapes[(app.shapeX1, app.shapeY1, app.shapeX2, app.shapeY2)] = \
            (app.type, app.penColor, None)
            (app.shapeX1, app.shapeY1,app.shapeX2, app.shapeY2) = (-1,-1,-1,-1)
    # clear the spell cast in-game 
    elif app.game and not app.paused and not app.gameOver:
        app.spellPen = []
        app.spellPenColor = "black"
        app.spellValid = True


################################################
# GAME MECHANICS:

def keyPressed(app, event):
    if event.key == "r" or event.key == "R":        # reset game
        gameApps(app)
        app.game = True
        app.gameOver = False
    elif event.key == "h" or event.key == "H":      # go back to splash
        appStarted(app)
    elif event.key == "p":
        app.paused = not app.paused

def correctSpell(app):
    # whether user enters correct spell order
    i = 0
    if app.spellValid: 
        while i < len(app.antags):
            if app.spellType == app.antags[i][2][0]:
            # laser sound effect taken from:
            # https://github.com/attreyabhatt/Space-Invaders-Pygame/find/master
                spellSound = mixer.Sound('laser.wav')
                spellSound.play()
                app.antags[i][2].pop(0)
                app.spellValid = False  # only applies spell once, not multiple
            if len(app.antags[i][2]) == 0:
                app.antags.pop(i)
                # pop sound effect taken from:
                # http://freesoundslibrary.com
                spellSound = mixer.Sound('pop.mp3')
                spellSound.play()
                app.score += 1
            i += 1      
  
    if len(app.antags) == 0:
        resetAntag(app)
        app.gameLevel +=1
        if app.gameLevel % 2 ==0:  # change enemy speed
            app.dx +=1
        else:
            app.numOfAntags = 1 + app.gameLevel//2 # change number of enemies

def timerFired(app):
    if app.game and not app.paused and not app.gameOver:
        moveAntag(app)
        spellCheck(app)
        correctSpell(app)

def moveAntag(app):
    for i in range(len(app.antags)):
        app.antags[i][0] -= app.antags[i][3]
        app.antags[i][1] -= app.antags[i][4]
    (touched, touchid) = antagTouchedProtag(app)
    if touched:
        app.lives -= 1
        app.antags.pop(touchid)
        if len(app.antags)==0:
            resetAntag(app)
        if app.lives == 0:
            app.gameOver = True
            app.game = False

def antagTouchedProtag(app):
    for i in range(len(app.antags)):
        if (app.antags[i][0] <= app.protagX + 100 
            and app.antags[i][1] <= app.protagY + 100):
            return (True, i)
    return (False, i)

def drawSpell(app, canvas):
    # when the user draws the "spell" on screen
    if app.game and not app.gameOver and not app.paused:
        for points in app.spellPen:
            penX, penY = points
            canvas.create_oval(penX - 4, penY - 4, penX + 4, 
                                penY + 4, fill = app.spellPenColor, 
                                outline= app.spellPenColor, width= app.toolSize)

def spellCheck(app):
    # checks what kind of spell type is drawn
    if len(app.spellPen) >= 4:
        deltaXList = []
        deltaYList = []
        increaseX = True
        Vstarted, Vformed = False, False
        inverseVStarted, inverseVFormed = False, False
        totalX, totalY = 0, 0
        variationInX, variationInY = 0, 0
        for points in app.spellPen:
            penX, penY = points
            totalX += penX
            totalY += penY
        avgX = totalX / len(app.spellPen)
        avgY = totalY / len(app.spellPen)
        for points in app.spellPen:
            penX, penY = points
            variationInX += ((penX - avgX)**2)
            variationInY += ((penY - avgY)**2)
        variationInX = (variationInX / (len(app.spellPen) - 1))**(0.5)
        variationInY = (variationInY / (len(app.spellPen) - 1))**(0.5)
        for i in range(len(app.spellPen)-1):
            x1, y1 = app.spellPen[i]
            x2, y2 = app.spellPen[i+1]
            deltaX = x2 - x1
            deltaY = y2 - y1
            deltaXList.append(deltaX)
            deltaYList.append(deltaY)
        for i in range(len(deltaXList)):
            if deltaXList[i] < 0:
                increaseX = False
            if deltaYList[i] > 0:       # if line drawn is going downwards
                Vstarted = True         # then the "V" symbol is being started
                if inverseVStarted == True:
                    inverseVFormed = True
                else:
                    inverseVStarted = False
                    inverseVFormed = False
            elif deltaYList[i] < 0:     # if line drawn is going upwards
                inverseVStarted = True  # then the "Λ" symbol is being started
                if Vstarted == True:
                    Vformed = True
                else:
                    Vstarted = False
                    Vformed = False        
    else:
        variationInX, variationInY = -1, -1
        increaseX = False
        Vstarted, Vformed = False, False
        inverseVStarted, inverseVFormed = False, False
    # types of lines recognized:
    if 0 < variationInY < 7 and variationInX > 15:
        app.spellType = "—"
        app.spellPenColor = "red"
    elif 0 < variationInX < 7 and variationInY > 15:
        app.spellType = "|"
        app.spellPenColor = "blue"
    elif increaseX and Vformed:
        app.spellType = "V"
        app.spellPenColor = "yellow"
    elif increaseX and inverseVFormed:
        app.spellType = "Λ"
        app.spellPenColor = "green"
    else:
        app.spellType = "None"
        app.spellPenColor = "black"

def drawGameOver(app, canvas):
    drawGameBG(app, canvas)
    canvas.create_rectangle(0, app.height//3 + 20, app.width, 
                            app.height * 2 // 3, fill = "gray")
    canvas.create_text(app.width/2, app.height/2 - 30,
                       text='Game Over!', font='fixedsys 18 bold')
    canvas.create_text(app.width/2, app.height/2,
                       text= f'Score: {app.score}', font='fixedsys 18 bold')                 
    canvas.create_text(app.width/2, app.height/2 + 25,
                       text='Press "R" to restart game', 
                       font='fixedsys 15')
    canvas.create_text(app.width/2, app.height/2 + 55,
                       text='Press "H" to go home', 
                       font='fixedsys 15')

def drawGameBG(app, canvas):
    if app.game or app.gameOver:
        canvas.create_rectangle(0, 0, app.width, app.height, fill = "white")
        canvas.create_text(app.width/2, 30, 
                            text = "Don't let your enemy get close!",
                            font = "fixedsys 16", fill = "black")
        canvas.create_image(app.protagX, app.protagY, 
                            image=ImageTk.PhotoImage(app.protagPic))
        for i in range(len(app.antags)):
            antagX = app.antags[i][0]
            antagY = app.antags[i][1]
            antagSpell = app.antags[i][2]
            canvas.create_image(antagX, antagY, 
                                image = ImageTk.PhotoImage(app.antagPic)) 
            canvas.create_text(antagX, antagY - app.height/8, 
                                text = antagSpell, font = "Arial 10 bold", 
                                fill = "red")
        canvas.create_text(50, 20, text = f'Lives: {app.lives}', 
                            font = "fixedsys 12", fill = "black")
        canvas.create_text(550, 20, text = f'Score: {app.score}', 
                            font = "fixedsys 12", fill = "black")
        drawSpell(app, canvas)

##########################################

def drawSplashPage(app, canvas):
    if app.splash == False:
        return
    else:
        canvas.create_image(app.width/2 + 18, app.height/2 + 18, 
                            image = ImageTk.PhotoImage(app.splashDrawing))
        canvas.create_text(app.width//2, app.height//2 + 70, 
                           text = 'PLAY!', fill = 'black',
                           font = 'fixedsys 18 italic', activefill = "red")
        canvas.create_text(app.width//2 - 5, app.height//2 + 130, 
                           text = "  Timmie's\nInstructions", fill = 'black',
                           font = 'fixedsys 17 italic', activefill = "red")

def drawInstructions(app, canvas):
    canvas.create_rectangle(90, 41, app.width - 90, app.height - 41, 
                            fill = "black")
    canvas.create_image(app.width/2, app.height/2, 
                            image = ImageTk.PhotoImage(app.instructPic))
                            
def redrawAll(app, canvas):
    if app.splash:
        drawSplashPage(app, canvas)
        if app.instructions:
            drawInstructions(app, canvas)
    else:
        canvas.create_rectangle(0, 0, app.width, app.height, fill = "SkyBlue")
        drawProtagText(app, canvas)
        drawAntagText(app, canvas)
        drawGameBG(app, canvas)
        pen(app, canvas)
        drawShapes(app,canvas)
        if app.gameOver == True:
            drawGameOver(app, canvas)

###########################################

def main():
    mixer.init()
    runApp(width=600, height=500)

if __name__ == '__main__':
    main()