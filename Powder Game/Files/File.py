from os import path
prefix = path.abspath(path.join(path.dirname(__file__), "..", "Saves")) + "/"
def save(fileName, pixelSize, gameArea): # Save game files
    string = str(pixelSize) + "\n"
    for row in gameArea:
        for element in row:
            string += type(element).__name__ + " " # Add name of powder to the string
        string += "\n"
    open(prefix + fileName, 'w').write(string)
    print("Saved file: " + fileName)

def load(fileName, pixelSize, gameArea): # Load game files
    import sys, os, Powders
    height = len(gameArea)
    width = len(gameArea[0])

    if os.path.isfile(prefix + fileName):
        file = open(prefix + fileName, "r")
        i = 0
        for line in file:
            if line != None:
                line = line.strip()
                words = line.split(" ")
                if words[0].isnumeric():
                    filePixelSize = int(words[0])
                    if pixelSize != filePixelSize:
                        print("File pixel sizes imcompatible, errors may occur")
                else:
                    for e in range(len(words)):
                        element = words[e]
                        if i < height + 1 and e < width:
                            if element != "NoneType":
                                gameArea[i - 1][e] = Powders.getElementFromString(element)()
                            else:
                                gameArea[i - 1][e] = None
            i += 1
        file.close()
    print("Loaded file: " + fileName)
    return gameArea