# Dragonfly: A Plugin for Climate Data Generation (GPL) started by Chris Mackey
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
Use this component to create an AMY weather file from a year of data downloaded from the National Climactic Data Center (NCDC) database and an existing TMY weather file for the location.
_
The existing EPW file is needed both to determine values that are not present in the data file (like latitude) and to help determine a relationship between radiation/illuminance and sky cover.  Since NCDC data usually does not contain data for radiation but does contain detailed information on cloud cover, this cloud cover information and the relation between cloud cover and radiation is used to produce radiation values in the new file.
_
All of the files in the NCDC database can be found on this map here:
http://gis.ncdc.noaa.gov/map/viewer/#app=cdo&cfg=cdo&theme=hourly&layers=1&node=gi
_
The front page of the NCDC database can be found here:
http://www.ncdc.noaa.gov/cdo-web/
-
Provided by Dragonfly 0.0.01
    Args:
        _NCDCDataFile: A text string representing the file path of an annual NCDC data file that you have downloaded and unzipped to your system.  This is the file ending in 'dat.txt' in the unzipped folder that you have downloaded.  You can download NCDC data files by picking a location on this online map: http://gis.ncdc.noaa.gov/map/viewer/#app=cdo&cfg=cdo&theme=hourly&layers=1&node=gi.
        _originalEPW: An text string representing an .epw file path on your system.  This EPW should be for the same location as the NCDC file above.
        patchMissingVals_: Set to 'True' to have the component attempt to fill gaps in recorded data by placing in data from previous hours.  Set to 'False' to just write the default missing value into the EPW file (which is susually 99, 999, 9999, or some version of this).  The default is set to 'True'.  Note that setting this to 'False' will also mean that no radiation or illuminance calulation is performed for the weather file and the values of the original fil are written instead.
        AMYfilename_: An optional text string to set the name of the output AMY file.
        _runIt: Set to 'True' to run the component and generate an AMY file from the connected NCDC data and existing EPW file.
    Returns:
        readMe!:...
        epwFile: The file address of the AMY file that has been written to your machine.
"""


import scriptcontext as sc
import Grasshopper.Kernel as gh

ghenv.Component.Name = "Dragonfly_AMY from NCDC Data"
ghenv.Component.NickName = 'AMYfromNCDC'
ghenv.Component.Message = 'VER 0.0.01\nMAR_07_2016'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "3 | GenerateEPW"
#compatibleLBVersion = VER 0.0.59\nNOV_30_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


w = gh.GH_RuntimeMessageLevel.Warning


def computeRadSkyCoverRelation(skyCov, dirRad, difRad, glbRad):
    #Create the lists to be filled
    dirRadRelatMtx, difRadRelatMtx, glbRadRelatMtx = [], [], []
    for month in range(12):
        dirRadRelatMtx.append([])
        difRadRelatMtx.append([])
        glbRadRelatMtx.append([])
        for hour in range(24):
            dirRadRelatMtx[month].append([])
            difRadRelatMtx[month].append([])
            glbRadRelatMtx[month].append([])
            for cov in range(11):
                dirRadRelatMtx[month][hour].append([])
                difRadRelatMtx[month][hour].append([])
                glbRadRelatMtx[month][hour].append([])
    
    #Sort the lists into the matrices.
    def sortVals(hourlyList, matrix, cloudCov):
        for count, val in enumerate(hourlyList):
            d, m, t = lb_preparation.hour2Date(count+1, True)
            hour = t - 1
            matrix[m][hour][int(cloudCov[count])].append(val)
    sortVals(dirRad, dirRadRelatMtx, skyCov)
    sortVals(difRad, difRadRelatMtx, skyCov)
    sortVals(glbRad, glbRadRelatMtx, skyCov)
    
    #Average the sortedvalues of the maxrix.
    def avgVals(matrix):
        for mCount, month in enumerate(matrix):
            for hCount, hour in enumerate(month):
                for skyCnt, skyCov in enumerate(hour):
                    if len(skyCov) != 0:
                        matrix[mCount][hCount][skyCnt] = sum(skyCov)/len(skyCov)
    avgVals(dirRadRelatMtx)
    avgVals(difRadRelatMtx)
    avgVals(glbRadRelatMtx)
    
    #if there are gaps in the matrix, interpolate between neighboring values or take a neighboring value.
    def interpVals(matrix):
        for mCount, month in enumerate(matrix):
            for hCount, hour in enumerate(month):
                for skyCnt, skyCov in enumerate(hour):
                    if skyCov == []:
                        try: matrix[mCount][hCount][skyCnt] = float((matrix[mCount][hCount][skyCnt+1] + matrix[mCount][hCount][skyCnt-1])/2)
                        except:
                            try: matrix[mCount][hCount][skyCnt] = float((matrix[mCount][hCount][skyCnt+1] + matrix[mCount][hCount][skyCnt-1])/2)
                            except:
                                try: matrix[mCount][hCount][skyCnt] = float(matrix[mCount][hCount][skyCnt+1])
                                except:
                                    try: matrix[mCount][hCount][skyCnt] = float(matrix[mCount][hCount][skyCnt-1])
                                    except:
                                        print "did not make it"
                                        matrix[mCount][hCount][skyCnt] = 0
    interpVals(dirRadRelatMtx)
    interpVals(difRadRelatMtx)
    interpVals(glbRadRelatMtx)
    
    return dirRadRelatMtx, difRadRelatMtx, glbRadRelatMtx

def computeFromCloudCov(cloudCov, relatMtx):
    finalDataList = []
    for count, val in enumerate(cloudCov):
        d, m, t = lb_preparation.hour2Date(count+1, True)
        hour = t - 1
        finalDataList.append(relatMtx[m][hour][int(val)])
    
    return finalDataList


def getNCDC(NCDC_File, patchMissingVals, lb_preparation, lb_comfortModels):
    #Types of Data to Pull from the file.
    modelYear = []
    dbTemp = []
    dewPoint = []
    relHumid = []
    windSpeed = []
    windDir = []
    barPress = []
    cloudCov = []
    visibility = []
    ceilingHeight = []
    
    #Have a list that keeps track of the hours that have been pulled.
    dateList = []
    hourList = []
    
    #Have a list that relates NCDC sky cover to percent of the sky covered.
    percentSkyCovList = [0, 1, 2, 4, 5, 6, 8, 9, 10, 10]
    
    #Pull out the relevant information from the NCDCFile.
    NCDCFile = open(NCDC_File,"r")
    for lnum, line in enumerate(NCDCFile):
        if lnum > 1:
            splitLine = line.split(',')
            day = str(splitLine[2])
            hour = str(splitLine[3])[:2]
            date = day+hour
            
            if date not in dateList:
                try: lasthour = int(hourList[-1])
                except: lasthour = 0
                hourFloat = int(hour)
                
                if hourFloat != lasthour+1 and lnum != 2:
                    if hourFloat > lasthour+1:
                        while lasthour+1 < hourFloat:
                            
                            modelYear.append(''.join(list(splitLine[2])[:4]))
                            if float(splitLine[20]) > 900 and patchMissingVals: dbTemp.append(dbTemp[-1])
                            else: dbTemp.append(float(splitLine[20]))
                            if float(splitLine[22]) > 900 and patchMissingVals: dewPoint.append(dewPoint[-1])
                            else: dewPoint.append(float(splitLine[22]))
                            if float(splitLine[24]) > 9000 and patchMissingVals: barPress.append(barPress[-1])
                            else: barPress.append(float(splitLine[24]))
                            if float(splitLine[10]) > 900 and patchMissingVals:  windSpeed.append(float(splitLine[10]))
                            else:windSpeed.append(windSpeed[-1])
                            if float(splitLine[7]) > 900 and patchMissingVals: windDir.append(windDir[-1])
                            else: windDir.append(float(splitLine[7]))
                            if splitLine[12] == '99999' and patchMissingVals: ceilingHeight.append(ceilingHeight[-1])
                            else: ceilingHeight.append(float(splitLine[12]))
                            if splitLine[16] == '99999' or splitLine[16] == '      ' and patchMissingVals:visibility.append(visibility[-1])
                            else: visibility.append(float(splitLine[16]))
                            if splitLine[590] == '99' and patchMissingVals: cloudCov.append(cloudCov[-1])
                            else: cloudCov.append(percentSkyCovList[int(splitLine[590])])
                            
                            hourList.append(str(lasthour))
                            dateList.append(date)
                            
                            lasthour += 1
                    elif lasthour != 23:
                        while lasthour-24 < hourFloat-1:
                            modelYear.append(''.join(list(splitLine[2])[:4]))
                            if float(splitLine[20]) > 900 and patchMissingVals: dbTemp.append(dbTemp[-1])
                            else: dbTemp.append(float(splitLine[20]))
                            if float(splitLine[22]) > 900 and patchMissingVals: dewPoint.append(dewPoint[-1])
                            else: dewPoint.append(float(splitLine[22]))
                            if float(splitLine[24]) > 9000 and patchMissingVals: barPress.append(barPress[-1])
                            else: barPress.append(float(splitLine[24]))
                            if float(splitLine[10]) > 900 and patchMissingVals: windSpeed.append(float(splitLine[10]))
                            else: windSpeed.append(float(splitLine[10]))
                            if float(splitLine[7]) > 900 and patchMissingVals: windDir.append(windDir[-1])
                            else: windDir.append(float(splitLine[7]))
                            if splitLine[12] == '99999' and patchMissingVals: ceilingHeight.append(ceilingHeight[-1])
                            else: ceilingHeight.append(float(splitLine[12]))
                            if splitLine[16] == '99999' or splitLine[16] == '      ' and patchMissingVals: visibility.append(visibility[-1])
                            else: visibility.append(float(splitLine[16]))
                            if splitLine[590] == '99' and patchMissingVals: cloudCov.append(cloudCov[-1])
                            else: cloudCov.append(percentSkyCovList[int(splitLine[590])])
                            hourList.append(str(lasthour))
                            dateList.append(date)
                            
                            lasthour += 1
                    elif lasthour == 23:
                        lasthour = -1
                        while lasthour < hourFloat-1:
                            modelYear.append(''.join(list(splitLine[2])[:4]))
                            if float(splitLine[20]) > 900 and patchMissingVals: dbTemp.append(dbTemp[-1])
                            else: dbTemp.append(float(splitLine[20]))
                            if float(splitLine[22]) > 900 and patchMissingVals: dewPoint.append(dewPoint[-1])
                            else: dewPoint.append(float(splitLine[22]))
                            if float(splitLine[24]) > 9000 and patchMissingVals: barPress.append(barPress[-1])
                            else: barPress.append(float(splitLine[24]))
                            if float(splitLine[10]) > 900 and patchMissingVals: windSpeed.append(float(splitLine[10]))
                            else: windSpeed.append(float(splitLine[10]))
                            if float(splitLine[7]) > 900 and patchMissingVals: windDir.append(windDir[-1])
                            else: windDir.append(float(splitLine[7]))
                            if splitLine[12] == '99999' and patchMissingVals: ceilingHeight.append(ceilingHeight[-1])
                            else: ceilingHeight.append(float(splitLine[12]))
                            if splitLine[16] == '99999' or splitLine[16] == '      ' and patchMissingVals: visibility.append(visibility[-1])
                            else: visibility.append(float(splitLine[16]))
                            if splitLine[590] == '99' and patchMissingVals: cloudCov.append(cloudCov[-1])
                            else: cloudCov.append(percentSkyCovList[int(splitLine[590])])
                            hourList.append(str(lasthour))
                            dateList.append(date)
                            
                            lasthour += 1
                
                
                modelYear.append(''.join(list(splitLine[2])[:4]))
                if float(splitLine[20]) > 900 and patchMissingVals: dbTemp.append(dbTemp[-1])
                else: dbTemp.append(float(splitLine[20]))
                if float(splitLine[22]) > 900 and patchMissingVals: dewPoint.append(dewPoint[-1])
                else: dewPoint.append(float(splitLine[22]))
                if float(splitLine[24]) > 9000 and patchMissingVals: barPress.append(barPress[-1])
                else: barPress.append(float(splitLine[24]))
                if float(splitLine[10]) > 900 and patchMissingVals:
                    if lnum != 2: windSpeed.append(float(splitLine[10]))
                    else: windSpeed.append(0)
                else: windSpeed.append(float(splitLine[10]))
                if float(splitLine[7]) > 900 and patchMissingVals:
                    if lnum != 2: windDir.append(windDir[-1])
                    else: windDir.append(0)
                else: windDir.append(float(splitLine[7]))
                if splitLine[12] == '99999' and patchMissingVals:
                    if lnum != 2: ceilingHeight.append(ceilingHeight[-1])
                    else: ceilingHeight.append(0)
                else: ceilingHeight.append(float(splitLine[12]))
                if splitLine[16] == '99999' or splitLine[16] == '      ' and patchMissingVals: visibility.append(visibility[-1])
                else: visibility.append(float(splitLine[16]))
                if splitLine[590] == '99' and patchMissingVals:
                    if lnum != 2: cloudCov.append(cloudCov[-1])
                    else: cloudCov.append(0)
                else: cloudCov.append(percentSkyCovList[int(splitLine[590])])
                
                
                
                hourList.append(hour)
                dateList.append(date)
                
                #Final bit of code to make sure that everything sopt of the EPW is being filled in.
                hourForLB = int(date[-2:])
                dayForLB = int(date[-4:-2])
                monthForLB = int(date[-6:-4])
                HOYFromLB = lb_preparation.date2Hour(monthForLB, dayForLB, hourForLB)
                
                if HOYFromLB > len(hourList):
                    while len(hourList) < HOYFromLB:
                        print lasthour
                        print'something wrong with :' + str(monthForLB) + ',' + str(dayForLB) + ',' + str(hourForLB)
                        modelYear.append(dbTemp[-1])
                        dbTemp.append(modelYear[-1])
                        dewPoint.append(dewPoint[-1])
                        barPress.append(barPress[-1])
                        windSpeed.append(windSpeed[-1])
                        windDir.append(windDir[-1])
                        cloudCov.append(cloudCov[-1])
                        visibility.append(visibility[-1])
                        ceilingHeight.append(ceilingHeight[-1])
                        hourList.append(hour)
                        dateList.append(date)
                        hourForLB +=1
    
    NCDCFile.close()
    
    #Convert barometric pressure to Pa from hPa.
    barpressNew = []
    for val in barPress:
        barpressNew.append(float(val)*100)
    
    #Check cloud cover values to be sure that values greater than 100% are read as 100%
    for count, val in enumerate(cloudCov):
        if val > 9: cloudCov[count] = 9
    
    #Compute relative humidity from dry bulb and dew point.
    for count, temp in enumerate(dbTemp):
        if temp < 900 and dewPoint[count] < 900:
            RH = lb_comfortModels.calcRelHumidFromDryBulbDewPt(temp, dewPoint[count])
            if RH > 100: relHumid.append(100)
            else: relHumid.append(RH)
        else:
            relHumid.append(999)
    
    if len(hourList) < 8760:
        for count in range(8760-len(hourList)):
            modelYear.append(dbTemp[-1])
            dbTemp.append(modelYear[-1])
            dewPoint.append(dewPoint[-1])
            relHumid.append(relHumid[-1])
            windSpeed.append(windSpeed[-1])
            windDir.append(windDir[-1])
            barpressNew.append(barpressNew[-1])
            cloudCov.append(cloudCov[-1])
            visibility.append(visibility[-1])
            ceilingHeight.append(ceilingHeight[-1])
    
    return modelYear, dbTemp, dewPoint, relHumid, windSpeed, windDir, barpressNew, cloudCov, visibility, ceilingHeight

def writeEPW(originalEPW, AMYfilename, modelYear, dbTemp, dewPoint, relHumid, windSpeed, windDir, barPress, cloudCov, visibility, ceilingHeight, dirRad, difRad, glbRad, dirIll, difIll, glbIll):
    #Assemble all of the lines for the EPW.
    linesForEpw = []
    hourCount = 0
    originalEpwfile = open(originalEPW,"r")
    for lnum, line in enumerate(originalEpwfile):
        if lnum < 8: linesForEpw.append(line)
        else:
            splitLine = line.split(',')
            newline = str(modelYear[hourCount]) + ','
            newline = newline + str(splitLine[1]) + ','
            newline = newline + str(splitLine[2]) + ','
            newline = newline + str(splitLine[3]) + ','
            newline = newline + str(splitLine[4]) + ','
            newline = newline + str(splitLine[5]) + ','
            newline = newline + str(dbTemp[hourCount]) + ','
            newline = newline + str(dewPoint[hourCount]) + ','
            newline = newline + str(relHumid[hourCount]) + ','
            newline = newline + str(barPress[hourCount]) + ','
            newline = newline + str(splitLine[10]) + ','
            newline = newline + str(splitLine[11]) + ','
            newline = newline + str(splitLine[12]) + ','
            newline = newline + str(glbRad[hourCount]) + ','
            newline = newline + str(dirRad[hourCount]) + ','
            newline = newline + str(difRad[hourCount]) + ','
            newline = newline + str(glbIll[hourCount]) + ','
            newline = newline + str(dirIll[hourCount]) + ','
            newline = newline + str(difIll[hourCount]) + ','
            newline = newline + str(splitLine[19]) + ','
            newline = newline + str(windDir[hourCount]) + ','
            newline = newline + str(windSpeed[hourCount]) + ','
            newline = newline + str(cloudCov[hourCount]) + ','
            newline = newline + str(cloudCov[hourCount]) + ','
            newline = newline + str(visibility[hourCount]) + ','
            newline = newline + str(ceilingHeight[hourCount]) + ','
            newline = newline + str(splitLine[26]) + ','
            newline = newline + str(splitLine[27]) + ','
            newline = newline + str(splitLine[28]) + ','
            newline = newline + str(splitLine[29]) + ','
            newline = newline + str(splitLine[30]) + ','
            newline = newline + str(splitLine[31]) + ','
            newline = newline + str(splitLine[32]) + ','
            newline = newline + str(splitLine[33]) + ','
            newline = newline + str(splitLine[34])
            
            linesForEpw.append(newline)
            hourCount +=1
    
    #Write all of the data into a new file.
    workingDirInit = originalEPW.split('\\')[:-1]
    workingDir = ''
    for folder in workingDirInit:
        workingDir = workingDir + folder + '\\'
    finalFilePath = workingDir + AMYfilename + '.epw'
    finalFile = open(finalFilePath, "w")
    for line in linesForEpw:
        finalFile.write(line)
    
    #Close the files
    finalFile.close()
    originalEpwfile.close()
    
    
    return finalFilePath


def main(NCDCDataFile, originalEPW, lb_preparation, lb_comfortModels):
    #Set a default patchMissingVals_.
    if patchMissingVals_ == None: patchMissingVals = True
    else: patchMissingVals = patchMissingVals_
    
    #Set default AMYfilename.
    if AMYfilename_ == None: AMYfilename = originalEPW.split('\\')[-1].split('.epw')[0] + 'AMY'
    else:
        if AMYfilename_.endswith('.epw'): AMYfilename = AMYfilename.split('.epw')[0]
        else: AMYfilename = AMYfilename_
    
    #Determine the relationship between sky cover and radiation in the existing EPW file.
    weatherData = lb_preparation.epwDataReader(originalEPW)
    skyCov = weatherData[11][7:]
    dirRad = weatherData[5][7:]
    difRad = weatherData[6][7:]
    glbRad = weatherData[7][7:]
    dirIll = weatherData[8][7:]
    difIll = weatherData[9][7:]
    glbIll = weatherData[10][7:]
    dirRadRelatMtx, difRadRelatMtx, glbRadRelatMtx = computeRadSkyCoverRelation(skyCov, dirRad, difRad, glbRad)
    dirIllRelatMtx, difIllRelatMtx, glbIllRelatMtx = computeRadSkyCoverRelation(skyCov, dirIll, difIll, glbIll)
    
    #Grab all of the data from the NCDC file.
    modelYear, dbTemp, dewPoint, relHumid, windSpeed, windDir, barPress, cloudCov, visibility, ceilingHeight = getNCDC(NCDCDataFile, patchMissingVals, lb_preparation, lb_comfortModels)
    
    if patchMissingVals == True:
        #Compute radiation and illuminance values for the new weather file using the sky cover from the NCDCDataFile and the relational matrices.
        dirRad = computeFromCloudCov(cloudCov, dirRadRelatMtx)
        difRad = computeFromCloudCov(cloudCov, difRadRelatMtx)
        glbRad = computeFromCloudCov(cloudCov, glbRadRelatMtx)
        dirIll = computeFromCloudCov(cloudCov, dirIllRelatMtx)
        difIll = computeFromCloudCov(cloudCov, difIllRelatMtx)
        glbIll = computeFromCloudCov(cloudCov, glbIllRelatMtx)
    
    #Write all of the AMY data into a final EPW.
    amyEpwFile = writeEPW(originalEPW, AMYfilename, modelYear, dbTemp, dewPoint, relHumid, windSpeed, windDir, barPress, cloudCov, visibility, ceilingHeight, dirRad, difRad, glbRad, dirIll, difIll, glbIll)
    
    
    return amyEpwFile


#If Honeybee or Ladybug is not flying or is an older version, give a warning.
initCheck = True

#Ladybug check.
if not sc.sticky.has_key('ladybug_release') == True:
    initCheck = False
    print "You should first let Ladybug fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Ladybug fly...")
else:
    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): initCheck = False
        if sc.sticky['ladybug_release'].isInputMissing(ghenv.Component): initCheck = False
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_comfortModels = sc.sticky["ladybug_ComfortModels"]()
    except:
        initCheck = False
        warning = "You need a newer version of Ladybug to use this compoent." + \
        "Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)


if _runIt and initCheck:
    epwFile = main(_NCDCDataFile, _originalEPW, lb_preparation, lb_comfortModels)

