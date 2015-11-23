# UWG Building Typlogy from Parameters
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
Use this component to generate a default building typology for a residential building to be used with the "Dragonfly_UWG Parameters from Typologies" component.  This default typology is based on the OpenStudio template of an open office and will automatically assign constructions based on the connected _climateZone.
-
Provided by Dragonfly 0.0.01
    Args:
        _flr2FlrHeight: The floor-to-floor height of the building typology in meters. Typical values range from 3 to 4 meters.
        _window2Wall: A number between 0 and 1 that represents the fraction of the exterior wall surface occupied by windows.  Typical recommended values for this are around 0.4 but many recent buildings push the amount of glazing up higher all of the way to 0.8 and 0.9.
        _climateZone: An integer from 1 to 8 that represents the ASHRAE climate zone of the urban area.  This will be used to set the constructions of the typology.  You can find the ASHRA climate zone for a weather file using the "Ladybug_Import stat" component.
        roofVegFraction_: A number between 0 and 1 that represents the fraction of the building's roof that is covered in vegetation, such as green roof, grassy lawn, etc.  If no value is input here, it will be assumed that the roof has no vegetation.
        wallVegFraction_: A number between 0 and 1 that represents the fraction of the building's walls that is covered in vegetation, such as green wall, vine-covered wall, etc. If no value is input here, it will be assumed that the wall has no vegetation.
    Returns:
        buildingTypology: A building typology that can be plugged into the "Dragonfly_UWG Parameters from Typologies" component.
"""

ghenv.Component.Name = "Dragonfly_Default Residential Typology"
ghenv.Component.NickName = 'ResidentialTypology'
ghenv.Component.Message = 'VER 0.0.01\nNOV_22_2015'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "2 | GenerateUrbanClimate"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass

import scriptcontext as sc
import Grasshopper.Kernel as gh

def main(flr2Flr, glzRatio, climateZone, df_textGen):
    #Check the glazing ratio.
    if glzRatio < 0 or glzRatio > 1:
        warning = "_window2Wall must be between 0 and 1."
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        return -1
    
    #Check the climate zone.
    try: climateZoneNum = int(climateZone)
    except:
        climateZoneChar = list(climateZone)
        try: climateZoneNum = int(climateZoneChar[0])
        except:
            warning = "_climateZone not recognized."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            return -1
    if climateZoneNum < 1 or climateZoneNum > 8:
        warning = "_climateZone must be between 1 (warmest) and 8 (coldest)."
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        return -1
    
    #Check the roof and vegetated wall fraction.
    if roofVegFraction_ != None:
        roofVegFraction = roofVegFraction_
        if roofVegFraction_ < 1 or roofVegFraction_ > 8:
            warning = "roofVegFraction_ must be between 1 (warmest) and 8 (coldest)."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            return -1
    else: roofVegFraction = 0
    
    if wallVegFraction_ != None:
        wallVegFraction = wallVegFraction_
        if wallVegFraction_ < 1 or wallVegFraction_ > 8:
            warning = "wallVegFraction_ must be between 1 (warmest) and 8 (coldest)."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            return -1
    else: wallVegFraction = 0
    
    
    typology = df_textGen.defaultResidTypology(flr2Flr, glzRatio, climateZoneNum, wallVegFraction, roofVegFraction)
    
    return typology

initCheck = True
if sc.sticky.has_key('dragonfly_release') == True:
    df_textGen = sc.sticky["dragonfly_UWGText"]()
else:
    initCheck = False
    print "You should first let Dragonfly  fly..."
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "You should first let Dragonfly fly...")


if initCheck == True and _flr2FlrHeight and _window2Wall and _climateZone:
    result = main(_flr2FlrHeight, _window2Wall, _climateZone, df_textGen)
    if result != -1: buildingTypology = result