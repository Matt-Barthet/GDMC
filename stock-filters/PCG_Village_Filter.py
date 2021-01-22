from pymclevel import alphaMaterials, MCSchematic, MCLevel, BoundingBox
from collections import namedtuple
from operator import mul
from itertools import permutations, repeat
import mcplatform

import numpy as np
import copy
import random
import time
import os
import matplotlib.pyplot as plt

# Local Imports (Utilities, Libraries, Agents)
import PreProcessing as PreProc
from Agent_Utility import spawn_village_entrance
from Agent_Utility import is_free
from Agent_Utility import DIRECTIONS
from Agent_Utility import change_direction
from Agent_Utility import placeBlockAt
from Agent_Utility import divideAndFloor

import AHouse_v5

"""("Agent-Based Settlement Generation", "label"),
("Minimum House Dimension", (3, 3, 20)),
("House Size Variation", (1, 1, 6)),
("House Path Length", (1, 1, 3)),
("House Density (%)", (50, 0, 100)),
("Street Lamp Density (%)", (5, 0, 100)),
("Enforce Square Houses", True),
("Maximum Street Depth Lookahead (in Houses)", (3, 1, 5)),
("Minimum Width for Street Lookahead", (3, 1, 5)),
("Creator: Matthew Barthet", "label"),"""

"""
Inputs given by the user before the filter is executed, as well as some labelling
instructions for the user.
"""
inputs = (
    ("Building Name", ("string", "value=")),
)

mapping = [0, 0, 5, 4, 17]

def convert_to_integer(lattice):
    """
    Convert material lattice from one-hot representation to integer encoding representation.

    :param lattice: lattice of one-hot material vectors.
    :return: lattice of integer material codes.
    """

    integer_reconstruct = np.zeros((20, 20, 20))
    for channel in range(20):
        for row in range(20):
            print(row)
            integer_reconstruct[channel][row] = np.argmax(lattice[channel][row], axis=1)
    return integer_reconstruct


def place_lattice_from_file(level, box, options):
    original = np.load("./stock-filters/lattices/" + options['Building Name'])
    original = original.astype(int)
    for i in range(20):
        for j in range(20):
            for k in range(20):
                level.setBlockAt(box.minx + i, box.miny + k, box.maxz - j, mapping[original[i][j][k]])


# Filter's main function which executes the functionality desired.
def perform(level, box, options):
    place_lattice_from_file(level, box, options)
    """heightMap, idMap, dataMap, dimensions = PreProc.extractHeightMap(level, box)
    edgeMap = PreProc.extractSmoothnessMap(heightMap, 1)
    squares = PreProc.extractFlatSquares(edgeMap, 1)

    global houseSizes, houseHeights, pathLength, streetSizes, houseDensity, lampDensity, minimum_street_width

    house_dimensions = (options['Minimum House Dimension'], options['Minimum House Dimension'] + options['House Size Variation'])
    houseWidths = range(house_dimensions[1], house_dimensions[0], -1)

    if options['Enforce Square Houses']:
        houseSizes = [[x, x] for x in houseWidths]
    else:
        houseSizes = [[x, y] for x in houseWidths for y in houseWidths]

    pathLength = options['House Path Length']

    minimum_street_width = options['Minimum Width for Street Lookahead']
    maximum_street_width = (house_dimensions[1] + pathLength) * 2
    minimum_street_depth = house_dimensions[0] + 2
    maximum_street_depth = (house_dimensions[0] + 3) * options['Maximum Street Depth Lookahead (in Houses)']

    streetWidths = range(maximum_street_width, minimum_street_width, -1)
    streetDepths = range(maximum_street_depth, minimum_street_depth, -1)
    streetSizes = [[x, y] for x in streetWidths for y in streetDepths]

    houseDensity = options['House Density (%)']
    lampDensity = options['Street Lamp Density (%)']

    master(level, box, squares, heightMap)"""

coverage = []
building_count = []
symmetry = []


def master(level, box, squares, heightMap):

    for currentSquare in squares:

        # number of runs - strictly for statistical purposes - do not do change this for generating content
        for i in range(1):
            
            squareSize = currentSquare[1][0] - currentSquare[0][0]
            freeMap = np.zeros((squareSize, squareSize), np.int8)

            remove_foliage(level, heightMap, currentSquare, box)
            add_border(level, heightMap, currentSquare, box, freeMap)

            agentPosition, direction = spawn_village_entrance(currentSquare, heightMap, offset=minimum_street_width + 1)
            freeMap[int(agentPosition[2]) - currentSquare[0][1]][agentPosition[0] - currentSquare[0][0]] = 0

            placeBlockAt(level, box, (agentPosition[0], agentPosition[1] + 1, agentPosition[2]), (0, 0))
            activeAgents = [BuilderAgent(freeMap, copy.copy(agentPosition), level, box, currentSquare, direction)]

            building_count.append(0)

            while len(activeAgents) > 0:
                for agent in activeAgents:
                    freeMap = agent.take_step(level, box, currentSquare, freeMap, activeAgents, heightMap)
                    if agent.active is False:
                        activeAgents.remove(agent)

            empty_tiles = 0.0
            full_tiles = 0.0

            for zCoord in range(currentSquare[0][1], currentSquare[1][1]):
                for xCoord in range(currentSquare[0][0], currentSquare[1][0]):
                    if freeMap[zCoord - currentSquare[0][1]][xCoord - currentSquare[0][0]] == 0:
                        empty_tiles += 1
                        if np.random.randint(0, 100) < 10:
                            level.setBlockAt(xCoord + box.minx, int(heightMap[zCoord][xCoord] + 1), zCoord + box.minz, 38)
                            level.setBlockDataAt(xCoord + box.minx, int(heightMap[zCoord][xCoord] + 1), zCoord + box.minz, np.random.randint(0, 8))
                    else:
                        full_tiles += 1

            plt.imshow(freeMap, cmap='gray')
            plt.show(False)

            np.fill_diagonal(freeMap, 0)  # changes original array, must be careful

            overlap = (freeMap == freeMap.T) * freeMap
            indices = np.argwhere(overlap != 0)

            symmetry.append(len(indices) / (full_tiles + empty_tiles))
            coverage.append(full_tiles / (full_tiles + empty_tiles))

        # print np.average(coverage), "\t", np.average(building_count),"\t", np.average(symmetry),"\t", np.std(coverage),"\t",  np.std(building_count),"\t",  np.std(symmetry)

def remove_foliage(level, heightMap, square, box):
    for zCoord in range(square[0][1], square[1][1]):
        for xCoord in range(square[0][0], square[1][0]):
            for yCoord in range(int(heightMap[zCoord][xCoord]) + 1, box.maxy):
                if level.blockAt(box.minx + xCoord, yCoord, box.minz + zCoord) != 8 and level.blockAt(box.minx + xCoord, yCoord, box.minz + zCoord) != 9:
                    placeBlockAt(level, box, (xCoord, yCoord, zCoord), (0, 0))
                else:
                    continue


def update_position(currentPosition, currentDirection, heightMap):
    currentPosition[0] += currentDirection[0]
    currentPosition[1] = heightMap[currentPosition[2]][currentPosition[0]]
    currentPosition[2] += currentDirection[1]
    return currentPosition


def add_border(level, heightMap, square, box, freeMap):
    border_coordinates = []

    for coord in range(square[0][1], square[1][1]):
        border_coordinates.append((square[0][0], coord))
        border_coordinates.append((square[1][0]-1, coord))

    for coord in range(square[0][0] + 1, square[1][0] - 1):
        border_coordinates.append((coord, square[0][1]))
        border_coordinates.append((coord, square[1][1]-1))

    for coordinate in border_coordinates:
        level.setBlockAt(box.minx + coordinate[0], int(heightMap[coordinate[1]][coordinate[0]]) + 1, box.minz + coordinate[1], 17)
        level.setBlockDataAt(box.minx + coordinate[0], int(heightMap[coordinate[1]][coordinate[0]]) + 1, box.minz + coordinate[1], 1)
        freeMap[int(coordinate[1]) - square[0][1]][int(coordinate[0]) - square[0][0]] = 2


def drill_upward(level, box, heightMap, coordinate):
    for yCoord in range(int(heightMap[coordinate[2]][coordinate[0]]) + 1, box.maxy):
        placeBlockAt(level, box, (coordinate[0], yCoord, coordinate[2]), (0, 0))


class BuilderAgent:

    def __init__(self, freeMap, position, level, box, square, direction_code=None):
        self.position = position
        self.pAddBuilding = houseDensity
        self.pAddLamp = lampDensity
        self.pAddStreet = 10
        self.streetLength = 0
        self.currentLength = 0
        self.active = True
        self.blockCode = 4
        self.direction_code = direction_code
        self.direction = DIRECTIONS[direction_code]
        self.choose_direction(level, box, square, freeMap, directionChanges=[0])

    # Move the agent one voxel in the direction its facing
    def take_step(self, level, box, square, freeMap, activeAgents, heightMap):

        self.end_condition(level, box, square, freeMap, activeAgents)

        # If the agent is in a valid spot, place a block and update the freeMap
        placeBlockAt(level, box, self.position, (self.blockCode, 0))
        freeMap[int(self.position[2]) - square[0][1]][int(self.position[0]) - square[0][0]] = 2

        # Attempt to place a building on other side of the position of the agent
        for newDirection in [-1, 1]:
            buildingDirectionCode = change_direction(self.direction_code, newDirection)
            buildingDirection = DIRECTIONS[buildingDirectionCode]

            if random.randint(1, 100) <= self.pAddBuilding:
                self.place_building(level, box, square, buildingDirection, freeMap, heightMap)
            if random.randint(1, 100) <= self.pAddLamp:
                self.place_lamp(level, box, square, buildingDirection, freeMap, heightMap)

        # Move the agent one position forward in the direction it's facing and increment length counter
        update_position(self.position, self.direction, heightMap)
        self.currentLength += 1

        # Return the latest copy of the freeMap to the master
        return freeMap

    def end_condition(self, level, box, square, freeMap, activeAgents):

        # Check to see if th1e agent intersects with another street, terminating if so
        if not self.is_street(square, freeMap):
            self.active = False

        # If the street length has been exhausted, return the kill signal for this agent
        if self.currentLength == self.streetLength:
            self.choose_direction(level, box, square, freeMap, activeAgents)
            self.active = False

    def is_street(self, square, freeMap):
        if freeMap[int(self.position[2]) - square[0][1]][int(self.position[0]) - square[0][0]] == 2:
            return False
        return True

    # Once the agent has reached the end of its street length, spawn new agents in different directions
    def choose_direction(self, level, box, square, freeMap, activeAgents=None, directionChanges=[0, -1, 1]):

        for directionChange in directionChanges:
            for streetWidth, streetDepth in streetSizes:

                build = False

                # Get the direction code for the street and it's direction vector 
                streetDirectionCode = change_direction(self.direction_code, directionChange)
                streetDirection = DIRECTIONS[streetDirectionCode]
                newAgentPosition = copy.copy(self.position)
                newAgentPosition[0] += streetDirection[0]
                newAgentPosition[2] += streetDirection[1]

                if not is_free(freeMap, square, int(newAgentPosition[0]), int(newAgentPosition[2])):
                    continue

                # channelList = [[-1, 1], [1], [-1]]
                channelList = [[-1, 1]]

                for channels in channelList:
                    if look_ahead(square, self.position, streetDirection, streetDepth, streetWidth, freeMap, channels):
                        build = True
                        break

                if not build:
                    continue

                if activeAgents is not None:
                    activeAgents.append(
                        BuilderAgent(freeMap, newAgentPosition, level, box, square, streetDirectionCode))
                    break
                else:
                    self.direction_code = streetDirectionCode
                    self.direction = streetDirection
                    self.streetLength = streetDepth
                    self.currentLength = 0
                    return freeMap

        return freeMap

    def place_lamp(self, level, box, square, lampDirection, freeMap, heightMap):

        if self.currentLength == 0 or self.currentLength == self.streetLength:
            return

            # Make sure the buildings being placed will not overstep the boundary of the street
        if not 1 < self.currentLength < self.streetLength - 1:
            return

        # Store a copy of the agents position and move it a number of steps in the direction of the building
        agentPosition = copy.copy(self.position)
        agentPosition[0] += lampDirection[0]
        agentPosition[2] += lampDirection[1]

        stickPosition = copy.copy(agentPosition)
        stickPosition[0] += lampDirection[0]
        stickPosition[2] += lampDirection[1]
        stickPosition[1] = heightMap[stickPosition[2]][stickPosition[0]]

        if is_free(freeMap, square, int(agentPosition[0]), int(agentPosition[2])) and is_free(freeMap, square, int(stickPosition[0]), int(stickPosition[2])):
            if freeMap[int(stickPosition[2]) - square[0][1]][int(stickPosition[0]) - square[0][0]] == 2 or freeMap[int(agentPosition[2]) - square[0][1]][int(agentPosition[0]) - square[0][0]] == 2:
                return

            freeMap[int(agentPosition[2]) - square[0][1]][int(agentPosition[0]) - square[0][0]] = 1
            freeMap[int(stickPosition[2]) - square[0][1]][int(stickPosition[0]) - square[0][0]] = 1

            for lampHeight in range(1, 4):
                placeBlockAt(level, box, (stickPosition[0], stickPosition[1] + lampHeight, stickPosition[2]), (85, 0))

            placeBlockAt(level, box, (agentPosition[0], stickPosition[1] + lampHeight, agentPosition[2]), (89, 0))

    # Place building adjacent to the position of the agent
    def place_building(self, level, box, square, buildingDirection, freeMap, heightMap):

        # Store a copy of the agents position and move it a number of steps in the direction of the building
        agentPosition = copy.copy(self.position)
        agentPosition[0] += buildingDirection[0] * pathLength
        agentPosition[1] = heightMap[self.position[2]][self.position[0]]
        agentPosition[2] += buildingDirection[1] * pathLength

        if not is_free(freeMap, square, int(agentPosition[0]), int(agentPosition[2])) or freeMap[int(agentPosition[2]) - square[0][1]][int(agentPosition[0]) - square[0][0]] == 2:
            return

        # List to store the dimensions of the building to be built
        buildingDimensions = []

        # We now attempt to find a building which fits in the given space
        for roomWidth, roomDepth in houseSizes:

            # Make sure the buildings being placed will not overstep the boundary of the street
            if not ((roomWidth / 2) < self.currentLength < self.streetLength - (roomWidth / 2)):
                continue

            # Check to see if the building will fit in the given space, setting the dimensions if so
            if look_ahead(square, agentPosition, buildingDirection, roomDepth, roomWidth, freeMap, street=False):
                buildingDimensions.append(roomWidth)
                buildingDimensions.append(roomWidth * 1.5)
                buildingDimensions.append(roomDepth)
                break

        # If no dimensions are found, the search has failed and so no building shall be placed
        if len(buildingDimensions) == 0:
            return False

        buildingCenter = []
        boxDimensions = copy.copy(buildingDimensions)

        if buildingDimensions[0] % 2 != 0:
            widthCut = 2
        else:
            widthCut = 1

        if buildingDirection[0] == 1:
            buildingCenter = [agentPosition[0] + 1, agentPosition[1] + 1, agentPosition[2] - divideAndFloor(buildingDimensions[2], 2) + 1]
            boxDimensions[2] -= widthCut

        elif buildingDirection[0] == -1:
            buildingCenter = [agentPosition[0] - (buildingDimensions[0]), agentPosition[1] + 1, agentPosition[2] - divideAndFloor(buildingDimensions[2], 2) + 1]
            boxDimensions[2] -= widthCut

        elif buildingDirection[1] == 1:
            buildingCenter = [agentPosition[0] - divideAndFloor(buildingDimensions[0], 2) + 1, agentPosition[1] + 1, agentPosition[2] + 1]
            boxDimensions[0] -= widthCut

        elif buildingDirection[1] == -1:
            buildingCenter = [agentPosition[0] - divideAndFloor(buildingDimensions[0], 2) + 1, agentPosition[1] + 1, agentPosition[2] - buildingDimensions[2]]
            boxDimensions[0] -= widthCut

        buildingCenter[0] += box.minx
        buildingCenter[2] += box.minz
        newBox = BoundingBox(buildingCenter, (boxDimensions[0], buildingDimensions[1], boxDimensions[2]))
        #AHouse_v5.ahouse(level, newBox, {"Operation": "House", "Seed:": 0})
        building_count[-1] += 1

        # Now that we have a building that fits in the given space, we start by constructing a path
        for pathStep in range(1, pathLength + 4):
            xStep = int(self.position[0] + buildingDirection[0] * pathStep)
            yStep = int(self.position[2] + buildingDirection[1] * pathStep)
            placeBlockAt(level, box, (xStep, heightMap[yStep][xStep], yStep), (4, 0))
            freeMap[yStep - square[0][1]][xStep - square[0][0]] = 1

        agentPosition[1] = heightMap[self.position[2]][self.position[0]]

        for step in range(0, buildingDimensions[2]):

            agentPosition[0] += buildingDirection[0]
            agentPosition[2] += buildingDirection[1]

            for lateralStep in range(0, buildingDimensions[0] / 2):

                if buildingDirection[0] == 0:
                    lateralDirection = np.array([1, 0]) * lateralStep
                else:
                    lateralDirection = np.array([0, 1]) * lateralStep

                for i in [-1, 1]:
                    lateralPosition = [agentPosition[0] + lateralDirection[0] * i, agentPosition[2] + lateralDirection[1] * i]
                    if lateralStep < buildingDimensions[0] / 2 and step < buildingDimensions[2]:
                        freeMap[int(lateralPosition[1]) - square[0][1]][int(lateralPosition[0]) - square[0][0]] = 1

        return True


def look_ahead(square, position, direction, lookDepth, lookWidth, freeMap, channels=[-1, 1],
               street=True):

    # Store a copy of the agent position for the lookahead
    agentPosition = copy.copy(position)

    for step in range(0, lookDepth):

        # Move one position forward in the direction of the potential street
        agentPosition[0] += direction[0]
        agentPosition[2] += direction[1]

        # If an existing object is found, this space is not available
        if not is_free(freeMap, square, int(agentPosition[0]), int(agentPosition[2])):
            return False

        # If an existing street is found, return true to join the the original street with this one
        if freeMap[int(agentPosition[2]) - square[0][1]][int(agentPosition[0]) - square[0][0]] == 2:
            if not street:
                return False

        # Perform steps in either perpendicular direction and check if the positions are free, acting accordingly
        for lateralStep in range(1, divideAndFloor(lookWidth, 2) + 1):
            if direction[0] == 0:
                lateralDirection = np.array([1, 0]) * lateralStep
            else:
                lateralDirection = np.array([0, 1]) * lateralStep
            for distance in channels:
                lateralPosition = [agentPosition[0] + lateralDirection[0] * distance, agentPosition[2] + lateralDirection[1] * distance]
                if not is_free(freeMap, square, int(lateralPosition[0]), int(lateralPosition[1])):
                    return False
                if freeMap[int(lateralPosition[1]) - square[0][1]][int(lateralPosition[0]) - square[0][0]] == 2:
                    return False

    # If placing a building we can stop here
    if not street:
        return True

    # Now we "book" the space for this street - set the freeMap value to 1 so that other agents ignore the space
    agentPosition = copy.copy(position)
    for _ in range(0, lookDepth):
        freeMap[agentPosition[2] - square[0][1]][agentPosition[0] - square[0][0]] = 1
        agentPosition[0] += direction[0]
        agentPosition[2] += direction[1]
        return True
