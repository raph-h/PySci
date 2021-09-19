class Button(): # Base button class which every other button class implements
    def __init__(self, DefaultColour, HoverColour, Position, Size, Text): # Each class should have a default colour, hover colour, position, size and text
        self.DefaultColour = DefaultColour
        self.HoverColour = HoverColour
        self.Position = Position
        self.Size = Size
        self.Text = Text
        self.Colour = None

    def update(self, mouseData): # Update function
        width, height = self.Size
        x, y = self.Position
        mouseX, mouseY = mouseData["mousePos"]
        if x <= mouseX <= x + width and y <= mouseY <= y + height:
            self.Colour = self.HoverColour
            if mouseData["clicking"]:
                return self.callFunction()
        elif self.Colour != self.DefaultColour:
            self.Colour = self.DefaultColour

    def render(self, screen): # Render function
        import Utils, pygame
        data = {"screen": screen, "colour": self.Colour, "position": self.Position, "size": self.Size}
        Utils.simpleDraw(data)
        screen.blit(self.Text, (self.Position[0] + (self.Size[0] - self.Text.get_width()) / 2, self.Position[1] + (self.Size[1] - self.Text.get_height()) / 2))
    
    def callFunction(self):
        return None

class ElementButton(Button): # Button which selects elements
    def __init__(self, DefaultColour, HoverColour, Position, Text, Element, Size=[60, 20]): # Each class should have a default colour, hover colour, position, size, text and a function which is called when it is pressed
        super().__init__(DefaultColour, HoverColour, Position, Size, Text)
        self.Element = Element
    
    def callFunction(self):
        return {"setElement": self.Element}

class SaveButton(Button): # Button which saves game files
    def __init__(self, DefaultColour, HoverColour, Position, Text, FileName): # Each class should have a default colour, hover colour, position, size, text and a function which is called when it is pressed
        super().__init__(DefaultColour, HoverColour, Position, [100, 20], Text)
        self.FileName = FileName
    
    def callFunction(self):
        return {"save": self.FileName}

class LoadButton(Button): # Button which loads game files
    def __init__(self, DefaultColour, HoverColour, Position, Text, FileName): # Each class should have a default colour, hover colour, position, size, text and a function which is called when it is pressed
        super().__init__(DefaultColour, HoverColour, Position, [100, 20], Text)
        self.FileName = FileName
    
    def callFunction(self):
        return {"load": self.FileName}