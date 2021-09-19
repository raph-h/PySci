class PrimativePowder(): # Base powder class which every other powder class implements
    def __init__(self, Colour="Black", Density=1): # Each class should have an id, colour and density
        self.Colour = Colour
        self.Density = Density

    def update(self, data): # Update function
        return None

    def render(self, data): # Render function
        import Utils
        data["colour"] = self.Colour
        Utils.simpleDraw(data) # Default render function

    def canSwap(self, data): # Function to sort out powders to see if they can swap positions
        return False
    
class LiquidPowder(PrimativePowder): # Liquid powder
    def __init__(self, Viscosity=1, Colour="White", Density=1): # Each liquid should have the same variables as the primative powder but also include viscosity and a tick to help randomise flow
        super().__init__(Colour, Density)
        self.Viscosity = Viscosity

    def update(self, data):
        import random, Utils
        if data["position"][1] + 1 < data["height"] and Utils.getSurroundingObjects(data["area"], data["position"])[6] == None: # If liquid can move down
            return {"position": [data["position"][0], data["position"][1] + 1]} # Sends data to tell the program to move the liquid down
        else: # If liquid cannot move down
            ran = 0
            if data["position"][0] <= 0: # Try to move liquid right if it is on the left edge of screen
                ran = 1
            elif data["position"][0] >= data["width"]: # Try to move liquid left if it is on the right edge of screen
                ran = -1
            else: # Move liquid in a random position
                ran = random.randint(-self.Viscosity, self.Viscosity)
            return {"position": [data["position"][0] + ran, data["position"][1]]} # Send data of new movement of liquid

    def canSwap(self, data): 
        if data["other"].Density > self.Density: # Allow the other particle to move if it is more dense than the liquid
            return True
        else:
            return False

class GasPowder(PrimativePowder):
    def __init__(self, Colour="Grey", Density=0.5, Viscosity=2): # Each class should have an id, colour and density
        super().__init__(Colour, Density)
        self.Viscosity = Viscosity

    def update(self, data): # Update function
        import random, Utils
        if data["position"][1] - 1 >= 0 and Utils.getSurroundingObjects(data["area"], data["position"])[2] == None: # If gas can move up
            return {"position": [data["position"][0], data["position"][1] - 1]} # Sends data to tell the program to move the gas up
        else: # If gas cannot move up
            ran = 0
            if data["position"][0] <= 0: # Try to move gas right if it is on the left edge of screen
                ran = 1
            elif data["position"][0] >= data["width"]: # Try to move gas left if it is on the right edge of screen
                ran = -1
            else: # Move liquid in a random position
                ran = random.randint(-self.Viscosity, self.Viscosity)
            return {"position": [data["position"][0] + ran, data["position"][1]]} # Send data of new movement of gas
    
    def canSwap(self, data): 
        if data["other"].Density > self.Density: # Allow the other particle to move if it is more dense than the gas
            return True
        else:
            return False

class Powder(PrimativePowder): # A default powder
    def __init__(self, Colour="Yellow", Density=1): # Have the default colour as yellow
        super().__init__(Colour, Density)

    def update(self, data):
        import random, Utils
        if data["position"][1] + 1 < data["height"] and Utils.getSurroundingObjects(data["area"], data["position"])[6] == None:
            return {"position": [data["position"][0], data["position"][1] + 1]} # Sends data to tell powder to move down if it can
        else:
            return {"position": [data["position"][0] + random.randint(-1, 1), data["position"][1] + 1]} # Sends data to try to move it diagonally down

class Solid(PrimativePowder): # Default solid
    def __init__(self, Colour="Gray"): # A powder with a default colour as grey and has no movement
        super().__init__(Colour)

class Steam(GasPowder):
    def __init__(self):
        super().__init__((104, 118, 129))

class Water(LiquidPowder):
    def __init__(self):
        super().__init__(3, "Blue", 1)

    def update(self, data):
        import Utils
        returningData = super().update(data)
        pos = data["position"]
        surrounding = Utils.getSurroundingObjects(data["area"], pos)
        for surround in surrounding:
            if isinstance(surround, Lava):
                returningData["set"] = [[pos[0], pos[1], Steam]]
        return returningData

class Lava(LiquidPowder):
    def __init__(self):
        super().__init__(1, "Red", 5)

    def update(self, data):
        import Utils
        returningData = super().update(data)
        pos = data["position"]
        surrounding = Utils.getSurroundingObjects(data["area"], pos)
        for surround in surrounding:
            if isinstance(surround, Water):
                returningData["set"] = [[pos[0], pos[1], Rock]]
        return returningData

class Sand(Powder):
    def __init__(self):
        super().__init__("Yellow", 2)

class Rock(Powder):
    def __init__(self):
        super().__init__("Grey", 5)

class Hole(Solid): # A powder which sets its surrounding powders to none
    def __init__(self):
        super().__init__("White")

    def update(self, data):
        pos = data["position"]
        return {"position": [pos[0], pos[1]], "set": [[pos[0] + 1, pos[1], None], [pos[0] - 1, pos[1], None], [pos[0], pos[1] + 1, None], [pos[0], pos[1] - 1, None], [pos[0] + 1, pos[1] + 1, None], [pos[0] - 1, pos[1] + 1, None], [pos[0] + 1, pos[1] - 1, None], [pos[0] - 1, pos[1] - 1, None]]} # Return data to set its surroundings to none

class PlayerSpawn(Solid):
    def __init__(self):
        super().__init__("Orange")
        self.Player = None

    def update(self, data):
        import Player
        if self.Player == None:
            position = data["position"]
            size = data["size"]
            self.Player = Player.Player(self, Position=[position[0] * size + data["offset_x"], position[1] * size])
            return {"position": data["position"], "addPlayer": self.Player}
    
    def playerDead(self, player):
        if player == self.Player:
            self.Player = None

class Duplicator(Solid):
    def __init__(self):
        super().__init__("Green")
        self.Powder = None

    def update(self, data):
        import Utils
        position = data["position"]
        if self.Powder == None:
            surroundings = Utils.getSurroundingObjects(data["area"], position)
            for surround in surroundings:
                if surround != None and not isinstance(surround, Duplicator) and self.Powder == None:
                    self.Powder = type(surround)
        else:
            return {"position": position, "set": [[position[0] + 1, position[1], self.Powder], [position[0] - 1, position[1], self.Powder], [position[0], position[1] + 1, self.Powder], [position[0], position[1] - 1, self.Powder]]}
def getElementFromString(string):
    import sys
    return getattr(sys.modules[__name__], string)

class TutorialText(Solid):
    def __init__(self): # A powder which shows text
        super().__init__("Grey")

    def render(self, data): # Render function
        import Utils
        # Render text
        text = 'Hello, this is the tutorial, on the left panel are the elements you can "place" onto the game area'
        text2 = 'Just simply click on the element and click / drag to place elements on the screen, you can also right click / drag to remove elements'
        text3 = 'Elements can interact with each other interestingly, go experiment!'
        text4 = 'There is also a work in progress player which can interact with the elements such as die, simply place the player element and it acts as a respawn point'
        text5 = 'On the right side are load and save buttons, the save file and load file are for you to use'
        text6 = 'The load game button loads a game, the clear game button clears the screen from elements'
        text7 = 'And thats it! Additionally, you can press space bar to pause the simulation and you use the arrow keys to move the player'
        data["screen"].blit(Utils.generateText(data["font"], text, "White"), [120, 50])
        data["screen"].blit(Utils.generateText(data["font"], text2, "White"), [120, 100])
        data["screen"].blit(Utils.generateText(data["font"], text3, "White"), [120, 150])
        data["screen"].blit(Utils.generateText(data["font"], text4, "White"), [120, 200])
        data["screen"].blit(Utils.generateText(data["font"], text5, "White"), [120, 250])
        data["screen"].blit(Utils.generateText(data["font"], text6, "White"), [120, 300])
        data["screen"].blit(Utils.generateText(data["font"], text7, "White"), [120, 350])