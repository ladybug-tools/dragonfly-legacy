# UWG Reference Site Parameters
#
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
Use this component to generate refernce EPW site parameters that can be plugged into the "Dragonfly_Run Urban Weather Generator" component.  If you are using standard files from the US Department of Energy, you should never need to use this component.  This component is onyl for when your data was recorded using non-standard means, such as an experiment that you have run in an actual urban canyon.
-
Provided by Dragonfly 0.0.01
    Args:
        avgObstacleHeight_: A number that represents the height in meters of objects that obstruct the view to the sky at the weather station site, such as trees and buildings.  The default is set to 0.1.
        pavementConstr_: A text string representing the construction of the uban pavement.  This construction can be either from the OpenStudio Library (the "Honeybee_Call from EP Construction Library" component) or it can be a custom construction from the "Honeybee_EnergyPlus Construction" component.  If no construction is input here, a default construction for asphalt will be used for simulating all paved areas of the urban neighborhood.
        vegetationCoverage_: A number between 0 and 1 that represents that fraction of the _pavementBrep that is covered in grass. If nothing is input here, it will be assumed that half of the EPW site is covered in grass.
        inclinationAngle_: A number between 0 and 1 that that represents the dinensionless inclination angle of the ground surfaces of the reference site:
            _
            0 = Perfectly vertical surface  (like a wall)
            0.5 = Sloped surfacece that is 45 degrees from the horizontal.
            1 = Perfectly horizontal surface (like a flat roof)
        tempMeasureHeight_: A number that represents the height in meters at which temperature is measured on the weather station.  The default is set to 10 meters as this is the standard measurement height for UD Department of Energy EPW files.
        windMeasureHeight_: A number that represents the height in meters at which wind speed is measured on the weather station.  The default is set to 10 meters as this is the standard measurement height for UD Department of Energy EPW files.
    Returns:
        pavementPar: A list of refernce EPW site parameters that can be plugged into the "Dragonfly_Run Urban Weather Generator" component.
"""

ghenv.Component.Name = "Dragonfly_Reference EPW Parameters"
ghenv.Component.NickName = 'RefEPWPar'
ghenv.Component.Message = 'VER 0.0.01\nNOV_22_2015'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "2 | GenerateUrbanClimate"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass


import scriptcontext as sc

from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh


def checkTheInputs(df_textGen):
    checkData = True
    
    #Check the inclination angle.
    if inclinationAngle_:
        if inclinationAngle_ >= 0 and inclinationAngle_ <= 1:
            inclinationAngle = inclinationAngle_
        else:
            inclinationAngle = 1
            checkData = False
            warning = "inclinationAngle_ must be between 0 (wall) and 1 (roof)."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else: inclinationAngle = 1
    
    #Check the inclination angle.
    if vegetationCoverage_:
        if vegetationCoverage_ >= 0 and vegetationCoverage_ <= 1:
            vegCoverage = vegetationCoverage_
        else:
            vegCoverage = 1
            checkData = False
            warning = "vegetationCoverage_ must be between 0 and 1."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else: vegCoverage = 0.5
    
    if pavementConstruction_:
        try:
            pavementConstr = df_textGen.createXMLFromEPConstr(pavementConstruction_, 'ruralRoad', vegCoverage, 'setByEPW')
        except:
            checkData = False
            warning = "pavementConstruction_ is not valid."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        pavementConstr = '    <ruralRoad>\n' + \
            '        <albedo>0.25</albedo>\n' + \
            '        <emissivity>0.95</emissivity>\n' + \
            '        <materials name="Default">\n' + \
            '          <names>\n' + \
            '            <item>asphalt</item>\n' + \
            '          </names>\n' + \
            '          <thermalConductivity>\n' + \
            '            <item>1</item>\n' + \
            '          </thermalConductivity>\n' + \
            '          <volumetricHeatCapacity>\n' + \
            '            <item>1600000</item>\n' + \
            '          </volumetricHeatCapacity>\n' + \
            '          <thickness>1.25</thickness>\n' + \
            '        </materials>\n' + \
            '        <vegetationCoverage>' + str(vegCoverage) + '</vegetationCoverage>\n' + \
            '        <inclination>' + str(inclinationAngle) + '</inclination>\n' + \
            '        <initialTemperature>setByEPW</initialTemperature>\n' + \
            '      </ruralRoad>\n'
    
    
    return checkData, pavementConstr


def main(pavementConstr):
    epwSiteParString =  '    <averageObstacleHeight>0.1</averageObstacleHeight>\n' + pavementConstr
    
    if tempMeasureHeight_: tempHeight = tempMeasureHeight_
    else: tempHeight = 10
    
    if windMeasureHeight_: windHeight = windMeasureHeight_
    else: windHeight = 10
    
    epwSitePar = [epwSiteParString, tempHeight, windHeight]
    
    return epwSitePar



#Check to be sure that Dragonfly is flying.
initCheck = False
if sc.sticky.has_key('honeybee_release') and sc.sticky.has_key("dragonfly_release"):
    df_textGen = sc.sticky["dragonfly_UWGText"]()
    initCheck = True
else:
    if not sc.sticky.has_key("honeybee_release"):
        warning = "You need to let Honeybee  fly to use this component."
        print warning
    if not sc.sticky.has_key("dragonfly_release"):
        warning = "You need to let Dragonfly fly to use this component."
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)

if initCheck == True:
    checkData, pavementConstr = checkTheInputs(df_textGen)
    if checkData:
        epwSitePar = main(pavementConstr)
