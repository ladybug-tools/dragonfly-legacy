# Dragonfly: A Plugin for Climate Modeling (GPL) started by Chris Mackey <chris@ladybug.tools> 
# This file is part of Dragonfly.
#
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Use this component to generate a building typology to be used with the "DF City" component from footprint geometry.
-
Provided by Dragonfly 0.0.02
    Args:
        _geo: A list of surface breps that represent the footprint geometry of the buildings in the urban area that fall under this typology.
        _num_floors: A float number (greater than 1) that represents the average number of stories of the
                buildings in the typology.
        _program: One of the 16 building programs listed from the "DF Bldg Programs" component.  The following options are available:
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
        _fract_canyon_: A number between 0 and 1 that represents the fraction of the building's waste heat from air conditioning that gets rejected into the urban canyon (as opposed to through rooftop equipment or into a ground source loop).  The default is set to 0.5.
        _run: Set to "True" to run the component and generate a building typology.
    Returns:
        read_me: ...
        -------------: ...
        typology: A Dragonfly building typology object that can be plugged into the "DF City" component.
        -------------: ...
        perim_crvs: A list of curves showing the exterior-exposed edges of the footprints.
"""

ghenv.Component.Name = "DF Typology from Footprints"
ghenv.Component.NickName = 'FootprintTypology'
ghenv.Component.Message = 'VER 0.0.02\nJUN_13_2018'
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
    typology, perim_crvs = df_BuildingTypology.from_footprint_geometry(_geo, _num_floors,
        _program, _age, _flr_to_flr_, _fract_canyon_)