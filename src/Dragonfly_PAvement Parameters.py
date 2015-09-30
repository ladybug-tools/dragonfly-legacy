# UWG Pavement Parameters
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
Use this component to generate pavement parameters that can be plugged into one of the "Dragonfly_UWG Parameters" components.
-
Provided by Dragonfly 0.0.01
    Args:
        pavementConstruction_: A text string representing the construction of the uban pavement.  This construction can be either from the OpenStudio Library (the "Honeybee_Call from EP Construction Library" component) or it can be a custom construction from the "Honeybee_EnergyPlus Construction" component.  If no construction is input here, a default construction for asphalt will be used for simulating all paved areas of the urban neighborhood.
        vegetationCoverage_: A number between 0 and 1 that represents the fraction of the pavementBrep plugged into the 'Dragonfly_UWG Parameters' component that is covered in grass or shrubs.  If no value is input here it will be assumed that all ground breps plugged into the 'UWG Parameters' component are completely paved.  This variable is particularly helpful if you do not want to plug in grassBreps into the 'UWG Parameters' component and just want to put a single surface and a value here for the fraction of grass area.
        nonBldgLatentFract_: A number between 0 and 1 that represents the the fraction of the nonBldgAnthroHeat_ plugged into the 'Dragonfly_UWG Parameters' component that is given off as latent heat.  LAtent heat is heat that goes towards evaporating water as opposed to raising the temperature of the air.  If no value is plugged in here, it will be assumed that all of the non-building antrhopogenic heat is sensible.
    Returns:
        pavementPar: A list of pavement parameters that can be plugged into either the "Dragonfly_UWG Parameters from Typologies" or the "Dragonfly_UWG Parameters from HBZones" component.
"""

ghenv.Component.Name = "Dragonfly_Pavement Parameters"
ghenv.Component.NickName = 'pavementPar'
ghenv.Component.Message = 'VER 0.0.01\nSEP_29_2015'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "2 | GenerateUrbanClimate"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass
