def resolveMovement(newObject, gameArea): # Recieves a list of movement data of each object
    import Utils
    setList = []
    for obj in newObject: # Iterate over all object data
        position = obj["position"] # Get position of object
        newPos = obj["data"]["position"] # Get it's new position the object wants to be at
        if "set" in obj["data"].keys():
            setList.append(obj["data"]["set"])
        if position != newPos: # Only continue if the new position is not equal to the origional position
            particle = Utils.getGameArea(position[0], position[1], gameArea) # Get the particle at the position
            if newPos[1] < len(gameArea) and newPos[1] >= 0:
                if newPos[0] < len(gameArea[newPos[1]]) and newPos[0] >= 0: # If new position is in bounds of game area
                    otherParticle = Utils.getGameArea(newPos[0], newPos[1], gameArea) # Get particle of new position
                    if otherParticle == None: # If there is no particle in the new area, swap the particles
                        gameArea[position[1]][position[0]] = None
                        gameArea[newPos[1]][newPos[0]] = particle
                    elif otherParticle.canSwap({"other": particle}): # If there is another particle, check if they can swap position and if so, swap the particles
                        gameArea[position[1]][position[0]] = otherParticle
                        gameArea[newPos[1]][newPos[0]] = particle
    setElements(setList, gameArea)
    return gameArea # Return new game area with objects which have moved

def setElements(setList, gameArea):
    import Utils
    for row in setList:
        for info in row:
            x = info[0]
            y = info[1]
            if (Utils.inGameArea(x, y, len(gameArea[0]), len(gameArea))):
                if info[2] != None:
                    gameArea[y][x] = info[2]()
                else:
                    gameArea[y][x] = info[2]

def sortDensities(gameArea, offset): # Sorts densities of liquids
    for y in range(offset, len(gameArea), 2): # Contains an offset so that only half the particles are sorted and the other half will be sorted next frame
        if y + 1 < len(gameArea):
            for x in range(len(gameArea[y])): # Loop through all particles in game area
                if sortDensity(gameArea[y][x], gameArea[y + 1][x]): # Call sort density function on the particle and the one below it and if it returns true, swap the two particles
                    part = gameArea[y][x] # Swap particles
                    gameArea[y][x] = gameArea[y + 1][x]
                    gameArea[y + 1][x] = part
    return gameArea # Return new game area with densities "sorted"

def sortDensity(itself, other): # Returns if a particle can swap with the one below
    import Powders
    if isinstance(itself, Powders.LiquidPowder): # Return false if it is not a liquid
        if itself == None or other == None: # If any of the sides are none, return false
            return False
        return other.canSwap({"other": itself}) # Return true if the particles can swap
    else:
        return False