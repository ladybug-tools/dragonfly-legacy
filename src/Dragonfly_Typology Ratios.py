#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2015, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com> 
# Honeybee is free software; you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published 
# by the Free Software Foundation; either version 3 of the License, 
# or (at your option) any later version. 
# 
# Honeybee is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Use this component to take building brep geometries that represent certain typologies and produce a list of typology ratios that can be plugged into the "Dragonfly_UWG Parameters from Typologies" component.
-
Provided by Dragonfly 0.0.01
    Args:
        _buildingTypologies: The list of building typologies that you intend to plug into the "Dragonfly_UWG Parameters from Typologies" component.
        _typology1Breps: The breps representing the buildings of the first typology connected to the _buildingTypologies input above.
        _typology2Breps: The breps representing the buildings of the second typology connected to the _buildingTypologies input above.
        _typology3Breps: The breps representing the buildings of the third typology connected to the _buildingTypologies input above.
        _typology4Breps: The breps representing the buildings of the fourth typology connected to the _buildingTypologies input above.
        _typology5Breps: The breps representing the buildings of the fifth typology connected to the _buildingTypologies input above.
        _typology6Breps: The breps representing the buildings of the sixth typology connected to the _buildingTypologies input above.
    Returns:
        typologyRatios: A list of typology ratios that can be plugged into the "Dragonfly_UWG Parameters from Typologies" component.

"""

ghenv.Component.Name = "Dragonfly_Typology Ratios"
ghenv.Component.NickName = 'TypologyRatios'
ghenv.Component.Message = 'VER 0.0.57\nSEP_29_2015'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "2 | GenerateUrbanClimate"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "5"
except: pass

print "yo"