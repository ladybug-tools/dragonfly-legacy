# Generate Urban Morphology
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
Use this component to generate geometry representing a simple urban area from the street canyon height-to-with ratio and a few other basic parameters that are typically linked to urban heat island effect.  These geometries can be plugged into the "Dragonfly_UWG Parameters from Typologies" component or the brepsForHBZones can be turned completely into HBZones to be used with the "Dragonfly_UWG PArameters from HBZones" component.
-
Provided by Dragonfly 0.0.01
    Args:
        _buildingHeight: A number in Rhino model units representing the height to make the buildings.
        _streetCanyonH/W: A number greater than 0 that represents the ratio between the width of the typical urban street canyon and the height of the surrounding buildings. Typical values can range from 0.25 for a subuurban area all of the ay up to 4 for a dense downtown area.
        blockXDimension_: A number that represents the East-West dimension of the typical urban block in Rhino model units.  The default is set to 100 meters.
        blockYDimensionn_: A number that represents the North-South dimension of the typical urban block in Rhino model units.  The default is set to 100 meters.
        orientationAngle_: A number between 0 and 90 that represents the degrees from a typical North-South orientation in which the urban morphology sits.
        treeCoverage_: A number between 0 and 1 that represents the fraction of the urban ground that is covered in trees.  This will be used to generate the treeBreps output from this component.  The default is set to 0 to produce no trees.
        grassCoverage_: A number between 0 and 1 that represents the fraction of the urban ground that is covered in grass.  This will be used to generate the grassBreps output from this component.  The default is set to 0 to produce no grass.
        floorHeights_: A number or list of numbers that represents the height of each floor in the urban area.  This will be used to divide the building mass into floors for the brepsForHBZones output.
        _runIt: Set to 'True' to run the component and generate an urban area based on the input urban morphology parameters.
    Returns:
        readMe!: ...
        FAR: The floor area ratio of the generated urban area.  Use this to keep trak of the density of your urban morphology.
        brepsForHBZoens: A list of closed solids that represent the floors of each building in the generated urban area.  These breps can be turned into HBZones that can be plugged into the "Dragonfly_UWG Parameters from HBZones" component.
        buildingBreps: A list of closed solids that represent the buildings of the urban.  These breps can be plugged into the "Dragonfly_UWG Parameters from Typologies" component.
        pavementBrep: A list of breps that represent the paved portion of the urban area.  These breps can be plugged into either the "Dragonfly_UWG Parameters from Typologies" component or the "Dragonfly_UWG Parameters from HBZones" component.
        treeBreps: A list of breps that represent the trees of the urban area that is being modeled. These breps can be plugged into either the "Dragonfly_UWG Parameters from Typologies" component or the "Dragonfly_UWG Parameters from HBZones" component.
        grassBrep:  A list of breps that represent the grassy ground surfaces of the urban area. These breps can be plugged into either the "Dragonfly_UWG Parameters from Typologies" component or the "Dragonfly_UWG Parameters from HBZones" component.
"""

ghenv.Component.Name = "Dragonfly_Urban Morphology from Canyon Height Width"
ghenv.Component.NickName = 'UrbanMorphFromCanyon'
ghenv.Component.Message = 'VER 0.0.01\nSEP_29_2015'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "2 | GenerateUrbanClimate"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "5"
except: pass