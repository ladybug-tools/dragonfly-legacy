# Dragonfly: A Plugin for Climate Modeling (GPL) started by Chris Mackey <chris@ladybug.tools> 
# This file is part of Dragonfly.
#
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Use this component to generate boundary layer parameters that can be plugged into the "Dragonfly_Run Urban Weather Generator" component.  This component is mostly for climatologists, meteorologists and urban weather experts and probably does not have to be used for most simulations.
-
Provided by Dragonfly 0.0.02
    Args:
        _dayBndLayerHeight_: A number that represents the height in meters of the urban boundary layer during the daytime. This is the height to which the urban meterorological conditions are stable and representative of the overall urban area. Typically, this boundary layer height increases with the height of the buildings.  The default is set to 1000 meters.
        _nightBndLayerHeight_: A number that represents the height in meters of the urban boundary layer during the nighttime. This is the height to which the urban meterorological conditions are stable and representative of the overall urban area. Typically, this boundary layer height increases with the height of the buildings.  The default is set to 80 meters.
        _inversionHeight_: A number that represents the height at which the vertical profile of potential temperature becomes stable. It is the height at which the profile of air temperature becomes stable. Can be determined by flying helium balloons equipped with temperature sensors and recording the air temperatures at different heights.  The default is set to 150 meters.
        _circulationCoeff_: A number that represents the circulation coefficient.  The default is 1.2 per Bueno, Bruno (2012).
        _exchangeCoeff_: A number that represents the exchange coefficient.  The default is 1.0 per Bueno, Bruno (2014).
    Returns:
        bndLayerPar: A list of refernce EPW site parameters that can be plugged into the "Dragonfly_Run Urban Weather Generator" component.
"""

ghenv.Component.Name = "Dragonfly_Boundary Layer Parameters"
ghenv.Component.NickName = 'BndLayerPar'
ghenv.Component.Message = 'VER 0.0.02\nJUN_03_2018'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "00::UWG"
#compatibleDFVersion = VER 0.0.02\nMAY_13_2018
ghenv.Component.AdditionalHelpFromDocStrings = "0"


import scriptcontext as sc
import Grasshopper.Kernel as gh

#Dragonfly check.
initCheck = True
if not sc.sticky.has_key('dragonfly_release') == True:
    initCheck = False
    print "You should first let Drafgonfly fly..."
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "You should first let Drafgonfly fly...")
else:
    if not sc.sticky['dragonfly_release'].isCompatible(ghenv.Component): initCheck = False
    if sc.sticky['dragonfly_release'].isInputMissing(ghenv.Component): initCheck = False
    df_BndLayerPar = sc.sticky["dragonfly_BoundaryLayerPar"]

if initCheck == True:
    bndLayerPar = df_BndLayerPar(_dayBndLayerHeight_, _nightBndLayerHeight_, _inversionHeight_, 
        _circulationCoeff_, _exchangeCoeff_)
