import numpy as np
import utility
import matplotlib.pyplot as plt
import Agent_Utility

# Block ID's which are not solid, cannot be walked on.
NONSURFACE = [0, 6, 8, 9, 17, 18, 31, 32, 37, 38, 39, 40, 50, 51, 59, 63, 75, 76, 78, 81, 82, 83, 86, 92, 99, 100, 103,
              104, 105, 106, 111, 115, 127, 140, 141, 142, 161, 162, 166, 175, 176, 177, 199, 200, 207, 255]

"""
Analyse the chunk given and extract a 2D height map representation of the terrain.
for later use.
"""


def extractHeightMap(level, box):
    (x1, y1, z1) = (box.minx, box.miny, box.minz)
    (x2, y2, z2) = (box.maxx, box.maxy, box.maxz)

    regionWidth = x2 - x1
    regionDepth = z2 - z1
    regionHeight = 0

    heightMap = np.zeros((regionDepth, regionWidth))
    idMap = np.zeros((regionDepth, regionWidth))
    dataMap = np.zeros((regionDepth, regionWidth))

    # Loop through the Z-Coordinate Space
    for zCoord in np.arange(z1, z2):

        # Loop through the X-Coordinate Space
        for xCoord in np.arange(x1, x2):

            yCoord = box.maxy

            # Loop downward from the top of the Y-Coordinate space until the bottom
            while yCoord >= y1:
                yCoord -= 1
                voxel = level.blockAt(xCoord, yCoord, zCoord)

                # If a non-empty voxel is found, store the height of the coordinate
                if voxel not in NONSURFACE:
                    dataMap[zCoord - z1][xCoord - x1] = level.blockDataAt(xCoord, yCoord, zCoord)
                    heightMap[zCoord - z1][xCoord - x1] = yCoord
                    idMap[zCoord - z1][xCoord - x1] = voxel

                    if yCoord > regionHeight:
                        regionHeight = yCoord
                    break

    return heightMap, idMap, dataMap, (regionWidth, regionDepth, regionHeight)


"""
Take the heightmap and compute the differences in heights between neigbouring tiles
to construct the edgemap.  Sensitivity defines how many neighbouring tiles affect
affect the edgemap entries.
"""


def extractSmoothnessMap(heightMap, sensitivity):
    width, depth = heightMap.shape
    smoothnessMap = np.zeros((width, depth))
    for yCoord in range(0, width):
        for xCoord in range(0, depth):
            count = 0
            neighbourDeltas = 0
            referenceTile = heightMap[yCoord][xCoord]

            for yOffset in range(-sensitivity, sensitivity + 1):
                for xOffset in range(-sensitivity, sensitivity + 1):
                    if not (xOffset == 0 and yOffset == 0):
                        if (0 <= yCoord + yOffset < width) and (0 <= xCoord + xOffset < depth):
                            neighbourTile = heightMap[yCoord + yOffset][xCoord + xOffset]
                            neighbourDeltas += abs(referenceTile - neighbourTile)
                            count += 1
            smoothnessMap[yCoord][xCoord] = round(neighbourDeltas / count, 1)
    return smoothnessMap


"""
Function which takes the edge map and identifies flat square regions which can be used
to build structures with the contructive agents further down the line.
"""


def extractFlatSquares(edgeMap, maxRoughness, minSize=100):
    squares = []
    flatMap = np.zeros(edgeMap.shape, int)
    for yCoord in range(0, edgeMap.shape[0]):
        for xCoord in range(0, edgeMap.shape[1]):
            if flatMap[yCoord][xCoord] == 0:
                if edgeMap[yCoord][xCoord] < maxRoughness:
                    flatMap[yCoord][xCoord] = 1
    while True:
        square, flatMap = extractFlatSquare(flatMap)
        if square[1][0] - square[0][0] >= minSize:
            squares.append(square)
        else:
            break
    return squares


"""

"""


def extractFlatSquare(flatMap):
    coordinates = findFlatSquare(flatMap)
    for zCoord in range(coordinates[0][1], coordinates[1][1]):
        for xCoord in range(coordinates[0][0], coordinates[1][0]):
            flatMap[zCoord][xCoord] = 0
    return coordinates, flatMap


"""

"""


def findFlatSquare(flatMap):
    rows = len(flatMap)
    columns = len(flatMap[0])

    square = [[0 for _ in range(columns)] for _ in range(rows)]

    for i in range(0, rows):
        for j in range(0, columns):
            if flatMap[i][j] == 1:
                square[i][j] = min(square[i][j - 1], square[i - 1][j], square[i - 1][j - 1]) + 1
            else:
                square[i][j] = 0

    max_of_s = square[0][0]
    max_i = 0
    max_j = 0

    for i in range(rows):
        for j in range(columns):
            if max_of_s < square[i][j]:
                max_of_s = square[i][j]
                max_i = i
                max_j = j

    xRange = range(max_j, max_j - max_of_s, -1)
    yRange = range(max_i, max_i - max_of_s, -1)
    return (xRange[-1], yRange[-1]), (xRange[0], yRange[0])
