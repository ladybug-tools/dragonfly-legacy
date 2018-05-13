# Dragonfly: A Plugin for Climate Modeling (GPL) started by Chris Mackey <chris@ladybug.tools> 
# This file is part of Dragonfly.
#
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Use this component to generate a city for an Urban Weather Generator simulation using building typologies.  These building typologies can generated with the "Dragonfly_UWG Building Typology" component.
_
The ouput of this component can be plugged into the 'Dragonfly_Run Urban Weather Generator' component in order to morph a rural/airport weather file to reflect the urban conditions input to this component.
-
Provided by Dragonfly 0.0.02
    Args:
        _buildingTypologies: One or more building typologies from the "Dragonfly_UWG Building Typology" component.
        _terrainBrep: A brep or list of breps that represent the the terrian beneath the urban area, including all pavement, grass areas, and the region beneath the buildings.  Note that this  brep should just reflect the surface of the terrain and should not be a closed solid.  The outer limits of this surface will be used to determine the density of the urban area so including surface area that extends well beyond the buildings will cause the simulation to inacurately model the density.
        treesOrCoverage_: Either a list of closed breps that represent the tree canopies of the urban area or a number between 0 and 1 that represents that fraction of tree coverage over the entire urban area (including those over both roofs and pavement).  If breps are input, they will be projected to the ground plane to compute the area of tree coverage as seen from above.  Thus, simpler tree geometry like boxes that represent the tree canopies are preferred.  If nothing is input here, it will be assumed that there are no trees in the urban area.
        grassOrCoverage_: Either a list of surfaces that represent the grassy surfaces of the urban area or a number between 0 and 1 that represents that fraction of grass coverage over the entire urban area (including both green roofs and ground vegetation). If surfaces are input here, they should be coplanar with the terrainBrep. If nothing is input here, it will be assumed that there is no grass in the urban area.
        --------------------: ...
        _trafficPar: Traffic parameters from the "Dragonfly_Traffic Parameters" component.  This input is required as anthropogenic heat from traffic can significantly affect urban climate and varies widely between commerical, residential, and industrial districts.
        vegetationPar_: An optional set of vegetation parameters from the "Dragonfly_Vegetation Parameters" component.  If no vegetation parameters are input here, the Dragonfly will use a vegetation albedo of 0.25, tree latent fraction of 0.7, and grass latent fraction of 0.6.  Furthermore, Dragonfly will attempt to determine the months in which vegetation is active by looking at the average monthly temperatures in the EPW file.
        pavementPar_: An optional set of pavement parameters from the "Dragonfly_Pavement Parameters" component.  If no paramters are plugged in here, it will be assumed that all pavement is asphalt.
        --------------------: ...
        _runIt: Set to 'True' to run the component and generate the UWG city from the connected inputs.
    Returns:
        readMe!: A report of the key variables extraced from the input geometry.
        ----------------: ...
        UWGCity: A city that can be plugged into the "Dragonfly_Run Urban Weather Generator" component.
        ----------------: ...
        treeFootprints: If tree breps are connected, this is the tree geometry as projected into the world XY plane.  This is used to determine the tree coverage of the pavement.
        terrainSrf: The terrian brep projected into the world XY plane.  The area of this surface is used to determine all other geometric parameters.
"""

ghenv.Component.Name = "Dragonfly_UWG City"
ghenv.Component.NickName = 'UWGcity'
ghenv.Component.Message = 'VER 0.0.02\nMAY_12_2018'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "01::UWG"
#compatibleDFVersion = VER 0.0.02\nMAY_12_2018
ghenv.Component.AdditionalHelpFromDocStrings = "2"


import scriptcontext as sc
import Grasshopper.Kernel as gh

#Dragonfly check.
initCheck = True
if not sc.sticky.has_key('dragonfly_release') == True:
    initCheck = False
    print "You should first let Drafgonfly fly..."
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "You should first let Drafgonfly fly...")
else:
    try:
        if not sc.sticky['dragonfly_release'].isCompatible(ghenv.Component): initCheck = False
        if sc.sticky['dragonfly_release'].isInputMissing(ghenv.Component): initCheck = False
        df_City = sc.sticky["dragonfly_City"]
        df_Terrain = sc.sticky["dragonfly_Terrain"]
    except:
        initCheck = False
        warning = "You need a newer version of Drafgonfly to use this compoent." + \
        "Use updateDrafgonfly component to update userObjects.\n" + \
        "If you have already updated userObjects drag Drafgonfly_Drafgonfly component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)

if initCheck == True and _runIt == True:
    terrain, terrainSrf = df_Terrain.fromGeometry(_terrainBrep)
    
    UWGCity = df_City.from_typologies(_buildingTypologies, terrain,
        _trafficPar, treesOrCoverage_, grassOrCoverage_, vegetationPar_, pavementPar_)
    
    print UWGCity

