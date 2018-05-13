# Dragonfly: A Plugin for Climate Modeling (GPL) started by Chris Mackey <chris@ladybug.tools> 
# This file is part of Dragonfly.
#
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Use this component to generate refernce EPW site parameters that can be plugged into the "Dragonfly_Run Urban Weather Generator" component.  If you are using standard files from the US Department of Energy, you should never need to use this component.  This component is onyl for when your data was recorded using non-standard means, such as an experiment that you have run in an actual urban canyon.
-
Provided by Dragonfly 0.0.02
    Args:
        avgObstacleHeight_: A number that represents the height in meters of objects that obstruct the view to the sky at the weather station site, such as trees and buildings.  The default is set to 0.1.
        vegetationCoverage_: A number between 0 and 1 that represents that fraction of the reference EPW site that is covered in grass. If nothing is input here, a defailt of 0.9 will be used.
        tempMeasureHeight_: A number that represents the height in meters at which temperature is measured on the weather station.  The default is set to 10 meters as this is the standard measurement height for US Department of Energy EPW files.
        windMeasureHeight_: A number that represents the height in meters at which wind speed is measured on the weather station.  The default is set to 10 meters as this is the standard measurement height for US Department of Energy EPW files.
    Returns:
        epwSitePar: Refernce EPW site parameters that can be plugged into the "Dragonfly_Run Urban Weather Generator" component.
"""

ghenv.Component.Name = "Dragonfly_Reference EPW Parameters"
ghenv.Component.NickName = 'RefEPWPar'
ghenv.Component.Message = 'VER 0.0.02\nMAY_13_2018'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "01::UWG"
#compatibleDFVersion = VER 0.0.02\nMAY_13_2018
ghenv.Component.AdditionalHelpFromDocStrings = "5"

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
    df_RefEpwPar = sc.sticky["dragonfly_RefEpwPar"]

if initCheck == True:
    epwSitePar = df_RefEpwPar(avgObstacleHeight_, vegetationCoverage_, tempMeasureHeight_, 
        windMeasureHeight_)
    print epwSitePar
