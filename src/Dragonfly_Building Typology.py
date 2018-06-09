# Dragonfly: A Plugin for Climate Modeling (GPL) started by Chris Mackey <chris@ladybug.tools> 
# This file is part of Dragonfly.
#
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Use this component to generate a default building typology to be used with the "Dragonfly_City" component.  The specific characteristcs of these typologies are based on the US Department of Energy (DoE) Building types.
-
Provided by Dragonfly 0.0.02
    Args:
        _geo: A list of closed breps that represent the geometry of the buildings in the urban area that fall under this typology.
        _program: One of the 16 building programs listed from the "Dragonfly_Bldg Programs" component.  The following options are available:
            FullServiceRestaurant
            Hospital
            LargeHotel
            LargeOffice
            MediumOffice
            MidRiseApartment
            OutPatient
            PrimarySchool
            QuickServiceRestaurant
            SecondarySchool
            SmallHotel
            SmallOffice
            StandAloneRetail
            StripMall
            SuperMarket
            Warehouse
        _age: An integer that sets the age of the buildings represented by this typology.  This is used to determine what constructions make up the walls, roofs, and windows based on international building codes over the last several decades.  Choose from the following options:
            Pre-1980's
            1980's-Present
            New Construction
        _flr_to_flr_: A number that sets the average distance between floors for the building typology.  This will be used to compute the total floor area of the building, which ultimately determines the influence that the typology has on the urban microclimate.
        _glz_ratio_: A number between 0 and 1 that represents the fraction of the exterior wall surface occupied by windows.  If no value is input here, a default will be used that comes from the DoE building template connected to the _bldgProgram and _bldgAge.
        _fract_canyon_: A number between 0 and 1 that represents the fraction of the building's waste heat from air conditioning that gets rejected into the urban canyon (as opposed to through rooftop equipment or into a ground source loop).  The default is set to 0.5.
        _run: Set to "True" to run the component and generate a building typology.
    Returns:
        readMe!: ...
        -------------: ...
        DF_typology: A Dragonfly building typology object that can be plugged into the "Dragonfly_City" component.
        -------------: ...
        footprints: The building geometry as projected onto the world XY plane.  This is used to determine the site coverage ratio and to perform a weighted-average of the building heights.
        floors: A list of breps representing the floors of the typology.
        facades: A list of breps representing the exposed facade area of the building breps.  These will be used to calculate the facade-to-site ratio.
"""

ghenv.Component.Name = "Dragonfly_Building Typology"
ghenv.Component.NickName = 'BldgTypology'
ghenv.Component.Message = 'VER 0.0.02\nJUN_03_2018'
ghenv.Component.Category = "Dragonfly"
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
    df_BuildingTypology = sc.sticky["dragonfly_BuildingTypology"]

if init_check == True and _run == True:
    DF_typology, footprints, floors, facades = df_BuildingTypology.from_geometry(_geo, 
        _program, _age, _flr_to_flr_, _glz_ratio_, _fract_canyon_)