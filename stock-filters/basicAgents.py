import copy
import numpy as np
import utility
import random
from utility import DIRECTIONS
from utility import ChangeDirection

"""

"""
def constructiveRuleBasedDigger(level, box, squares, heightMap):

	#Establish the movement properties and starting direction of the agent
	forwardProbability = 90
	leftTurn = 98
	rightTurn = 100
	revisitTile = 50

	for currentSquare in squares:
		terminate = False
		squareSize = currentSquare[1][0] - currentSquare[0][0] 
		freeMap = np.zeros((squareSize, squareSize), np.int8)
		freeMapUpdate = np.zeros((squareSize, squareSize), np.int8)
		agentPosition = utility.spawnDiggerCenter(currentSquare, heightMap)

		utility.placeBlockAt(level, box, (agentPosition[0], agentPosition[2] - 1, agentPosition[1]), (2,0))

		directionCode = random.randint(0,3)
		direction = DIRECTIONS[directionCode]
		newPosition = []

		while(True):
    			
			diceRoll = random.randint(1,110)
			newPosition = agentPosition

			if diceRoll >= rightTurn:
				newPosition[0] += direction[0] * 3
				newPosition[1] += direction[1] * 3

				"""				
				try:
					newPosition[2] = heightMap[newPosition[1]][newPosition[0]] + 1
				except:
					pass
				"""

				if utility.validCoordinate(currentSquare, newPosition):
					if utility.attemptRoomSpawn(level, box, currentSquare, newPosition, freeMapUpdate):
						agentPosition = newPosition

			else:	

				if diceRoll < forwardProbability:
						pass
				elif diceRoll < leftTurn:
					directionCode = ChangeDirection(directionCode, -1)
				elif diceRoll < rightTurn:
					directionCode = ChangeDirection(directionCode, 1)

				newPosition[0] += direction[0]
				newPosition[1] += direction[1]

				if not utility.validCoordinate(currentSquare, newPosition):
					validPath = False
					for i in range(0,4):
						directionCode = ChangeDirection(directionCode, -1)
						direction = DIRECTIONS[directionCode]
						newPosition[0] = agentPosition[0] + direction[0]
						newPosition[1] = agentPosition[1] + direction[1]

						if utility.validCoordinate(currentSquare, newPosition):
							validPath = True
							break
						else:
							utility.placeBlockAt(level, box, (newPosition[0], newPosition[2] - 1, newPosition[1]), (8,0))	

					if not validPath:
						print("No valid path found")
						break

				agentPosition = newPosition
				utility.placeBlockAt(level, box, (agentPosition[0], agentPosition[2] - 1, agentPosition[1]), (2,0))

			direction = DIRECTIONS[directionCode]
			freeMap = freeMapUpdate.copy()
		
"""

"""
def lookAheadDiggingAgent(level, box, squares, heightMap):
	for currentSquare in squares:
		squareSize = currentSquare[1][0] - currentSquare[0][0] 
		freeMap = np.zeros((squareSize, squareSize), np.int8)
		freeMapUpdate = np.zeros((squareSize, squareSize), np.int8)
		agentPosition = utility.spawnDiggerRandom(level, box, currentSquare, heightMap, freeMap)

		while(True):
			fRoom = False
			fCorridor = False
			fRoom = utility.attemptRoomSpawn(level, box, currentSquare, agentPosition, freeMapUpdate)
			fCorridor = utility.attemptCorridorSpawn(level, box, currentSquare, agentPosition, freeMap)
			freeMap = freeMapUpdate.copy()
			if not(fRoom or fCorridor):
				break

"""
Agent which choose the next direction to place a block randomly. Also rolls to check whether a building should
be placed in the current location.
"""
def randomDiggingAgent(level, box, squares, heightMap):
	directions = [[-1, 0], [1, 0], [0, 1], [0, -1]]
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
			for yCoord in range(agentPosition[1] - newRoom[1] / 2, agentPosition[1] + newRoom[1] / 2):
				for xCoord in range(agentPosition[0] - newRoom[0] / 2, agentPosition[0] + newRoom[0] / 2):
					utility.placeBlockAt(level, box, (xCoord, agentPosition[2], yCoord), (4,0))
			pAddRoom = 0
		else:
			pAddRoom += 5