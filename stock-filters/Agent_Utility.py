import random
import math
import time
import numpy as np
import matplotlib.pyplot as plt

DIRECTIONS = [(-1, 0), (0, -1), (1, 0), (0, 1)]


def change_direction(direction, turn):
    return (direction + turn) % 4


def is_free(freeMap, square, xCoord, yCoord):
    return not (not validCoordinate(square, (xCoord, yCoord)) or freeMap[yCoord - square[0][1]][xCoord - square[0][0]] == 1)


def plot_maps(mapList):
    for xMap in mapList:
        plt.imshow(xMap, cmap="gray")
        plt.show(False)


def spawn_village_entrance(square, heightMap, offset=4):
    border_coordinates = []

    for coord in range(square[0][1] + offset, square[1][1] - offset):
        border_coordinates.append((square[0][0], coord))
        border_coordinates.append((square[1][0]-1, coord))

    for coord in range(square[0][0] + offset + 1, square[1][0] - offset - 1):
        border_coordinates.append((coord, square[0][1]))
        border_coordinates.append((coord, square[1][1]-1))

    coordinate = random.sample(border_coordinates, 1)[0]

    if coordinate[0] == square[0][0]:
        directionCode = 2
    elif coordinate[0] == square[1][0] - 1:
        directionCode = 0
    elif coordinate[1] == square[0][1]:
        directionCode = 3
    else:
        directionCode = 1

    return [coordinate[0], heightMap[coordinate[1]][coordinate[0]], coordinate[1]], directionCode


def attemptRoomSpawn(level, box, currentSquare, agentPosition, freeMap):
    roomDimensions = (3, 5)
    roomWidths = range(roomDimensions[1], roomDimensions[0], -1)
    roomDepths = range(roomDimensions[1], roomDimensions[0], -1)
    roomSizes = [[x, y] for x in roomWidths for y in roomDepths]
    for (roomWidth, roomDepth) in random.sample(roomSizes, len(roomSizes)):
        yRange = range(agentPosition[1] - divideAndFloor(roomDepth, 2), agentPosition[1] + divideAndCeil(roomDepth, 2))
        xRange = range(agentPosition[0] - divideAndFloor(roomWidth, 2), agentPosition[0] + divideAndCeil(roomWidth, 2))
        if attemptPlacement(currentSquare, (xRange, yRange), freeMap):
            placeObject(level, box, currentSquare, (xRange, yRange, 2), agentPosition, freeMap, (5, 0))
            return True
    return False


def attemptCorridorSpawn(level, box, currentSquare, agentPosition, freeMap):
    corridorLengths = range(8, 3, -1)
    directions = [[-1, 0], [1, 0], [0, 1], [0, -1]]
    corridorPossibilities = [[x, y] for x in directions for y in corridorLengths]
    for direction, corridorLength in random.sample(corridorPossibilities, len(corridorPossibilities)):
        corridorDimensions = [direction[0] * corridorLength, direction[1] * corridorLength]
        if corridorDimensions[0] == 0:
            corridorDimensions[0] = 1
        elif corridorDimensions[1] == 0:
            corridorDimensions[1] = 1

        directions = [1, 1]
        if corridorDimensions[0] < 0:
            directions[0] = -1
        if corridorDimensions[1] < 0:
            directions[1] = -1

        yRange = range(agentPosition[1], agentPosition[1] + corridorDimensions[1], directions[1])
        xRange = range(agentPosition[0], agentPosition[0] + corridorDimensions[0], directions[0])

        if attemptPlacement(currentSquare, (xRange, yRange), freeMap):
            placeObject(level, box, currentSquare, (xRange, yRange), agentPosition, block=(1, 0))
            agentPosition[0] += direction[0] * corridorLength
            agentPosition[1] += direction[1] * corridorLength
            return True
    return False


def placeObject(level, box, square, ranges, agentPosition, freeMap=None, block=(4, 0), code=1):
    for yCoord in ranges[1]:
        for xCoord in ranges[0]:
            placeBlockAt(level, box, (xCoord, agentPosition[2], yCoord), block)
            try:
                for i in range(0, ranges[2]):
                    placeBlockAt(level, box, (xCoord, agentPosition[2] + i, yCoord), block)
            except:
                pass

    if freeMap is None:
        return

    ranges[1].insert(0, ranges[1][0] - 1)
    ranges[1].append(ranges[1][1] + 1)
    ranges[0].insert(0, ranges[0][0] - 1)
    ranges[0].append(ranges[0][1] + 1)

    for yCoord in ranges[1]:
        for xCoord in ranges[0]:
            freeMap[yCoord - square[0][1]][xCoord - square[0][0]] = code

    return freeMap


def placeBlockAt(level, box, coordinates, block):
    level.setBlockAt(int(box.minx + coordinates[0]), int(coordinates[1]), int(box.minz + coordinates[2]), block[0])
    level.setBlockDataAt(int(box.minx + coordinates[0]), int(coordinates[1]), int(box.minz + coordinates[2]), block[1])


"""
Take the given ranges of coordinates to create a 2-dimensional array and check the 
free space map for any collision with existing objects.
"""
def attemptPlacement(square, ranges, freeMap):
    for yCoord in ranges[1]:
        for xCoord in ranges[0]:
            if not validCoordinate(square, (xCoord, yCoord)):
                return False
            if freeMap[yCoord - square[0][1]][xCoord - square[0][0]] == 1:
                return False
    return True


# Checks whether the given coordinate lies inside the given square coordinate boundary.
def validCoordinate(square, coordinate):
    return square[0][0] <= coordinate[0] < square[1][0] and square[0][1] <= coordinate[1] < square[1][1]


# Divide the given numbers and round down the result.
def divideAndFloor(numerator, denominator):
    return int(math.floor(numerator / denominator))


# Divide the given numbers and round up the result.
def divideAndCeil(numerator, denomenator):
    return int(math.ceil(float(numerator) / float(denomenator)))


# Loop through the given 2-Dimensional Array and print the items in an easy to read manner.
def printMap(map, type):
    print("\n" + type + " Map:")
    for yCoord in range(0, len(map)):
        line = ""
        for xCoord in range(0, len(map[0])):
            line += (str(map[yCoord][xCoord]) + "\t")
        print(line)
