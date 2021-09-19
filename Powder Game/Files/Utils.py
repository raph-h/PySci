def getSurroundingObjects(gameArea, position=[0,0]): # Returns a list which contains the objects surrounding the position
    x = position[0] # Get position variables
    y = position[1]
    width = len(gameArea[y])
    height = len(gameArea)

    surrounding = [] # Initialise list
    #Left
    if x - 1 >= 0: # Check if it is in bounds
        surrounding.append(getGameArea(x - 1, y, gameArea)) # Append to the list the object in that area
    else:
        surrounding.append(None)

    #TopLeft
    if x - 1 >= 0 and y - 1 >= 0:
        surrounding.append(getGameArea(x - 1, y - 1, gameArea))
    else:
        surrounding.append(None)
    
    #Top
    if y - 1 >= 0:
        surrounding.append(getGameArea(x, y - 1, gameArea))
    else:
        surrounding.append(None)

    #TopRight
    if x + 1 < width and y - 1 >= 0:
        surrounding.append(getGameArea(x + 1, y - 1, gameArea))
    else:
        surrounding.append(None)
    
    #Right
    if x + 1 < width:
        surrounding.append(getGameArea(x + 1, y, gameArea))
    else:
        surrounding.append(None)

    #RightBottom
    if x + 1 < width and y + 1 < height:
        surrounding.append(getGameArea(x + 1, y + 1, gameArea))
    else:
        surrounding.append(None)

    #Bottom
    if y + 1 < height:
        surrounding.append(getGameArea(x, y + 1, gameArea))
    else:
        surrounding.append(None)

    #LeftBottom
    if x - 1 >= 0 and y + 1 < height:
        surrounding.append(getGameArea(x - 1, y + 1, gameArea))
    else:
        surrounding.append(None)

    #Left, TopLeft, Top, TopRight, Right, RightBottom, Bottom, LeftBottom
    return surrounding # Return list

def simpleDraw(data):
    import pygame
    x, y = data["position"]
    if isinstance(data["size"], list):
        sizeX, sizeY = data["size"]
    else:
        sizeX = data["size"]
        sizeY = sizeX
    pygame.draw.rect(data["screen"], data["colour"], pygame.Rect(x, y, sizeX, sizeY)) # Draw a rectange on the screen where data varible specified

def getGameArea(x, y, area): # A helper function which gets an area in y, x space from x, y
    if x >= 0 and y >= 0 and x < len(area[0]) and y < len(area):
        return area[y][x]
    return None

def setLine(x, y, toX, toY, area, powder, brush_size, replace=False): # A helper function which sets a powder in a line from the start to end line
    ratio = None
    area = drawSize(brush_size, area, x, y, powder, replace)
    if not y - toY == 0: # If the y difference is not 0 (Can't divide by 0)
        ratio = (x - toX) / (y - toY) # Get ratio of x difference to y difference
    if not ratio == None and ratio <= 1 and ratio >= -1:
        cX = x
        for cY in range(y, toY): # If there is a ratio, loop through
            cX += ratio # Add the ratio to the x position
            area = drawSize(brush_size, area, round(cX), cY, powder, replace) # Create a new powder at the position specified
    else:
        if not x - toX == 0: # If the x difference is not 0 (Can't divide by 0)
            ratio = (y - toY) / (x - toX)
        if not ratio == None:
            cY = y
            for cX in range(x, toX): # If there is a ratio, loop through
                cY += ratio # Add the ratio to the y position
                area = drawSize(brush_size, area, round(cX), cY, powder, replace) # Create a new powder at the position specified

def setObjectAtMouse(objectType, mouseHeld, pixelSize, gameArea, previousMousePos, offset_x, brush_size=1, replace=False): # Sets an object at mouse position or removes it if it is a right click
    import math, pygame
    x, y = pygame.mouse.get_pos() # Get position of mouse
    if x >= offset_x and y > 0:
        x -= offset_x
        x /= pixelSize # Divide position of mouse by the pixel size to find which particle it is pointing at
        y /= pixelSize
        x = math.floor(x) # Floor the position so that it is an integer
        y = math.floor(y)
        if x < len(gameArea[0]) and y < len(gameArea):
            if previousMousePos == None:
                previousMousePos = [x, y]
            pX, pY = previousMousePos
            if pX >= offset_x and pY > 0:
                pX -= offset_x
                pX = math.floor(pX / pixelSize)
                pY = math.floor(pY / pixelSize)
                if pX < len(gameArea[0]) and pY < len(gameArea):
                    if getGameArea(x, y, gameArea) == None and mouseHeld[0]: # If it is an empty position and it is a left click
                        setLine(x, y, pX, pY, gameArea, objectType, brush_size, replace) # Create a new powder at the position
                        setLine(pX, pY, x, y, gameArea, objectType, brush_size, replace)
                    elif mouseHeld[1]: # If it is a right click
                        setLine(x, y, pX, pY, gameArea, None, brush_size, True) # Set position's powder to nothing
                        setLine(pX, pY, x, y, gameArea, None, brush_size, True)

def drawSize(size, area, x, y, powder, replace=False):
    if powder == None:
        area = setSquare(x, y, size, area, powder, replace)
    else:
        area = setSquare(x, y, size, area, powder(), replace)
    return area

def setSquare(x, y, i, gameArea, powder, replace=False):
    i -= 1
    if x >= 0 and y >= 0:
        gameArea = setArea(gameArea, round(x), round(y), powder, replace)
    for height in range(i * 2):
        for width in range(i * 2):
            if x + width - i >= 0 and y + height - i >= 0:
                gameArea = setArea(gameArea, round(x + width - i), round(y + height - i), powder, replace)
    return gameArea

def setArea(area, x, y, powder, replace=False):
    try:
        if replace:
            area[y][x] = powder
        elif area[y][x] == None:
            area[y][x] = powder
    except:
        x = x
    return area

def inGameArea(x, y, sizeX, sizeY, offsetX=0, offsetY=0):
    if x >= offsetX and y >= offsetY and x < sizeX + offsetX and y < sizeY + offsetY:
        return True
    else:
        return False

def generateText(font, text, colour="Black"):
    return font.render(text, True, colour)