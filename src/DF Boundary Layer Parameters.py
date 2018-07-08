# Dragonfly: A Plugin for Climate Modeling (GPL) started by Chris Mackey <chris@ladybug.tools> 
# This file is part of Dragonfly.
#
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Use this component to generate boundary layer parameters that can be plugged into the "DF Run Urban Weather Generator" component.  This component is mostly for climatologists, meteorologists and urban weather experts and probably does not have to be used for most simulations.
-
Provided by Dragonfly 0.0.03
    Args:
        _day_height_: A number that represents the height in meters of the urban boundary layer during the daytime. This is the height to which the urban meterorological conditions are stable and representative of the overall urban area. Typically, this boundary layer height increases with the height of the buildings.  The default is set to 1000 meters.
        _night_height_: A number that represents the height in meters of the urban boundary layer during the nighttime. This is the height to which the urban meterorological conditions are stable and representative of the overall urban area. Typically, this boundary layer height increases with the height of the buildings.  The default is set to 80 meters.
        _inversion_height_: A number that represents the height at which the vertical profile of potential temperature becomes stable. It is the height at which the profile of air temperature becomes stable. Can be determined by flying helium balloons equipped with temperature sensors and recording the air temperatures at different heights.  The default is set to 150 meters.
        _circulation_coeff_: A number that represents the circulation coefficient.  The default is 1.2 per Bueno, Bruno (2012).
        _exchange_coeff_: A number that represents the exchange coefficient.  The default is 1.0 per Bueno, Bruno (2014).
    Returns:
        bnd_layer_par: A list of refernce EPW site parameters that can be plugged into the "DF Run Urban Weather Generator" component.
"""

ghenv.Component.Name = "DF Boundary Layer Parameters"
ghenv.Component.NickName = 'BndLayerPar'
ghenv.Component.Message = 'VER 0.0.03\nJUL_08_2018'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "1 | Urban Weather"
#compatibleDFVersion = VER 0.0.02\nMAY_13_2018
ghenv.Component.AdditionalHelpFromDocStrings = "0"


import scriptcontext as sc
import Grasshopper.Kernel as gh

#Dragonfly check.
init_check = True
if not sc.sticky.has_key('dragonfly_release') == True:
    init_check = False
    print "You should first let Drafgonfly fly..."
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "You should first let Drafgonfly fly...")
else:
    if not sc.sticky['dragonfly_release'].isCompatible(ghenv.Component): init_check = False
    if sc.sticky['dragonfly_release'].isInputMissing(ghenv.Component): init_check = False
    df_BndLayerPar = sc.sticky["dragonfly_BoundaryLayerPar"]

if init_check == True:
    bnd_layer_par = df_BndLayerPar(_day_height_, _night_height_, _inversion_height_, 
        _circulation_coeff_, _exchange_coeff_)
