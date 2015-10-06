# UWG Vegetation Parameters
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
Use this component to generate vegetation parameters that can be plugged into one of the "Dragonfly_UWG Parameters" components.
-
Provided by Dragonfly 0.0.01
    Args:
        vegStartMonth_: An integer from 1 to 12 that represents the first month after winter when vegetation begins to participate in the energy balance of the urban area (though photosynthesis and evapotranspiration).  If no value is input here, Dragonfly will attempt to guess this parameter by calculating the first month that average outdoor temperatures are above 12 C in the EPW file that you are altering.
        vegEndMonth_: An integer from 1 to 12 that represents the last month after summer that vegetation participates in the energy balance of the urban area (though photosynthesis and evapotranspiration).If no value is input here, Dragonfly will attempt to guess this parameter by calculating the last month that average outdoor temperatures are above 8 C in the EPW file that you are altering.
        vegetationAlbedo_: A number between 0 and 1 that represents the ratio of reflected radiation from vegetated surfaces to incident radiation upon them.  If no value is input here, the UWG will assume a typical vegetation albedo of 0.25.  This number may be higher for bright green grass or lower for coniferous trees.
        treeLatentFraction_: A number between 0 and 1 that represents the the fraction of absorbed solar energy by trees that is given off as latent heat (evapotranspiration). This affects the moisture balance and temperature in the urban area.  If no value is input here, a stypical value of 0.7 will be assumed, although this number may be lower in an arid climate or higher in a tropical climate.
        grassLatentFraction_: A number between 0 and 1 that represents the the fraction of absorbed solar energy by grass that is given off as latent heat (evapotranspiration). This affects the moisture balance and temperature in the urban area.  If no value is input here, a stypical value of 0.6 will be assumed, although this number may be lower in an arid climate or higher in a tropical climate.
    Returns:
        vegetationPar: A list of vegetation parameters that can be plugged into either the "Dragonfly_UWG Parameters from Typologies" or the "Dragonfly_UWG Parameters from HBZones" component.
"""

ghenv.Component.Name = "Dragonfly_Vegetation Parameters"
ghenv.Component.NickName = 'vegetationPar'
ghenv.Component.Message = 'VER 0.0.01\nSEP_29_2015'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "2 | GenerateUrbanClimate"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass
