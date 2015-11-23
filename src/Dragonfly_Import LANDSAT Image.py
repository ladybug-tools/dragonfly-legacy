# Import a LANDSAT Image File to Grasshopper
#
# Dragonfly: A Plugin for Environmental Analysis (GPL) started by Chris Mackey
# 
# This file is part of Dragonfly.
# 
# Copyright (c) 2015, Chris Mackey <Chris@MackeyArchitecture.com> 
# Dragonfly is free software; you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published 
# by the Free Software Foundation; either version 3 of the License, 
# or (at your option) any later version. 
# 
# Dragonfly is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Use this component to import a LADNSAT image that has been downloaded from GloVis into Grassoppper.  LANDSAT images contain a wide variety of data at a resolution of 30 meters x 30 meters per pixel.  This data includes:
    1) Earth Surface Temperature
    2) "True Color" Images of the Earth (using RGB channels)
    3) Surface Solar Reflectivity
    4) Vegetation Index (NDVI)
    5) Radiance at 6 Different Portions of the Electromagnetic Spectrum
-
Provided by Dragonfly 0.0.01
    Args:
        _landsatImgFolder: The file path to the folder on your computer into which the LANDSAT image has been decompressed.
        latitude_: A number representing the latitude at which you would like to center the LANDSAT image imported to the Rhino scene.  It is helpful to take the latitudefrom the location of an EPW file imported with Ladybug or from a site that you have looked up in Google.  If no value is input here, the latitude will be set to the center of the image.
        longitude_: A number representing the longitude at which you would like to center the LANDSAT image imported to the Rhino scene.  It is helpful to take the longitude from the location of an EPW file imported with Ladybug or from a site that you have looked up in Google.  If no value is input here, the longitude will be set to the center of the image.
        imageWidth_: A number representing the width of the portion of the LANDSAT image that you would like to import in meters.  If no value is input here, the default will be set to 2 kilometers (2000 meters).
        imageHeight_: A number representing the height of the portion of the LANDSAT image that you would like to import in meters.  If no value is input here, the default will be set to 2 kilometers (2000 meters).
        sampleSize_: An integer representing the number of pixels to skip with each sampling.  Set this to a high number like 32 to allow the component to run quickly and zoom out to the entire LANDSAT image scene.  If no value is input here, every single pixel within the given latitude, longitude imageHeight and imageWidth will be sampled, assuming a sample size of 1.
        legendPar_: Optional legend parameters from the 'Ladybug Legend Parameters' component.
        _runIt: Set to 'True' to run the component and import the LANDSAT image.
    Returns:
        readMe!: ...
        temperatures: Temperature values for for each of the imported pixels in degrees Celcius.
        geoTiffPts: A list of points with one point for each pixel imported from the LANDSAT image.  Connect this to the 'G' of a native grasshopper 'Custom Preview' component to preview the points colored with the imported values.
        ptColors: A list of colors one color for each pixel imported from the LANDSAT image.  Connect this to the 'S' of a native grasshopper 'Custom Preview' component to preview the points colored with the imported values.
        ---------------: ...
        imageMesh: A mesh of the imported LANDSAT image.  Connect this output to a grasshopper "Geo" component in order to preview the legend separately in the Rhino scene.
        legend: A legend for the imported LANDSAT image.
        legendBasePt: The legend base point, which can be used to move the legend in relation to the imported LANDSAT image with the native rasshopper "Move" component.
        title: The title text of the LANDSAT image.  Hook this up to a native Grasshopper 'Geo' component to preview it separately from the other outputs.
        titleBasePt: Point for the placement of the title, which can be used to move the title in relation to the LANDSAT imag with the native Grasshopper "Move" component.
"""

ghenv.Component.Name = "Dragonfly_Import LANDSAT Image"
ghenv.Component.NickName = 'ImportLANDSATImg'
ghenv.Component.Message = 'VER 0.0.01\nNOV_22_2015'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "1 | VisualizeSatelliteData"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import os
from clr import AddReference
AddReference('Grasshopper')
AddReference('System.Drawing')
from System.Drawing import Image

import Rhino as rc
import Grasshopper.Kernel as gh
import math
import scriptcontext as sc


def checkTheInputs():
    #Set defaults in case we don't find what we need.
    checkData1 = True
    checkData2 = True
    checkData3 = True
    metaDataFilePath = None
    thermalBandFilePath = None
    img = None
    radianceMin = None
    radianceMax = None
    toFromX = []
    toFromY = []
    cellGridSize = 30
    
    #Make sure that the input to the image folder is an actual path on the person's computer.
    if os.path.exists(_landsatImgFolder):
        #Go through the files in the directory and try to find the ones that we need to make a thermal image.
        for file in os.listdir(_landsatImgFolder):
            fullFilePath = os.path.join(_landsatImgFolder,file)
            if os.path.isfile(fullFilePath):
                if str(fullFilePath).endswith('_MTL.txt'): metaDataFilePath = fullFilePath
                elif str(fullFilePath).endswith('_B6.TIF'): thermalBandFilePath = fullFilePath
        
        #Check to be sure that I was able to find a header file and a tiff file for the thermal band.
        if metaDataFilePath == None:
            checkData1 = False
            warning = 'Failed to find a valid metadata file in the connected _landsatImgFolder.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        if thermalBandFilePath == None:
            checkData1 = False
            warning = 'Failed to find a valid thermal band file in the connected _landsatImgFolder.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        checkData1 = False
        warning = '_landsatImgFolder is not a valid file path on your system.'
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    
    if metaDataFilePath != None and thermalBandFilePath != None:
        #Next, read the image file and get the height and width.
        img = Image.FromFile(thermalBandFilePath)
        imgWidth = img.Width
        imgHeight = img.Height
        
        #Next, read the metadata file and grab the max/min lat/long, and max/min radiance.
        latitudes = []
        longitudes = []
        
        headerData = open(metaDataFilePath, 'r')
        for line in headerData:
            if "CORNER" in line and "LAT" in line: latitudes.append(float(line.split(" = ")[-1]))
            elif "CORNER" in line and "LON" in line: longitudes.append(float(line.split(" = ")[-1]))
            elif "RADIANCE_MAXIMUM_BAND_6" in line: radianceMax = float(line.split(" = ")[-1])
            elif "RADIANCE_MINIMUM_BAND_6" in line: radianceMin = float(line.split(" = ")[-1])
            elif "GRID_CELL_SIZE_THERMAL" in line: cellGridSize = float(line.split(" = ")[-1])
        
        #Pull out the maximum and minimum latitude of the scene.
        latitudes.sort()
        longitudes.sort()
        maxLat = latitudes[-2]
        minLat = latitudes[1]
        maxLon = longitudes[-2]
        minLon = longitudes[1]
        print "The LANDSAT scene ranges from latitude " + str(minLat) + " to " + str(maxLat)
        print "The LANDSAT scene ranges from longitude " + str(minLon) + " to " + str(maxLon)
        
        #If there is no connected latitude and longitude, set the default to be the center of the image otherwise, check to be sure that we are not requesting anything outside of the scene.
        if latitude_ == None:
            centerCellX = int(imgWidth/2)
            print "The central latitude of the displying image is set to " + str(minLat+((maxLat-minLat)/2))
        else:
            #Check to be sure that the latitude is not beyond the maximum of the scene.
            if latitude_ <= minLat or latitude_ >= maxLat:
                centerCellX = None
                checkData2 = False
                warning = 'The connected lattitude lies outside of the LANDSAT scene.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            else:
                centerCellX = int((maxLat - latitude_)/(maxLat-minLat)*imgWidth)
                print "The central latitude of the displying image is set to " + str(latitude_)
        
        if longitude_ == None:
            centerCellY = int(imgHeight/2)
            print "The central longitude of the displying image is set to " + str(minLon+((maxLon-minLon)/2))
        else:
            #Check to be sure that the longitude is not beyond the maximum of the scene.
            if longitude_ <= minLon or longitude_ >= maxLon:
                centerCellY = None
                checkData3 = False
                warning = 'The connected longitude lies outside of the LANDSAT scene.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            else:
                if longitude_ < 0: centerCellY = int((longitude_-minLon)/(maxLon-minLon)*imgHeight)
                else: centerCellY = int((longitude_-minLon)/(maxLon-minLon)*imgHeight)
                print "The central longitude of the displying image is set to " + str(longitude_)
        
        
        if centerCellX and centerCellY:
            #If there is not connected imageWidth and imageHeight, set the default to 2000 meters.
            #If there is a connected width or height, check to be sure that we are not requesting anything outside the scene.
            if imageWidth_ == None: offsetX = int(1000/cellGridSize)
            else: offsetX = int((imageWidth_/2)/cellGridSize)
            toFromX = [centerCellX-offsetX, centerCellX+offsetX]
            if toFromX[0] < 0:
                toFromX[0] = 0
                warning = 'With the current imageWidth, the image would lie outside of the LANDSAT scene and so the left side has been set to the limit of the scene.'
                print warning
            if toFromX[1] > imgWidth:
                toFromX[1] = imgWidth
                warning = 'With the current imageWidth, the image would lie outside of the LANDSAT scene and so the right side has been set to the limit of the scene.'
                print warning
            
            if imageHeight_ == None: offsetY = int(1000/cellGridSize)
            else: offsetY = int((imageHeight_/2)/cellGridSize)
            toFromY = [centerCellY-offsetY, centerCellY+offsetY]
            if toFromY[0] < 0:
                toFromY[0] = 0
                warning = 'With the current imageHeight, the image would lie outside of the LANDSAT scene and so the bottom has been set to the limit of the scene.'
                print warning
            if toFromY[1] > imgHeight:
                toFromY[1] = imgHeight
                warning = 'With the current imageHeight, the image would lie outside of the LANDSAT scene and so the top has been set to the limit of the scene.'
                print warning
    
    if sampleSize_: sampleSize = sampleSize_
    else: sampleSize = 1
    
    #Do a final check of everything.
    if checkData1 == True and checkData2 == True and checkData3 == True: checkData = True
    else: checkData = False
    
    return checkData, img, toFromX, toFromY, radianceMin, radianceMax, cellGridSize, sampleSize

def main(img, toFromX, toFromY, radianceMin, radianceMax, cellGridSize, sampleSize):
    #Create the lists to be filled.
    temperatureValues = []
    geoTiffPts = []
    
    #Read the legendParameters.
    lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold = lb_preparation.readLegendParameters(legendPar_, False)
    legendTitle = 'C'
    
    #Set the constants before running the for loop.
    radianceDiff = radianceMax - radianceMin
    
    #Create lists for each of the x/y pixels.
    xPixelNums = range(toFromX[0], toFromX[1], sampleSize)
    yPixelNums = range(toFromY[0], toFromY[1], sampleSize)
    yPixelNums.reverse()
    
    #Run through the portion of the image that has been selected for display and calculate temperature values.
    for xCount, xVal in enumerate(xPixelNums):
        for yCount, yVal in enumerate(yPixelNums):
            point = rc.Geometry.Point3d(xCount*cellGridSize*sampleSize, yCount*cellGridSize*sampleSize, 0)
            geoTiffPts.append(point)
            color = img.GetPixel(xVal, yVal)
            DN = color.R/255
            cellRadiance = radianceMin + (DN*radianceDiff)
            cellTempKelvin = 1260.56 / math.log((( 607.76 * 0.95) / cellRadiance) +1)
            cellTempCelcius = cellTempKelvin - 273.15
            temperatureValues.append(cellTempCelcius)
    
    #Generate colors for the temperature values.
    colors = lb_visualization.gradientColor(temperatureValues, lowB, highB, customColors)
    
    #Create a legend for the temperature values.
    legend = []
    sceneRect = rc.Geometry.Rectangle3d(rc.Geometry.Plane.WorldXY, (toFromX[1]-toFromX[0])*cellGridSize, (toFromY[1]-toFromY[0])*cellGridSize)
    sceneCrv = sceneRect.ToNurbsCurve()
    lb_visualization.calculateBB([sceneCrv], True)
    legendSrfs, legendText, legendTextCrv, textPt, textSize = lb_visualization.createLegend(temperatureValues, lowB, highB, numSeg, legendTitle, lb_visualization.BoundingBoxPar, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold)
    legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, customColors)
    legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)
    legend.append(legendSrfs)
    for list in legendTextCrv:
        for item in list:
            legend.append(item)
    if legendBasePoint == None:
        legendBasePoint = lb_visualization.BoundingBoxPar[0]
    
    
    return temperatureValues, geoTiffPts, colors, legend, legendBasePoint


#Check to be sure Ladybug is flying.
initCheck = False
if sc.sticky.has_key('ladybug_release'):
    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): pass
        initCheck = True
    except:
        warning = "You need a newer version of Ladybug to use this compoent." + \
        "Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    if initCheck == True:
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
else:
    print "You should first let the Ladybug fly..."
    w = gh.GH_RuntimeMessageLevel.Warning
    ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")



if initCheck == True and _landsatImgFolder:
    checkData, img, toFromX, toFromY, radianceMin, radianceMax, cellGridSize, sampleSize = checkTheInputs()
    
    if checkData == True and _runIt == True:
        temperatures, geoTiffPts, ptColors, legend, legendBasePt = main(img, toFromX, toFromY, radianceMin, radianceMax, cellGridSize, sampleSize)
