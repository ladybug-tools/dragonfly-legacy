# UWG Building Typlogy from HBZone
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
Use this component to generate a building typology to be used with the "Dragonfly_UWG Parameters from Typologies" component using a single HBZone that represents the charateristics of a whole building.  It is recommended that this zone be an entire floor of the full building typology that it represents.
-
Provided by Dragonfly 0.0.01
    Args:
        _HBZones: A single HBZone that represents the charateristics of a whole building.  It is recommended that this zone be an entire floor of the full building typology that it represents.  This input can also be several HBZones and will result in several building typologies will be produced.
        flr2FlrHeight_: The floor-to-floor height of the building typology in meters. Typical values range from 3 to 4 meters.
        roofVegFraction_: A number between 0 and 1 that represents the fraction of the building's roof that is covered in vegetation, such as green roof, grassy lawn, etc. If no value is input here, it will be assumed that the roof has no vegetation.
        wallVegFraction_: A number between 0 and 1 that represents the fraction of the building's walls that is covered in vegetation, such as green wall, vine-covered wall, etc. If no value is input here, it will be assumed that the roof has no vegetation.
        coolingCOP_: A number representing the mechanical cooling system coefficient of performance (COP), as defined as the ratio of the heat removed from a building over the electrical energy used by the building cooling system.  If no value is input here, a typical value of 3.7 will be used.
        heatingCOP_: A number representing the effectiveness of the building heating system at transforming the fuel energy (either electricity or burned fuel) into building heat energy. If no value is input here, a typical value of 0.8 will be used, representative of a typical gas furnace.
        coolingSystemType_: Set to 'True' to have the building modeled with an air-based cooling system and set to 'False' to have the building modeled with a water-based system.  The default is set to 'True' to model the building with a water-based system.
        heatFac2Canyon_: A number between 0 an 1 that represents the fraction of the waste heat from the mechanical cooling system that is exhausted into the urban canyon as opposed to being release above your neighborhood boundary layer.  If no value is input here, a default of 0.5 will be used, assuming that half of the cooling system's waste heat is rejected to the canyon in the fashion that window AC units would.  Set to 0 to assume that all wast heat is exhausted through the roof.
    Returns:
        buildingTypology: A building typology that can be plugged into the "Dragonfly_UWG Parameters from Typologies" component.
"""

ghenv.Component.Name = "Dragonfly_Building Typology from HBZone"
ghenv.Component.NickName = 'BldgTypologyFromZone'
ghenv.Component.Message = 'VER 0.0.01\nSEP_29_2015'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "2 | GenerateUrbanClimate"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass
