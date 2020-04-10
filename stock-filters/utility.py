import random
import math
import time

"""
Object Creation Utilities
"""
def generateCoordinate(square):
	cursor = [0,0]
	cursor[0] = random.randint(square[0][0]+1, square[1][0])
	cursor[1] = random.randint(square[0][1]+1, square[1][1])
	return cursor

def placeObject(level, box, square, ranges, agentPosition, freeMap = None):
	if freeMap is not None:
		freeMapRoom = freeMap.copy()
	for yCoord in ranges[1]:
		for xCoord in ranges[0]:
			placeBlockAt(level, box, (xCoord, agentPosition[2], yCoord), (2,0))
			if freeMap is not None:
				freeMapRoom[yCoord - square[0][1]][xCoord - square[0][0]] = 1
	if freeMap is not None:
		return freeMapRoom

def placeBlockAt(level, box, coordinates, block):
	level.setBlockAt((int)(box.minx + coordinates[0]),(int)(coordinates[1]),(int)(box.minz + coordinates[2]), block[0])
	level.setBlockDataAt((int)(box.minx + coordinates[0]),(int)(coordinates[1]),(int)(box.minz + coordinates[2]), block[1])

"""
Conditional Utilities
"""
def attemptPlacement(square, ranges, freeMap):
	for yCoord in ranges[1]:
		for xCoord in ranges[0]:
			if not validCoordinate(square, (xCoord, yCoord)):
				return False
			if freeMap[yCoord - square[0][1]][xCoord - square[0][0]] == 1:
				return False
	return True

def validCoordinate(square, coordinate):
	return coordinate[0] >= square[0][0] and coordinate[0] < square[1][0] and coordinate[1] >= square[0][1] and coordinate[1] < square[1][1]

"""
Arithmetic Utilities
"""
def divideAndFloor(numerator, denomenator):
	return int(math.floor(numerator/denomenator))

def divideAndCeil(numerator,denomenator):
	return int(math.ceil(float(numerator)/float(denomenator)))

"""
Output Utilities
"""
def printMap(map, type):
	print("\n" + type + " Map:")
	for yCoord in range(0, len(map)):
		line = ""
		for xCoord in range(0, len(map[0])):
			line+=(str(map[yCoord][xCoord]) + "\t")
		print(line)	

def log(message):
	print ("PCG_Village_Filter",time.ctime(),message)

