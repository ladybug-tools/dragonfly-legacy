# UWG Boundary Layer Parameters
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
Use this component to generate boundary layer parameters that can be plugged into the "Dragonfly_Run Urban Weather Generator" component.  This component is mostly for climatologists, meteorologists and urban weather experts and probably does not have to be used for most simulations.
-
Provided by Dragonfly 0.0.01
    Args:
        dayBndLayerHeight_: A number that represents the height in meters of the urban boundary layer during the daytime. This is the height to which the urban meterorological conditions are stable and representative of the overall urban area. Typically, this boundary layer height increases with the height of the buildings.  The default is set to 700 meters.
        nightBndLayerHeight_: A number that represents the height in meters of the urban boundary layer during the nighttime. This is the height to which the urban meterorological conditions are stable and representative of the overall urban area. Typically, this boundary layer height increases with the height of the buildings.  The default is set to 800 meters.
        referenceHeight_: A number that represents the reference height at which the vertical profile of potential temperature is vertical. It is the height at which the profile of air temperature becomes stable. Can be determined by flying helium balloons equipped with temperature sensors and recording the air temperatures at different heights.  The default is set to 150 meters.
    Returns:
        boundLayerPar: A list of refernce EPW site parameters that can be plugged into the "Dragonfly_Run Urban Weather Generator" component.
"""

ghenv.Component.Name = "Dragonfly_Boundary Layer Parameters"
ghenv.Component.NickName = 'boundaryLayerPar'
ghenv.Component.Message = 'VER 0.0.01\nOCT_17_2015'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "2 | GenerateUrbanClimate"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass


#Set default parameters.
if dayBndLayerHeight_: dayBndLayerHeight = dayBndLayerHeight_
else: dayBndLayerHeight = 700
if nightBndLayerHeight_: nightBndLayerHeight = nightBndLayerHeight_
else: nightBndLayerHeight = 80
if referenceHeight_: referenceHeight = referenceHeight_
else: referenceHeight = 150

boundLayerPar = "    <daytimeBLHeight>" + str(dayBndLayerHeight) + "</daytimeBLHeight>\n"
boundLayerPar = boundLayerPar + "    <nighttimeBLHeight>" + str(nightBndLayerHeight) + "</nighttimeBLHeight>\n"
boundLayerPar = boundLayerPar + "    <refHeight>" + str(referenceHeight) + "</refHeight>\n"
