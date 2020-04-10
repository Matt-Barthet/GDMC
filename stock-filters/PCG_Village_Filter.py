from pymclevel import alphaMaterials, MCSchematic, MCLevel, BoundingBox
from collections import namedtuple
from operator import mul
from itertools import permutations, repeat
import mcplatform
import random
import matplotlib.pyplot as plt
import numpy as np
import utility

"""
Inputs given by the user before the filter is executed, as well as some labelling
instructions for the user.
"""
inputs = (
	("Procedurally Generated Settlement Filter", "label"),
	("Creator: Matthew Barthet", "label"),
	)

#Block ID's which are not solid, cannot be walked on.
NONSURFACE = [0,6,8,9,17,18,31,32,37,38,39,40,50,51,59,63,75,76,78,81,82,83,86,92,99,100,103,104,105,106,111,115,127,140,141,142,161,162,166,175,176,177,199,200,207,255]

roomDimensions = (3, 5)
roomWidths = range(roomDimensions[1], roomDimensions[0], -1)
roomDepths = range(roomDimensions[1], roomDimensions[0], -1)
roomSizes = [[x,y] for x in roomWidths for y in roomDepths]

corridorLengths = range(8, 3, -1)
directions = [[-1, 0], [1, 0], [0, 1], [0, -1]]
corridorPossibilities = [[x,y] for x in directions for y in corridorLengths]

"""
Filter's main function which executes the functionality desired.
"""
def perform(level, box, options):
	heightMap, idMap, dataMap, dimensions = extractHeightMap(level, box, options)
	edgeMap = extractSmoothnessMap(heightMap, 1)
	squares = extractFlatSquares(level, edgeMap, 1, heightMap, box)
	lookAheadDiggingAgent(level, box, squares, heightMap)
	utility.log(str(dimensions) + ", Done")

def ruleBasedDigger(level, box, squares, heightMap):
	for currentSquare in squares:
		agentPosition = utility.randomCoordinate(currentSquare)
		agentPosition.append(heightMap[agentPosition[1]][agentPosition[0]] + 10)
		squareSize = currentSquare[1][0] - currentSquare[0][0] 

def spawnDigger(level, box, square, heightMap, freeMap):
	while(True):
		agentPosition = utility.generateCoordinate(square)
		agentPosition.append(heightMap[agentPosition[1]][agentPosition[0]] + 10)
		if attemptRoomSpawn(level, box, square, agentPosition, freeMap):
			break
	return agentPosition

def attemptRoomSpawn(level, box, currentSquare, agentPosition, freeMap):
	for (roomWidth, roomDepth) in random.sample(roomSizes, len(roomSizes)):
		yRange = range(agentPosition[1] - utility.divideAndFloor(roomDepth, 2), agentPosition[1] + utility.divideAndCeil(roomDepth, 2))
		xRange = range(agentPosition[0] - utility.divideAndFloor(roomWidth, 2), agentPosition[0] + utility.divideAndCeil(roomWidth, 2))
		if utility.attemptPlacement(currentSquare, (xRange, yRange), freeMap):
			freeMapRoom = utility.placeObject(level, box, currentSquare, (xRange, yRange), agentPosition, freeMap)
			fRoom = 1
			return True
	return False

def lookAheadDiggingAgent(level, box, squares, heightMap):

	for currentSquare in squares:
		squareSize = currentSquare[1][0] - currentSquare[0][0] 
		freeMap = np.zeros((squareSize, squareSize), np.int8)
		agentPosition = spawnDigger(level, box, currentSquare, heightMap, freeMap)
		while(True):
			fRoom = False
			fCorridor = False

			freeMapRoom = np.zeros((squareSize, squareSize), np.int8)

			fRoom = attemptRoomSpawn(level, box, currentSquare, agentPosition, freeMapRoom)
			
			for direction, corridorLength in random.sample(corridorPossibilities, len(corridorPossibilities)):
				corridorDimensions = [direction[0] * corridorLength, direction[1] * corridorLength]
				if corridorDimensions[0] == 0:
					corridorDimensions[0] = 1
				elif corridorDimensions[1] == 0:
					corridorDimensions[1] = 1

				directions = [1, 1]
				if(corridorDimensions[0] < 0):
					directions[0] = -1
				if(corridorDimensions[1] < 0):
					directions[1] = -1

				yRange = range(agentPosition[1], agentPosition[1] + corridorDimensions[1], directions[1])
				xRange = range(agentPosition[0], agentPosition[0] + corridorDimensions[0], directions[0])
					
				if utility.attemptPlacement(currentSquare, (xRange, yRange), freeMap):
					utility.placeObject(level, box, currentSquare, (xRange, yRange), agentPosition)
					fCorridor = True
					agentPosition[0] += direction[0] * corridorLength
					agentPosition[1] += direction[1] * corridorLength
					break

			freeMap = freeMapRoom.copy()
			if not(fRoom or fCorridor):
				break

def randomDiggingAgent(level, box, squares, heightMap):

	pDirectionChange = 5
	pAddRoom = 5
	agentPosition = utility.randomCoordinate(squares[0])
	agentPosition.append(heightMap[agentPosition[1]][agentPosition[0]] + 15)
	agentDirection = directions[random.randint(0, len(directions))]

	for i in range(0,100):
		if(utility.validCoordinate(squares[0], agentPosition)):
			utility.placeBlockAt(level, box, (agentPosition[0], agentPosition[2], agentPosition[1]), (4,0))
			
		if(utility.validCoordinate(squares[0], agentPosition + agentDirection)):
			agentPosition[0] += agentDirection[0]
			agentPosition[1] += agentDirection[1]
		else:
			agentDirection[0] = -agentDirection[0]
			agentDirection[0] = -agentDirection[1]
			pDirectionChange = 0

		if random.randint(0, 100) < pDirectionChange:
			agentDirection = directions[random.randint(0, len(directions))]
			pDirectionChange = 0
		else:
			pDirectionChange += 5

		if random.randint(0, 100) < pAddRoom:
			newRoom = [random.randint(3, 7), random.randint(3,7)]
			print newRoom
			for yCoord in range(agentPosition[1] - newRoom[1] / 2, agentPosition[1] + newRoom[1] / 2):
				for xCoord in range(agentPosition[0] - newRoom[0] / 2, agentPosition[0] + newRoom[0] / 2):
					utility.placeBlockAt(level, box, (xCoord, agentPosition[2], yCoord), (4,0))
			pAddRoom = 0
		else:
			pAddRoom += 5

"""
Function which takes the edge map and identifies flat rectangular regions which can be used
to build structures with the contructive agents further down the line.
"""
def extractFlatSquares(level, edgeMap, maxRoughness, heightMap, box):
	squares = []
	flatMap = np.zeros(edgeMap.shape, int) 
	for yCoord in range(0, edgeMap.shape[0]):
		for xCoord in range (0, edgeMap.shape[1]):
			if flatMap[yCoord][xCoord] == 0:
				if edgeMap[yCoord][xCoord] < maxRoughness:
					flatMap[yCoord][xCoord] = 1

	for repeat in range(0,3):
		square, flatMap = extractFlatSquare(level, box, flatMap, heightMap)
		squares.append(square)
	return squares

def extractFlatSquare(level, box, flatMap, heightMap):
	coordinates = findFlatSquare(flatMap)
	max_height = heightMap[coordinates[0][1]][coordinates[0][0]] + 10

	for zCoord in range (coordinates[0][1], coordinates[1][1]):
		for xCoord in range (coordinates[0][0], coordinates[1][0]):
			flatMap[zCoord][xCoord] = 0
			yCoord = heightMap[zCoord][xCoord]
			while yCoord < max_height:
				utility.placeBlockAt(level, box, (xCoord, yCoord, zCoord), (4, 0))
				yCoord+=1
	return coordinates, flatMap

"""
Analyse the chunk given and extract a 2D height map representation of the terrain.
for later use.
"""
def extractHeightMap(level, box, options):
	heightMap = []
	idMap = []
	dataMap = []

	(x1,y1,z1) = (box.minx, box.miny, box.minz)
	(x2,y2,z2) = (box.maxx, box.maxy, box.maxz)

	regionWidth = x2-x1
	regionDepth = z2-z1
	regionHeight = 0

	heightMap = np.zeros((regionDepth,regionWidth))
	idMap = np.zeros((regionDepth,regionWidth))
	dataMap = np.zeros((regionDepth,regionWidth))

	#Loop through the Z-Coordinate Space
	for zCoord in np.arange(z1, z2):
		column = []

		#Loop through the X-Coordinate Space
		for xCoord in np.arange(x1, x2):
			(voxel, voxelData) = (-1,1)
			voxelHeight = -1
			yCoord = box.maxy

			#Loop downward from the top of the Y-Coordinate space until the bottom
			while yCoord >= y1:
				yCoord -= 1
				voxel = level.blockAt(xCoord, yCoord, zCoord)

				#If a non-empty voxel is found, store the height of the coordinate
				if voxel not in NONSURFACE:
					dataMap[zCoord - z1][xCoord - x1] = level.blockDataAt(xCoord, yCoord, zCoord)
					heightMap[zCoord - z1][xCoord - x1] = yCoord
					idMap[zCoord - z1][xCoord - x1] = voxel
					if yCoord > regionHeight:
						regionHeight = yCoord
					break

	return (heightMap, idMap, dataMap, (regionWidth, regionDepth, regionHeight))

"""
Take the heightmap and compute the differences in heights between neigbouring tiles
to construct the edgemap.  Sensitivity defines how many neighbouring tiles affect
affect the edgemap entries.
"""
def extractSmoothnessMap(heightMap, sensitivity):
	(width,depth) = heightMap.shape
	smoothnessMap = np.zeros((width,depth))
	for yCoord in range(0, width):
		for xCoord in range(0, depth):
			count = 0
			neighbourDeltas = 0
			referenceTile = heightMap[yCoord][xCoord]

			for yOffset in range(-sensitivity, sensitivity + 1):
				for xOffset in range(-sensitivity, sensitivity + 1):
					if not (xOffset == 0 and yOffset == 0):
						if (yCoord + yOffset >= 0 and yCoord + yOffset < width) and (xCoord + xOffset >= 0 and xCoord + xOffset < depth):
							neighbourTile = heightMap[yCoord + yOffset][xCoord + xOffset]
							neighbourDeltas += abs(referenceTile - neighbourTile)
							count += 1
			smoothnessMap[yCoord][xCoord] = round(neighbourDeltas / count, 1)	
	return smoothnessMap		

def findFlatSquare(flatMap):
	rows = len(flatMap)
	columns = len(flatMap[0]) 

	square = [[0 for k in range(columns)] for l in range(rows)]

	for i in range(0, rows):
		for j in range(0, columns):
			if (flatMap[i][j] == 1):
				square[i][j] = min(square[i][j-1], square[i-1][j], square[i-1][j-1]) + 1
			else:
				square[i][j] = 0

	max_of_s = square[0][0]
	max_i = 0
	max_j = 0

	for i in range(rows):
		for j in range(columns):
			if (max_of_s < square[i][j]):
				max_of_s = square[i][j]
				max_i = i
				max_j = j

	xRange = range(max_j, max_j - max_of_s, -1)
	yRange = range(max_i, max_i - max_of_s, -1)
	return ((xRange[-1], yRange[-1]), (xRange[0], yRange[0]))