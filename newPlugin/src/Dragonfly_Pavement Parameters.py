# Dragonfly: A Plugin for Climate Modeling (GPL) started by Chris Mackey <chris@ladybug.tools> 
# This file is part of Dragonfly.
#
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Use this component to generate parameters that describe the pavement of the urban area, which can be plugged into the "Dragonfly_UWG City" component.
-
Provided by Dragonfly 0.0.02
    
    Args:
        _albedo_: A number between 0 and 1 that represents the surface albedo (or reflectivity) of the pavement.  The default is set to 0.1, which is typical of fresh asphalt.
        _thickness_: A number that represents the thickness of the pavement material in meters (m).  The default is set to 0.5 meters.
        _conductivity_:  A number representing the conductivity of the pavement material in W/m-K.  This is the heat flow in Watts across one meter thick of the material when the temperature difference on either side is 1 Kelvin. The default is set to 1 W/m-K, which is typical of asphalt.
        _specificHeat_:  A number representing the volumetric heat capacity of the pavement material in J/m3-K.  This is the number of joules needed to raise one cubic meter of the material by 1 degree Kelvin.  The default is set to 1,600,000 J/m3-K, which is typical of asphalt.
    Returns:
        pavementPar: Pavement parameters that can be plugged into the "Dragonfly_UWG City" component.

"""

ghenv.Component.Name = "Dragonfly_Pavement Parameters"
ghenv.Component.NickName = 'pavementPar'
ghenv.Component.Message = 'VER 0.0.02\nAPR_29_2018'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "01::UWG"
ghenv.Component.AdditionalHelpFromDocStrings = "4"


