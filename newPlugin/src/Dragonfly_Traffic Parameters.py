# Dragonfly: A Plugin for Climate Modeling (GPL) started by Chris Mackey <chris@ladybug.tools> 
# This file is part of Dragonfly.
#
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Use this component to generate traffic parameters that can be plugged into the "Dragonfly_UWG City" component.
-
Provided by Dragonfly 0.0.02
    Args:
        _sensibleHeat: A number that represents the sensible anthropogenic heat generated in the urban canyon in Watts per square meter of pavement (W/m2).  This is specifcally the heat that DOES NOT originate from buildings and mostly includes heat originating from automobiles, street lighting, and human metabolism.  Typical values are:
        _
        10 W/m2 = A commercial area in Singapore
        8 W/m2 = A typical mixed use part of Toulouse, France
        4 W/m2 = A residential area in Singapore
        _
        Values are available for some cities by Sailor: http://onlinelibrary.wiley.com/doi/10.1002/joc.2106/abstract
        _weekdaySched_: A list of 24 values between 0 and 1 that sets the fraction of the anthropogenic heat that occurs at each hour of the typical weekday.  If no value is input here, a typical schedule for a commercial area will be used:
                0.2,0.2,0.2,0.2,0.2,0.4,0.7,0.9,0.9,0.6,0.6,0.6,0.6,0.6,0.7,0.8,0.9,0.9,0.8,0.8,0.7,0.3,0.2,0.2
        _saturdaySched_: A list of 24 values between 0 and 1 that sets the fraction of the anthropogenic heat that occurs at each hour of the typical Saturday.  If no value is input here, a typical schedule for a commercial area will be used:
                0.2,0.2,0.2,0.2,0.2,0.3,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.6,0.7,0.7,0.7,0.7,0.5,0.4,0.3,0.2,0.2
        _sundaySched_: A list of 24 values between 0 and 1 that sets the fraction of the anthropogenic heat that occurs at each hour of the typical Sunday.  If no value is input here, a typical schedule for a commercial area will be used:
                0.2,0.2,0.2,0.2,0.2,0.3,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.3,0.3,0.2,0.2
    Returns:
        trafficPar: Traffic parameters that can be plugged into the "Dragonfly_UWG City" component.
"""

ghenv.Component.Name = "Dragonfly_Traffic Parameters"
ghenv.Component.NickName = 'trafficPar'
ghenv.Component.Message = 'VER 0.0.01\nAPR_29_2018'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "01::UWG"
#compatibleDFVersion = VER 0.0.02\nMAY_08_2018
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
    df_TrafficPar = sc.sticky["dragonfly_TrafficPar"]

if initCheck == True:
    trafficPar = df_TrafficPar(_sensibleHeat, _weekdaySched_, _saturdaySched_,
        _sundaySched_)
    print trafficPar