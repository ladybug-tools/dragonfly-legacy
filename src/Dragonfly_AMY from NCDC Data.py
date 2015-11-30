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
Use this component to generate a building typology using a HBZone that represents a single floor of the entire building.  The resulting typology can be plugged into the "Dragonfly_UWG Parameters from Typologies" component.
-
Provided by Dragonfly 0.0.01
    Args:
        _HBZones: A HBZone that represents a single floor of the whole building typology that you hope to create.  While it is important that this zone represent a single typical floor for the building typology, the roof construction of this zone should be representative of the roof of the whole building (not an interior ceilings).  The floor of the zone represents the interior floor construction.
        roofVegFraction_: A number between 0 and 1 that represents the fraction of the building's roof that is covered in vegetation, such as green roof, grassy lawn, etc. If no value is input here, it will be assumed that the roof has no vegetation.
        wallVegFraction_: A number between 0 and 1 that represents the fraction of the building's walls that is covered in vegetation, such as green wall, vine-covered wall, etc. If no value is input here, it will be assumed that the roof has no vegetation.
        coolingCOP_: A number representing the mechanical cooling system coefficient of performance (COP), as defined as the ratio of the heat removed from a building over the electrical energy used by the building cooling system.  If no value is input here, a typical value of 3.7 will be used.
        heatingCOP_: A number representing the effectiveness of the building heating system at transforming the fuel energy (either electricity or burned fuel) into building heat energy. If no value is input here, a typical value of 0.8 will be used, representative of a typical gas furnace.
        coolingSystemType_: Set to 'True' to have the building modeled with an air-based cooling system and set to 'False' to have the building modeled with a water-based system.  The default is set to 'True' to model the building with an air-based system.
        heatFract2Canyon_: A number between 0 an 1 that represents the fraction of the waste heat from the mechanical cooling system that is exhausted into the urban canyon as opposed to being release above your neighborhood boundary layer.  If no value is input here, a default of 0.5 will be used, assuming that half of the cooling system's waste heat is rejected to the canyon in the fashion that window AC units would.  Set to 0 to assume that all waste heat is exhausted through the roof.
    Returns:
        buildingTypology: A building typology that can be plugged into the "Dragonfly_UWG Parameters from Typologies" component.
"""


import scriptcontext as sc
import Grasshopper.Kernel as gh

ghenv.Component.Name = "Dragonfly_AMY from NCDC Data"
ghenv.Component.NickName = 'AMYfromNCDC'
ghenv.Component.Message = 'VER 0.0.01\nNOV_30_2015'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "3 | GenerateEPW"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


w = gh.GH_RuntimeMessageLevel.Warning


def ncdc2epw(NCDC_File, lb_comfortModels):
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
    
    #Pull out the relevant information from the NCDCFile.
    NCDCFile = open(NCDC_File,"r")
    for lnum, line in enumerate(NCDCFile):
        if lnum > 1:
            day = str(line.split(',')[2])
            hour = str(line.split(',')[3])[:2]
            date = day+hour
            
            if date not in dateList:
                try:
                    lasthour = int(hourList[-1])
                    hourFloat = int(hour)
                    if hourFloat != lasthour+1:
                        if hourFloat > lasthour+1:
                            while lasthour+1 < hourFloat:
                                modelYear.append(float(line.split(',')[2]))
                                if float(line.split(',')[12]) > 900: dbTemp.append(dbTemp[-1])
                                else: dbTemp.append(float(line.split(',')[20]))
                                if float(line.split(',')[22]) > 900: dewPoint.append(dewPoint[-1])
                                else: dewPoint.append(float(line.split(',')[22]))
                                barPress.append(float(line.split(',')[24]))
                                windSpeed.append(float(line.split(',')[10]))
                                windDir.append(float(line.split(',')[7]))
                                if line.split(',')[12] == '99999': ceilingHeight.append(ceilingHeight[-1])
                                else: ceilingHeight.append(float(line.split(',')[12]))
                                if line.split(',')[16] == '99999' or line.split(',')[16] == '      ': visibility.append(visibility[-1])
                                else: visibility.append(float(line.split(',')[16]))
                                if line.split(',')[590] == '99': cloudCov.append(cloudCov[-1])
                                else: cloudCov.append(float(line.split(',')[590]))
                                
                                hourList.append(str(lasthour))
                                dateList.append(date)
                                
                                lasthour += 1
                        elif lasthour != 23:
                            while lasthour-24 < hourFloat-1:
                                modelYear.append(float(line.split(',')[2]))
                                if float(line.split(',')[12]) > 900: dbTemp.append(dbTemp[-1])
                                else: dbTemp.append(float(line.split(',')[20]))
                                if float(line.split(',')[22]) > 900: dewPoint.append(dewPoint[-1])
                                else: dewPoint.append(float(line.split(',')[22]))
                                barPress.append(float(line.split(',')[24]))
                                windSpeed.append(float(line.split(',')[10]))
                                windDir.append(float(line.split(',')[7]))
                                if line.split(',')[12] == '99999': ceilingHeight.append(ceilingHeight[-1])
                                else: ceilingHeight.append(float(line.split(',')[12]))
                                if line.split(',')[16] == '99999' or line.split(',')[16] == '      ': visibility.append(visibility[-1])
                                else: visibility.append(float(line.split(',')[16]))
                                if line.split(',')[590] == '99': cloudCov.append(cloudCov[-1])
                                else: cloudCov.append(float(line.split(',')[590]))
                                hourList.append(str(lasthour))
                                dateList.append(date)
                                
                                lasthour += 1
                except: pass
                
                modelYear.append(float(line.split(',')[2]))
                if float(line.split(',')[12]) > 900: dbTemp.append(dbTemp[-1])
                else: dbTemp.append(float(line.split(',')[20]))
                if float(line.split(',')[22]) > 900: dewPoint.append(dewPoint[-1])
                else: dewPoint.append(float(line.split(',')[22]))
                barPress.append(float(line.split(',')[24]))
                windSpeed.append(float(line.split(',')[10]))
                windDir.append(float(line.split(',')[7]))
                if line.split(',')[12] == '99999': ceilingHeight.append(ceilingHeight[-1])
                else: ceilingHeight.append(float(line.split(',')[12]))
                if line.split(',')[16] == '99999' or line.split(',')[16] == '      ': visibility.append(visibility[-1])
                else: visibility.append(float(line.split(',')[16]))
                if line.split(',')[590] == '99': cloudCov.append(cloudCov[-1])
                else: cloudCov.append(float(line.split(',')[590]))
                
                hourList.append(hour)
                dateList.append(date)
    
    NCDCFile.close()
    
    #Convert barometric pressure to Pa from hPa.
    barpressNew = []
    for val in barPress:
        barpressNew.append(float(val)*100)
    
    #Compute relative humidity from dry bulb and dew point.
    for count, temp in enumerate(dbTemp):
        RH = lb_comfortModels.calcRelHumidFromDryBulbDewPt(temp, dewPoint[count])
        if RH > 100: relHumid.append(100)
        else: relHumid.append(RH)
    
    return dewPoint


def main(NCDCDataFile, originalEPW, lb_preparation, lb_comfortModels):
    
    data = ncdc2epw(NCDCDataFile, lb_comfortModels)
    
    
    return None


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

