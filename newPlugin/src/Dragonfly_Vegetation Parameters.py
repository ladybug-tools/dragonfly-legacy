# Dragonfly: A Plugin for Climate Modeling (GPL) started by Chris Mackey <chris@ladybug.tools> 
# This file is part of Dragonfly.
#
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Use this component to generate vegetation parameters that can be plugged into the "Dragonfly_UWG City" component.
-
Provided by Dragonfly 0.0.02
    Args:
        _vegetationAlbedo_: A number between 0 and 1 that represents the ratio of reflected radiation from vegetated surfaces to incident radiation upon them.  If no value is input here, the UWG will assume a typical vegetation albedo of 0.25.  This number may be higher for bright green grass or lower for coniferous trees.
        _vegStartMonth_: An integer from 1 to 12 that represents the first month after winter when vegetation begins to participate in the energy balance of the urban area (though photosynthesis and evapotranspiration).  If no value is input here, Dragonfly will attempt to guess this parameter by calculating the first month that average outdoor temperatures are above 10 C in the EPW file that you are altering.
        _vegEndMonth_: An integer from 1 to 12 that represents the last month after summer that vegetation participates in the energy balance of the urban area (though photosynthesis and evapotranspiration).If no value is input here, Dragonfly will attempt to guess this parameter by calculating the last month that average outdoor temperatures are above 10 C in the EPW file that you are altering.
    Returns:
        vegetationPar: Vegetation parameters that can be plugged into the "Dragonfly_UWG City" component.
"""

ghenv.Component.Name = "Dragonfly_Vegetation Parameters"
ghenv.Component.NickName = 'vegPar'
ghenv.Component.Message = 'VER 0.0.02\nMAY_20_2018'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "01::UWG"
#compatibleDFVersion = VER 0.0.02\nMAY_20_2018
ghenv.Component.AdditionalHelpFromDocStrings = "4"


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
    df_VegetationPar = sc.sticky["dragonfly_VegetationPar"]

if initCheck == True:
    vegetationPar = df_VegetationPar(_vegetationAlbedo_, _vegStartMonth_, _vegEndMonth_)
    print vegetationPar




