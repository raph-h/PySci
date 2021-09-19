VERSION = "1.1" # Version of the program
print("Version: " + VERSION)

# Import all modules and classes and functions and files
import pygame
import time
from pygame.locals import *
from os import path

from Powders import *
from Player import *
from Buttons import *
import Physics
import File
import Utils

clock = pygame.time.Clock() # Get clock

screen = None
background = None

# Window variables
WWIDTH = 1296
WHEIGHT = 650

# Default values
pixelSize = 6
fps_cap = 30
brush_size = 1

options = open(path.abspath(path.join(path.dirname(__file__), "..", "options.txt")), "r") # Load option file
for option in options:
    if option != None:
        option = option.split(" ")
        if option[0] != "#":
            if option[0] == "fps_cap":
                fps_cap = int(option[1])
            if option[0] == "pixel_size":
                pixelSize = int(option[1])
            if option[0] == "brush_size":
                brush_size = int(option[1])
options.close() # Close option file

WIDTH = int(1080 / pixelSize)
HEIGHT = int(600 / pixelSize)

OFFSET_X = (WWIDTH - (WIDTH * pixelSize)) / 2

font = None

# To stop program if paused
paused = False

# Variable to store which determines if the mouse is down
mouseHeld = [False, False]
previousMousePos = None
selectedPowder = Solid

keysPressed = []

buttonList = []
playerList = []
gravity = 9.8 # Pixels
gameArea = [] # Arranged as
"""
[[00, 01, 02],
[10, 11, 12],
[20, 21, 22]]
"""
def initialise(): # Function which initialises the game
    global screen, background, gameArea, font
    # Initialise screen
    print("Initialising screen")
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((WWIDTH, WHEIGHT))
    pygame.display.set_caption("PySci - Powder Game")

    # Fill background
    print("Initialising background")
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((50, 50, 50))

    # Fill area with solid "blocks"
    print("Generating game area")
    gameArea = generateGameArea(WIDTH, HEIGHT)

    print("Generating font")
    posX = OFFSET_X / 2 - 30
    font = pygame.font.SysFont('Comic Sans MS', 15)

    print("Registering elements") # Register elements
    registerElement("Blue", "Dark Blue", Water, posX, font)
    registerElement("Red", "Dark Red", Lava, posX, font)
    registerElement("Yellow", (99, 80, 00), Sand, posX, font)
    registerElement("Dark Grey", (60, 60, 60), Solid, posX, font)
    registerElement((200, 200, 200), "White", Hole, posX, font)
    registerElement("Orange", (191, 87, 0), PlayerSpawn, posX, font, "Player")
    registerElement("Green", (0, 100, 0), Duplicator, posX - 10, font, size=[80,20])

    print("Creating more buttons") # Register buttons
    buttonList.append(SaveButton("Grey", (60, 60, 60), [WIDTH * pixelSize + OFFSET_X + 5, 10], Utils.generateText(font, "Save File"), "SaveFile.save"))
    buttonList.append(LoadButton("Grey", (60, 60, 60), [WIDTH * pixelSize + OFFSET_X + 5, 40], Utils.generateText(font, "Load File"), "SaveFile.save"))
    buttonList.append(LoadButton("Grey", (60, 60, 60), [WIDTH * pixelSize + OFFSET_X + 5, 70], Utils.generateText(font, "Load Game"), "Game.save"))
    buttonList.append(LoadButton("Grey", (60, 60, 60), [WIDTH * pixelSize + OFFSET_X + 5, 100], Utils.generateText(font, "Load Tutorial"), "Tutorial.save"))
    buttonList.append(LoadButton("Grey", (60, 60, 60), [WIDTH * pixelSize + OFFSET_X + 5, 130], Utils.generateText(font, "Clear Game"), "Clear.save"))
    print("Initialisation complete")

offset = 0
def update(): # Update function which is called
    global gameArea, offset
    clock.tick(fps_cap) # Tick the clock
    dt = getDeltaTime()

    updateKeys() # Get keys pressed and depending on what is pressed, do something

    objectData = [] # Will contain information on objects which have moved or have changed position
    # Loop through all objects in gameArea
    if not paused: # Only loop if game is not paused
        for r in range(HEIGHT): # y
            row = gameArea[r] # Get row of game area
            for p in range(WIDTH): # x
                obj = row[p] # Get the object in the game area
                if obj != None:
                    returnData = obj.update({"width": WIDTH, "height": HEIGHT, "position": [p, r], "area": gameArea, "offset_x": OFFSET_X, "size": pixelSize}) # Update the object and gather any data sent                        
                    if returnData != None:
                        objectData.append({"position": [p, r], "data": returnData}) # Add new data to list of information on objects which have moved
                        handlePowders(returnData)
        gameArea = Physics.resolveMovement(objectData, gameArea) # Using the list of information, move objects and calculate physics
        if offset == 1: # Change offset from 0 to 1,
            offset = 0
        else:
            offset = 1
        gameArea = Physics.sortDensities(gameArea, offset) # Sort densities of liquids depending on offset, offset used so that the liquids arent all sorted in one frame
        
        deadPlayers = []
        for player in playerList: # Update players
            output = player.update({"keysPressed": keysPressed, "area": gameArea, "offset_x": OFFSET_X, "size": pixelSize, "gravity": gravity, "dt": dt, "gameSize": [WIDTH * pixelSize, HEIGHT * pixelSize], "fps": clock.get_fps()})
            if output != None:
                if output["Dead"]:
                    deadPlayers.append(player)
        for player in deadPlayers:
            playerList.remove(player)

def render():
    # Blit background to the screen
    screen.blit(background, (0, 0))
    pygame.draw.rect(screen, (30, 30, 30), pygame.Rect(OFFSET_X, 0, WIDTH * pixelSize, HEIGHT * pixelSize)) # Draw a darker rectangle for game area

    for r in range(HEIGHT): # For every element in table, call its render function
        row = gameArea[r]
        for p in range(WIDTH):
            obj = row[p]
            if obj != None:
                obj.render({"position": [p * pixelSize + OFFSET_X, r * pixelSize], "size": pixelSize, "screen": screen, "font": font}) # Call its render function with inputs to its position
    for player in playerList:
            player.render(screen, font)

    for button in buttonList: # Iterate over all buttons in list
        button.render(screen) # Render button

    screen.blit(Utils.generateText(font, "FPS: " + str(int(clock.get_fps())), "White"), (OFFSET_X, 0))

    # Display all the blitted objects
    pygame.display.flip()

def generateGameArea(width, height): # Generate a table depending on how many rows and columns it should have
    gameArea = []
    for y in range(height):
        gameArea.append([None] * width)
    return gameArea

def updateKeys(): # Called every update and processes keybinds and mouse
    import Utils
    global Running, mouseHeld, previousMousePos, paused, keysPressed
    for event in pygame.event.get():
        if event.type == QUIT: # When program wants to quit
            Running = False
        if event.type == pygame.MOUSEBUTTONDOWN: # When mouse is down
            updateButtons(True) # Update buttons with mouse being down
            previousMousePos = pygame.mouse.get_pos()
            if event.button == 1: # Left click
                mouseHeld[0] = True
            if event.button == 3: # Right click
                mouseHeld[1] = True
            Utils.setObjectAtMouse(selectedPowder, mouseHeld, pixelSize, gameArea, previousMousePos, OFFSET_X) # Add a solid or remove particles in the game area where mouse is            
        else:
            updateButtons(False) # Update buttons with mouse being up
        
        if event.type == pygame.MOUSEBUTTONUP: # When mouse is released
            previousMousePos = None
            if event.button == 1: # Left click
                mouseHeld[0] = False
            if event.button == 3: # Right click
                mouseHeld[1] = False
        if event.type == pygame.MOUSEMOTION: # If mouse is moved
            Utils.setObjectAtMouse(selectedPowder, mouseHeld, pixelSize, gameArea, previousMousePos, OFFSET_X, brush_size)      
            previousMousePos = pygame.mouse.get_pos()
        
        if event.type == pygame.KEYDOWN: # If a key is down
            if event.key == pygame.K_SPACE:
                paused = not paused # Toggle paused to opposite value
            keysPressed.append(event.key)
        
        if event.type == pygame.KEYUP:
            if event.key in keysPressed:
                keysPressed.remove(event.key)
    if mouseHeld[0] or mouseHeld[1]:
        Utils.setObjectAtMouse(selectedPowder, mouseHeld, pixelSize, gameArea, previousMousePos, OFFSET_X, brush_size)

def updateButtons(mouseClicking): # Called to update all buttons
    import pygame
    pos = pygame.mouse.get_pos() # Get position of mouse
    buttonData = []
    for button in buttonList: # Iterate over all buttons in list
        data = button.update({"mousePos": pos, "clicking": mouseClicking}) # Get button and update it with data
        if data != None:
            buttonData.append(data)

    for button in buttonData:
        handleButtons(button)

def handleButtons(buttonData): # Handles button functions
    global selectedPowder, gameArea, playerList
    if "setElement" in buttonData:
        selectedPowder = buttonData["setElement"]
    if "save" in buttonData:
        File.save(buttonData["save"], pixelSize, gameArea)
    if "load" in buttonData:
        gameArea = generateGameArea(WIDTH, HEIGHT)
        playerList = []
        gameArea = File.load(buttonData["load"], pixelSize, gameArea)

def handlePowders(powderData): # Handles powder functions
    if "addPlayer" in powderData:
        playerList.append(powderData["addPlayer"])

ticksLastFrame = 0
def getDeltaTime(): # Gets delta time in seconds
    global ticksLastFrame
    t = pygame.time.get_ticks()
    deltaTime = (t - ticksLastFrame) / 1000.0
    ticksLastFrame = t
    return deltaTime

height = 10
def registerElement(colour, selectedColour, element, posX, font, name="", size=[60,20]): # Function which helps with the addition of elements
    global buttonList, height
    if name == "":
        name = element.__name__
    buttonList.append(ElementButton(colour, selectedColour, [posX, height], Utils.generateText(font, name), element, Size=size))
    height += 30

initialise() # Initialise the program
Running = True # Set running to true
while Running: # While running is true, loop through program
    update() # Update the program
    render() # Draw to the screen