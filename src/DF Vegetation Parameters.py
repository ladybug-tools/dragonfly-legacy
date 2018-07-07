# Dragonfly: A Plugin for Climate Modeling (GPL) started by Chris Mackey <chris@ladybug.tools> 
# This file is part of Dragonfly.
#
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Use this component to generate vegetation parameters that can be plugged into the "DF UWG City" component.
-
Provided by Dragonfly 0.0.02
    Args:
        _albedo_: A number between 0 and 1 that represents the ratio of reflected radiation from
            vegetated surfaces to incident radiation upon them.  If no value is input here, the
            UWG will assume a typical vegetation albedo of 0.25.  This number may be higher for
            bright green grass or lower for coniferous trees.
        _start_month_: An integer from 1 to 12 that represents the first month after winter when
            vegetation begins to participate in the energy balance of the urban area (though
            photosynthesis and evapotranspiration).  If no value is input here, Dragonfly will
            attempt to guess this parameter by calculating the first month that average outdoor
            temperatures are above 10 C in the EPW file that you are altering.
        _end_month_: An integer from 1 to 12 that represents the last month after summer that
            vegetation participates in the energy balance of the urban area (though photosynthesis
            and evapotranspiration).If no value is input here, Dragonfly will attempt to guess this
            parameter by calculating the last month that average outdoor temperatures are above 10 C
            in the EPW file that you are altering.
        _tree_latent_: A number between 0 and 1 that represents the the fraction of absorbed 
            solar energy by trees that is given off as latent heat (evapotranspiration). Currently, 
            this does not affect the moisture balance in the UWG but it will affect the temperature.
            If no value is input here, a typical value of 0.7 will be assumed.
        _grass_latent_: A number between 0 and 1 that represents the the fraction of absorbed solar 
            energy by grass that is given off as latent heat (evapotranspiration). Currently, 
            this does not affect the moisture balance in the UWG but it will affect the temperature.
            If no value is input here, a typical value of 0.5 will be assumed.
    Returns:
        vegetation_par: Vegetation parameters that can be plugged into the "DF UWG City" component.
"""

ghenv.Component.Name = "DF Vegetation Parameters"
ghenv.Component.NickName = 'VegPar'
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
    df_VegetationPar = sc.sticky["dragonfly_VegetationPar"]

if init_check == True:
    vegetation_par = df_VegetationPar(_albedo_, _start_month_, _end_month_, _tree_latent_, _grass_latent_)




