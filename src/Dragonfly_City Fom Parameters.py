# Dragonfly: A Plugin for Climate Modeling (GPL) started by Chris Mackey <chris@ladybug.tools> 
# This file is part of Dragonfly.
#
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Use this component to generate a Dragonfly City object from numerical parameters like building height and site coverage ratio.
_
The ouput of this component can be plugged into the 'Dragonfly_Run Urban Weather Generator' component to morph a rural/airport weather file to reflect the urban climate.
-
Provided by Dragonfly 0.0.02
    Args:
        _avg_height: The average height of the buildings in the city in meters.
        _site_coverage:  A number between 0 and 1 that represents the fraction of the city terrain that
            the building footprints occupy.  It describes how close the buildings are to one another in the city.
        _facade_to_site: A number that represents the ratio of vertical urban surface area [walls] to 
            the total terrain area of the city.  This value can be greater than 1.
        _bldg_programs: A list of building programs that are within the urban area. 
            These should come from the "Dragonfly_Bldg Programs" component.
        _bldg_ages: A list of building ares that are within the urban area, which correspond with the _bldg_programs above.
            These should come from the "Dragonfly_Bldg Age" component.
        _bldg_ratios: A list of values between 0 and 1 that denote the fraction of the total floor area of the urban area
            occupied each of the _bldg_programs above.  The connected values should sum to 1.
        tree_coverage_: An number from 0 to 1 that defines the fraction of the entire urban area
            (including both pavement and roofs) that is covered by trees.  The default is set to 0.
        grass_coverage_: An number from 0 to 1 that defines the fraction of the entire urban area 
            (including both pavement and roofs) that is covered by grass/vegetation.  The default is set to 0.
        --------------------: ...
        _climate_zone: A text string representing the ASHRAE climate zone. (eg. 5A). This is used to set default
            constructions for the buildings in the city.
        _traffic_par: Traffic parameters from the "Dragonfly_Traffic Parameters" component.  This input is required
            as anthropogenic heat from traffic can significantly affect urban climate and varies widely between
            commerical, residential, and industrial districts.
        vegetation_par_: An optional set of vegetation parameters from the "Dragonfly_Vegetation Parameters" component.
            If no vegetation parameters are input here, the Dragonfly will use a vegetation albedo of 0.25 and Dragonfly
            will attempt to determine the months in which vegetation is active by looking at the average monthly temperatures
            in the EPW file.
        pavement_par_: An optional set of pavement parameters from the "Dragonfly_Pavement Parameters" component.  If no
            paramters are plugged in here, it will be assumed that all pavement is asphalt.
        --------------------: ...
        _run: Set to 'True' to run the component and generate the Dragonfly city from the connected inputs.
    Returns:
        read_me: ...
        ----------------: ...
        DF_city: A Drafongfly city objectthat can be plugged into the "Dragonfly_Run Urban Weather Generator" component.
"""

ghenv.Component.Name = "Dragonfly_City Fom Parameters"
ghenv.Component.NickName = 'CityFromPar'
ghenv.Component.Message = 'VER 0.0.02\nJUN_09_2018'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "1 | Urban Weather"
#compatibleDFVersion = VER 0.0.02\nMAY_12_2018
ghenv.Component.AdditionalHelpFromDocStrings = "3"


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
    df_City = sc.sticky["dragonfly_City"]
    df_Terrain = sc.sticky["dragonfly_Terrain"]
    df_Vegetation = sc.sticky["dragonfly_Vegetation"]

if initCheck == True and _run == True:
    assert len(_bldg_programs) == len(_bldg_ages) == len(_bldg_ratios), \
        'The lengths of _bldg_programs, _bldg_ages, and _bldg_ratios lists must match. Got legnths of {} {} {}'.format(
        len(_bldg_programs), len(_bldg_ages), len(_bldg_ratios))
    
    bldg_types = {}
    for i in range(len(_bldg_programs)):
        bldg_types[_bldg_programs[i] + ',' + _bldg_ages[i]] = _bldg_ratios[i]
    
    DF_city = df_City(_avg_height, _site_coverage, _facade_to_site, bldg_types, _climate_zone,
        _traffic_par, tree_coverage_, grass_coverage_, vegetation_par_, pavement_par_)

