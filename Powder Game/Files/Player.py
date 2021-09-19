class Player():
    def __init__(self, SpawnPowder, ID="Player", Colour="Orange", Density=1, Health=100, Position=[0,0]): # Each class should have an id, colour and density
        self.ID = ID
        self.Colour = Colour
        self.Density = Density
        self.Health = Health
        self.Position = Position
        self.Size = [10, 25]
        self.SpawnPowder = SpawnPowder
        self.initialise()

    def initialise(self):
        self.OnGround = False
        self.Ticks = 100
        self.Velocity = [0,0]
        self.Health = 100

    def update(self, data): # Update function
        import pygame, Utils, Powders
        dt = data["dt"] * 30
        keys = data["keysPressed"]
        self.Ticks += data["dt"]

        gameArea = data["area"]
        offsetX = data["offset_x"]
        pixelSize = data["size"]
        gameWidth, gameHeight = data["gameSize"]
        pixelWidth = gameWidth / pixelSize
        pixelHeight = gameHeight / pixelSize

        x = int((self.Position[0] - offsetX + self.Size[0] / 2) / pixelSize)
        y = int((self.Position[1] + self.Size[1] - pixelSize) / pixelSize)
        self.OnGround = self.colliding(x, y, gameArea, pixelWidth, pixelHeight)

        if not self.OnGround and self.Ticks > .3:
            self.Velocity[1] += data["gravity"] * dt
        elif not self.OnGround and self.Ticks > .1:
            self.Velocity[1] += 1 * dt
        if pygame.K_UP in keys:
            if self.OnGround:
                self.Ticks = 0
                self.Velocity[1] -= 40
                self.OnGround = False
        if pygame.K_DOWN in keys:
            self.Velocity[1] += 1
        if pygame.K_LEFT in keys:
            self.Velocity[0] -= 1
        if pygame.K_RIGHT in keys:
            self.Velocity[0] += 1

        if not (pygame.K_UP in keys or pygame.K_DOWN in keys):
            if self.Velocity[1] > 0:
                self.Velocity[1] -= 1
            elif not self.Velocity[1] == 0:
                self.Velocity[1] += 1

        if not (pygame.K_LEFT in keys or pygame.K_RIGHT in keys):
            if self.Velocity[0] > 0:
                self.Velocity[0] -= 1
            elif not self.Velocity[0] == 0:
                self.Velocity[0] += 1

        if self.Velocity[0] > 0:
            self.Velocity[0] = min(self.Velocity[0], 10)
        else:
            self.Velocity[0] = max(self.Velocity[0], -10)
        if self.Velocity[1] > 0:
            self.Velocity[1] = min(self.Velocity[1], 10)
        else:
            self.Velocity[1] = max(self.Velocity[1], -10)
        
        if Utils.inGameArea(self.Position[0] + self.Velocity[0], self.Position[1], gameWidth, gameHeight, offsetX) and Utils.inGameArea(self.Position[0] + self.Velocity[0] + self.Size[0], self.Position[1], gameWidth, gameHeight, offsetX):
            newPos = self.Position[0] + self.Velocity[0] * dt
            if self.Velocity[0] * dt > 0:
                if self.collidingSideWays(newPos + self.Size[0], x + 1, y, gameArea, pixelSize, offsetX) or self.collidingSideWays(newPos + self.Size[0], x + 2, y, gameArea, pixelSize, offsetX):
                    self.Velocity[0] = 0
                else:
                    self.Position[0] = newPos
            elif self.collidingSideWays(newPos, x - 1, y, gameArea, pixelSize, offsetX) or self.collidingSideWays(newPos, x - 2, y, gameArea, pixelSize, offsetX):
                self.Velocity[0] = 0
            else:
                self.Position[0] = newPos
        else:
            if self.Position[0] + self.Velocity[0] >= gameWidth + offsetX - self.Size[0]:
                self.Position[0] = gameWidth + offsetX - self.Size[0]
            elif self.Position[0] + self.Velocity[0] < offsetX:
                self.Position[0] = offsetX
        
        if Utils.inGameArea(self.Position[0], self.Position[1] + self.Velocity[1], gameWidth, gameHeight, offsetX) and Utils.inGameArea(self.Position[0], self.Position[1] + self.Velocity[1] + self.Size[1], gameWidth, gameHeight, offsetX):
            newPos = self.Position[1] + self.Velocity[1] * dt
            if self.OnGround and self.Velocity[1] * dt > 0:
                self.Velocity[1] = -1
            else:
                self.Position[1] = newPos
        else:
            if self.Position[1] + self.Velocity[1] >= gameHeight - self.Size[1]:
                self.Position[1] = gameHeight - self.Size[1]
            elif self.Position[1] + self.Velocity[1] < 0:
                self.Position[1] = 0

        if y < pixelHeight and x < pixelWidth:
            if isinstance(gameArea[y][x], Powders.Lava):
                self.Health -= 1 * dt
        if y + 1 < pixelHeight and x < pixelWidth:
            if isinstance(gameArea[y + 1][x], Powders.Lava):
                self.Health -= 1 * dt
        if self.Health <= 0:
            if self.SpawnPowder == None:
                self.SpawnPowder.playerDead(self)
                return {"Dead": True}
            else:
                particleValid = False
                for i in range(int(pixelHeight)):
                    row = gameArea[i]
                    if self.SpawnPowder in row:
                        index = row.index(self.SpawnPowder)
                        if index != None:
                            self.Position = [index * pixelSize + offsetX, i * pixelSize]
                            self.initialise()
                            particleValid = True
                if not particleValid:
                    self.SpawnPowder = None
                    return {"Dead": True}

    def render(self, screen, font): # Render function
        import Utils
        text = Utils.generateText(font, str(int(self.Health)), "White")
        screen.blit(text, (self.Position[0] + (self.Size[0] - text.get_width()) / 2, self.Position[1] - text.get_height()))
        Utils.simpleDraw({"position": self.Position, "size": self.Size, "screen": screen, "colour": self.Colour})
    
    def collidingElement(self, element):
        import Powders
        if element != None and not isinstance(element, Powders.LiquidPowder) and not isinstance(element, Powders.PlayerSpawn) and not isinstance(element, Powders.GasPowder):
            return True
        return False

    def colliding(self, x, y, gameArea, width, height):
        if y < height and y >= 0 and x < width and x >= 0:
            if y >= height - 1 or self.collidingElement(gameArea[y][x]):
                return True
        if y + 1 < height and y >= 0 and x < width and x >= 0:
            if self.collidingElement(gameArea[y + 1][x]):
                return True
        if y - 1 >= 0 and y - 1 < height and x < width and x >= 0:
            if self.collidingElement(gameArea[y - 1][x]):
                return True
        return False

    def collidingSideWays(self, worldX, powderX, powderY, gameArea, pixelSize, offsetX):
        import Powders
        if powderY < len(gameArea) and powderY >= 0 and powderX < len(gameArea[0]) and powderX >= 0:
            element = gameArea[powderY][powderX]
            if powderX < len(gameArea[0]) and powderX >= 0:
                if self.collidingElement(element):
                    if worldX < powderX * pixelSize + pixelSize + offsetX and worldX >= powderX * pixelSize + offsetX:
                        return True
        if powderY - 1 < len(gameArea) and powderY - 1 >= 0 and powderX < len(gameArea[0]) and powderX >= 0:
            element = gameArea[powderY - 1][powderX]
            if powderX < len(gameArea[0]) and powderX >= 0:
                if self.collidingElement(element):
                    if worldX < powderX * pixelSize + pixelSize + offsetX and worldX >= powderX * pixelSize + offsetX:
                        return True
        if powderY - 2 < len(gameArea) and powderY - 2 >= 0 and powderX < len(gameArea[0]) and powderX >= 0:
            element = gameArea[powderY - 2][powderX]
            if powderX < len(gameArea[0]) and powderX >= 0:
                if self.collidingElement(element):
                    if worldX < powderX * pixelSize + pixelSize + offsetX and worldX >= powderX * pixelSize + offsetX:
                        return True
        return False