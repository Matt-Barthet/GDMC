# -*- coding: utf-8 -*-
"""
Created on Mon Jun 29 11:14:12 2020

@author: Manos
"""

import random
import numpy 

displayName = "Random facade"


def perform(level, box, options):
    block = 5
    data = 0

    xx = (box.maxx - box.minx) 
    zz = (box.maxz - box.minz)
    yy = (box.maxy - box.miny)

    #3D matrix to store level blocks 
    selectionMatrix = numpy.zeros((xx, zz, yy))
    
    for i in range(0, selectionMatrix.shape[0]):
        for j in range(0, selectionMatrix.shape[1]):
            for k in range(0, selectionMatrix.shape[2]):
                # inner section
                selectionMatrix[i][j][k] = random.randint(0, 1)
                # build frame
                if i == 0 or i == selectionMatrix.shape[0]-1 or k == 0 or k == selectionMatrix.shape[2]-1:
                    selectionMatrix[i][j][k] = 1
    
    # search within frame for floating blocks with no neighbours vert and hor
    for i in range(1, selectionMatrix.shape[0]-1):
        for k in range(1, selectionMatrix.shape[2]-1):
            if selectionMatrix[i][0][k] == 1:
                if not (selectionMatrix[i-1][0][k] == 1 or selectionMatrix[i+1][0][k] == 1 or selectionMatrix[i][0][k-1] == 1 or selectionMatrix[i][0][k+1] == 1):
                    selectionMatrix[i][0][k] = 2

    selectionMatrix = selectionMatrix.astype(numpy.uint16)
    
    # generate block according to selection matrix
    for x in xrange(box.minx, box.maxx):
        for z in xrange(box.minz, box.maxz):
            for y in xrange(box.miny, box.maxy):
                if selectionMatrix[abs(box.maxx-x-xx)][abs(box.maxz-z-zz)][abs(box.maxy-y-yy)] == 1:
                    block = 5
                elif selectionMatrix[abs(box.maxx-x-xx)][abs(box.maxz-z-zz)][abs(box.maxy-y-yy)] == 2:
                    block = 4
                else:
                    block = 0
                level.setBlockAt(x, y, z, block)
                level.setBlockDataAt(x, y, z, data)
    
#    print(selectionMatrix.shape[0])
#    print(selectionMatrix.shape[1])
#    print(selectionMatrix.shape[2])
#    
#    print(str(box.minx) + " " + str(box.maxx))
#    print(str(box.miny) + " " + str(box.maxy))
#    print(str(box.minz) + " " + str(box.maxz))
    
    
                   