# Dragonfly: A Plugin for Climate Modeling (GPL) started by Chris Mackey <chris@ladybug.tools> 
# This file is part of Dragonfly.
#
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Use this component to generate a default building typology to be used with the "DF City" component.  The specific characteristcs of these typologies are based on the US Department of Energy (DoE) Building types.
-
Provided by Dragonfly 0.0.03
    Args:
        _typology: A building typology from the "DF Building Typology" component.
        _glz_ratio_: A number between 0 and 1 that represents the fraction of the exterior wall surface occupied by windows.  If no value is input here, a default will be used that comes from the DoE building template connected to the _bldgProgram and _bldgAge.
        _shgc_: A number between 0 and 1 that represents the solar heat gain coefficient (SHGC) of the typology's windows.
        _wall_alb_: A number between 0 and 1 that represents the exterior albedo of the typology's walls.
        _roof_alb_: A number between 0 and 1 that represents the exterior albedo of the typology's roofs.
        _roof_veg_: A number between 0 and 1 that represents the fraction of the typology's roofs covered in vegetation.
    Returns:
        readMe!: ...
        typology: A Dragonfly building typology object that can be plugged into the "DF City" component.
"""

ghenv.Component.Name = "DF Edit Typology Envelope"
ghenv.Component.NickName = 'TypeEnvelope'
ghenv.Component.Message = 'VER 0.0.03\nMAR_25_2020'
ghenv.Component.Category = "DF-Legacy"
ghenv.Component.SubCategory = "1 | Urban Weather"
#compatibleDFVersion = VER 0.0.02\nMAY_12_2018
ghenv.Component.AdditionalHelpFromDocStrings = "2"

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

if init_check == True and _typology is not None:
     _typology.glz_ratio = _glz_ratio_
     _typology.shgc = _shgc_
     _typology.wall_albedo = _wall_alb_
     _typology.roof_albedo = _roof_alb_
     _typology.roof_veg_fraction = _roof_veg_
     typology = _typology