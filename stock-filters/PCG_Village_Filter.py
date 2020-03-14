import time 
from random import *
from numpy import *
from pymclevel import alphaMaterials, MCSchematic, MCLevel, BoundingBox
from mcplatform import *
import numpy as np

"""
Inputs given by the user before the filter is executed, as well as some labelling
instructions for the user.
"""
inputs = (
	("Procedurally Generated Settlement Filter", "label"),
	("Creator: Matthew Barthet", "label"),
	)

def perform(level, box, options):
	heightMap = extractHeightMap(level, box, options)
	printHeightMap(heightMap)
	printEdgeMap(heightMap, extractEdgeMap(heightMap))

def extractEdgeMap(heightMap):
	horizontalEdges = []
	verticalEdges = []

	for yCoord in range(0, len(heightMap) + 1):
		column = []
		for xCoord in range(0, len(heightMap[0])):
			column.append("__")
		verticalEdges.append(column)

	for yCoord in range(0, len(heightMap)):
		column = []
		for xCoord in range(0, len(heightMap[0]) + 1):
			column.append("||")
		horizontalEdges.append(column)

	return (horizontalEdges, verticalEdges)

"""
Analyse the chunk given and extract a 2D height map representation of the terrain
for later use.
"""
def extractHeightMap(level, box, options):
	heightMap = []

	#Loop through the Z-Coordinate Space
	for zCoord in np.arange(box.minz, box.maxz):
		column = []

		#Loop through the X-Coordinate Space
		for xCoord in np.arange(box.minx, box.maxx):
			(voxel, voxelData) = (-1,1)
			voxelHeight = -1
			yCoord = box.maxy

			#Loop downward from the top of the Y-Coordinate space until the bottom
			while yCoord >= box.miny:
				yCoord -= 1
				voxel = level.blockAt(xCoord, yCoord, zCoord)

				#If a non-empty voxel is found, store the height of the coordinate
				if voxel != 0:
					voxelData = level.blockDataAt(xCoord, yCoord, zCoord)
					voxelHeight = yCoord
					break

			column.append((voxelHeight, False, (voxel, voxelData)))

		heightMap.append(column)

	return heightMap

"""
Given a heightmap and associated edgemap, use the console to print out a diagram for debugging purposes.
"""
def printEdgeMap(heightMap, edgeMap):
	print("\nEdgeMap: \n")

	horizontalEdges = edgeMap[0]
	verticalEdges = edgeMap[1]

	edgeMap = ""
	for yCoord in range(0, len(heightMap)):

		for xCoord in range(0, len(verticalEdges[0])):
			edgeMap += "\t" + verticalEdges[yCoord][xCoord] +"\t"
		edgeMap += "\n\n"
		
		for xCoord in range(0, len(horizontalEdges[0])-1):
			if xCoord == 0:
				edgeMap += horizontalEdges[yCoord][xCoord] + "\t"
				edgeMap += str(heightMap[yCoord][xCoord][0])
				edgeMap += "\t" +  horizontalEdges[yCoord][xCoord] + "\t"
			else:
				edgeMap += str(heightMap[yCoord][xCoord][0])
				edgeMap += "\t" +  horizontalEdges[yCoord][xCoord] + "\t"
				
		edgeMap +="\n"

	for xCoord in range(0, len(verticalEdges[-1])):
		edgeMap += "\t" + verticalEdges[-1][xCoord] +"\t"

	print(edgeMap)

"""
Given a heightmap, use the console to print out a diagram for debugging purposes.
"""
def printHeightMap(heightMap):
	print("\nHeightMap: \n")
	for xCoord in range(0, len(heightMap)):
		line = ""
		for yCoord in range(0, len(heightMap[0])):
			line+=(str(heightMap[xCoord][yCoord][0]) + "\t")
		print(line)	

	