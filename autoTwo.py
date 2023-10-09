from vmtk import pypes
import os
import numpy as np


#Getting Target and Source Points From vmtknetworkextraction For Centerline Calculations
def getSource(val: int, savePath: str):
    file = open(savePath + 'centerPre/centerPre' + str(val) + '.dat')
    lst = []
    lstTotal = None
    
    for line in file:
        lst += [line.split()]
    if len(lst) > 2:
        if lst[2][3] == 0:
            lstTotal = len(lst)-2
            xTarg = lst[3][0]
            yTarg = lst[3][1]
            zTarg = lst[3][2]
        else:
            lstTotal = len(lst)-2
            xTarg = lst[2][0]
            yTarg = lst[2][1]
            zTarg = lst[2][2]

        xSource = lst[lstTotal][0]
        ySource = lst[lstTotal][1]
        zSource = lst[lstTotal][2]
    else:
        xTarg = '1'
        yTarg = '1'
        zTarg = '1'
        
        xSource = '1'
        ySource = '1'
        zSource = '1'

    targs = [xTarg,yTarg,zTarg]
    source = [xSource,ySource,zSource]

    return targs,source

    
#VMTK Scripts for Getting Aorta Geometry
def getDims(pathToCT: str, tempPath: str, val: int, savePath: str):
    
    pypes.PypeRun('vmtkimagereader -ifile ' + pathToCT + ' -origin 0.0 0.0 0.0 --pipe vmtkimagewriter -ofile ' + tempPath + 'aorta-label.vti')
    #For multilabel add -upperthreshold and make both that and -lowerthreshold 52.0
    pypes.PypeRun('vmtkimageinitialization -ifile ' + tempPath + 'aorta-label.vti -interactive 0 -method threshold -lowerthreshold 1.0 --pipe vmtklevelsetsegmentation -ifile ' + tempPath + 'aorta-label.vti -iterations 300 -ofile ' + tempPath + 'testing.vti')
    pypes.PypeRun('vmtkmarchingcubes -ifile ' + tempPath + 'testing.vti -ofile ' + tempPath + 'mcSurf.vtp --pipe')
    pypes.PypeRun('vmtksurfacesmoothing -ifile ' + tempPath + 'mcSurf.vtp -passband 0.005 -iterations 30 -ofile ' + savePath + 'smoothedModel/smModel' + str(val) + '.vtp --pipe')
    pypes.PypeRun('vmtknetworkextraction -ifile ' + savePath + 'smoothedModel/smModel' + str(val) + '.vtp -advancementratio 1.10 -ofile ' + tempPath + 'centerPre.vtp')
    pypes.PypeRun('vmtksurfacewriter -ifile ' + tempPath + 'centerPre.vtp -ofile ' + savePath + 'centerPre/centerPre' + str(val) + '.dat')

    targs,sources = getSource(val, savePath)

    source = sources[0] + ' ' + sources[1] + ' ' + sources[2]
    target = targs[0] + ' ' + targs[1] + ' ' + targs[2]


    pypes.PypeRun('vmtksurfacereader -ifile ' + savePath + 'smoothedModel/smModel' + str(val) + '.vtp --pipe vmtkcenterlines -seedselector pointlist -sourcepoints ' + source + ' -targetpoints ' + target + ' -ofile ' + tempPath + 'center.vtp')
    pypes.PypeRun('vmtksurfacereader -ifile ' + savePath + 'smoothedModel/smModel' + str(val) + '.vtp --pipe vmtkdistancetocenterlines -centerlinesfile ' + tempPath + 'center.vtp -ofile ' + tempPath + 'centerDist.vtp')   
    pypes.PypeRun('vmtkcenterlinegeometry -ifile ' + tempPath + 'center.vtp -ofile ' + savePath + 'geomRaw/geomRaw' + str(val) + '.vtp')
    pypes.PypeRun('vmtksurfacewriter -ifile ' + savePath + 'geomRaw/geomRaw' + str(val) + '.vtp -ofile ' + savePath + 'geomData/geomData' + str(val) + '.dat')
    pypes.PypeRun('vmtksurfacewriter -ifile ' + tempPath + 'centerDist.vtp -ofile ' + savePath + 'centerDist/centerDist' + str(val) + '.dat')
    pypes.PypeRun('vmtksurfacewriter -ifile ' + tempPath + 'center.vtp -ofile ' + savePath + 'centerLines/center' + str(val) + '.vtp')

################################################################

#File Path to Where Labels Are Stores
base = '/mnt/e/aorta/chest/without_contrast/'
os.chdir(base)

files = os.listdir()

tempFilePath = '/mnt/e/tempFiles/'
savePath = '/mnt/e/CenterlinesAndRadiusTest/'


#Generating Necessary File Paths
if os.path.isdir(tempFilePath) == False:
    os.makedirs(tempFilePath)
    
if os.path.isdir(savePath) == False:
    os.makedirs(savePath)
    os.makedirs(savePath + 'centerDist')
    os.makedirs(savePath + 'centerLines')
    os.makedirs(savePath + 'centerPre')
    os.makedirs(savePath + 'geomData')
    os.makedirs(savePath + 'geomRaw')
    os.makedirs(savePath + 'smoothedModel')

for i in range(20,22):
    os.chdir(base + files[i])
    tempBase = base + files[i] + '/' + os.listdir()[0] + '/aorta.seg.nrrd' 
    getDims(tempBase,tempFilePath,i+100,savePath)

    

