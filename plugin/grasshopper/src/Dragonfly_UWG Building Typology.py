# Dragonfly: A Plugin for Climate Modeling (GPL) started by Chris Mackeu
# This file is part of Dragonfly.
#
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Use this component to generate a default building typology to be used with the "Dragonfly_UWG City" component.  The specific characteristcs of these typologies are based on the US Department of Energy (DoE) Building types.  Wall, roof, and window constructions are based on the climateZone of the epw weather file.
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

ghenv.Component.Name = "Dragonfly_UWG Building Typology"
ghenv.Component.NickName = 'BldgTypology'
ghenv.Component.Message = 'VER 0.0.01\nOCT_29_2016'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "01::UWG"
ghenv.Component.AdditionalHelpFromDocStrings = "2"

