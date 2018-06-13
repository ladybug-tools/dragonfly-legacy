# Dragonfly: A Plugin for Climate Modeling (GPL) started by Chris Mackey <chris@ladybug.tools> 
# This file is part of Dragonfly.
#
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Use this component to generate traffic parameters that can be plugged into the "DF UWG City" component.
-
Provided by Dragonfly 0.0.02
    Args:
        _sensible_heat: A number that represents the sensible anthropogenic heat generated in the urban canyon in Watts per square meter of pavement (W/m2).  This is specifcally the heat that DOES NOT originate from buildings and mostly includes heat originating from automobiles, street lighting, and human metabolism.  Typical values are:
        _
        10 W/m2 = A commercial area in Singapore
        8 W/m2 = A typical mixed use part of Toulouse, France
        4 W/m2 = A residential area in Singapore
        _
        Values are available for some cities by Sailor: http://onlinelibrary.wiley.com/doi/10.1002/joc.2106/abstract
        _weekday_sch_: A list of 24 values between 0 and 1 that sets the fraction of the anthropogenic heat that occurs at each hour of the typical weekday.  If no value is input here, a typical schedule for a commercial area will be used:
                0.2,0.2,0.2,0.2,0.2,0.4,0.7,0.9,0.9,0.6,0.6,0.6,0.6,0.6,0.7,0.8,0.9,0.9,0.8,0.8,0.7,0.3,0.2,0.2
        _sat_sch_: A list of 24 values between 0 and 1 that sets the fraction of the anthropogenic heat that occurs at each hour of the typical Saturday.  If no value is input here, a typical schedule for a commercial area will be used:
                0.2,0.2,0.2,0.2,0.2,0.3,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.6,0.7,0.7,0.7,0.7,0.5,0.4,0.3,0.2,0.2
        _sun_sch_: A list of 24 values between 0 and 1 that sets the fraction of the anthropogenic heat that occurs at each hour of the typical Sunday.  If no value is input here, a typical schedule for a commercial area will be used:
                0.2,0.2,0.2,0.2,0.2,0.3,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.3,0.3,0.2,0.2
    Returns:
        traffic_par: Traffic parameters that can be plugged into the "DF UWG City" component.
"""

ghenv.Component.Name = "DF Traffic Parameters"
ghenv.Component.NickName = 'TrafficPar'
ghenv.Component.Message = 'VER 0.0.02\nJUN_12_2018'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "1 | Urban Weather"
#compatibleDFVersion = VER 0.0.02\nMAY_20_2018
ghenv.Component.AdditionalHelpFromDocStrings = "5"

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
    df_TrafficPar = sc.sticky["dragonfly_TrafficPar"]

if init_check == True:
    traffic_par = df_TrafficPar(_sensible_heat, _weekday_sch_, _sat_sch_,
        _sun_sch_)