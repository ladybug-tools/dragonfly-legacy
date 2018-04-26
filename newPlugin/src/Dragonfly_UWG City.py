# Dragonfly: A Plugin for Climate Modeling (GPL) started by Chris Mackeu
# This file is part of Dragonfly.
#
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Use this component to generate paremeters for an Urban Weather Generator model using urban typologies and the ratios of each typology within the urban area.  These building typologies can generated with the "Dragonfly_UWG Building Typology" component.
_
The ouput of this component can be plugged into the 'Dragonfly_Run Urban Weather Generator' component in order to morph a rural/airport weather file to reflect the urban conditions input to this component.
-
Provided by Dragonfly 0.0.01
    Args:
        _buildingTypologies: One or more building typologies from either the "Dragonfly_Building Typology from HBZone" or the "Dragonfly_Building Typology from Parameters" component.
        _pavementBrep: A list of breps that represent the paved portion of the urban area.  Note that this input brep should just reflect the surface of the terrain and should not be a solid.  Also note that this surface should be coninuous beneath the ground of the HBZones and should only be interrupted in grassy areas where the user intends to connect up such grassy surfaces to the "grassBrep_" input below.  The limits of this surface will be used to determine the density of the urban area so including a surface that extends well beyond the area where the HBZones are will cause the simulation to inacurately model the density.
        treesOrCoverage_: Either a list of breps that represent the trees of the urban area that is being modeled or a number between 0 and 1 that represents that fraction of tree coverage in the urban area.  If breps are input, they will be projected to the ground plane to compute the area of tree coverage as seen from above.  Thus, simpler tree geometry like boxes that represent the tree canopies are preferred.  If nothing is input here, it will be assumed that there are no trees in the urban area.
        grassOrCoverage_: Either a list of breps that represent the grassy ground surfaces of the urban area or a number between 0 and 1 that represents that fraction of the _pavementBrep that is covered in grass. If nothing is input here, it will be assumed that there is no grass in the urban area.
        --------------------: ...
        vegetationPar_: An optional list of Vegetation Parameters from the "Dragonfly_Vegetation Parameters" component.  If no vegetation parameters are input here, the UWG will attempt to determine the months in which vegetation is active by looking at the average monthly temperatures in the EPW file.
        nonBldgHeat_: An number that represents the anthropogenic heat generated in the urban canyon in Watts per square meter of pavement (W/m2).  This is specifcally the heat that DOES NOT originate from buildings and mostly includes heat originating from automobiles, street lighting, and human metabolism.  Typical values are:
        _
        10 W/m2 = A commercial area in Singapore
        4 W/m2 = A residential area in Singapore
        8 W/m2 = A typical part of Toulouse, France.
        _
        Values are available for some cities by Sailor: http://onlinelibrary.wiley.com/doi/10.1002/joc.2106/abstract
        _runIt: Set to 'True' to run the component and generate UWG parameters from the connected inputs.
    Returns:
        readMe!: A report of the key variables extraced from the input geometry.
        ----------------: ...
        UWGCity: A city that can be plugged into the "Dragonfly_Run Urban Weather Generator" component.
        ----------------: ...
        joinedBldgs: The boolean union of adjacent buildings.  This is done to ensure that a correct facade-to-site ratio is computed.
        bldgFootprints: The building geometry as projected onto the world XY plane.  This is used to determine the site coverage ratio and to perform a weighted-average of the building heights.
        treeFootprints: If tree breps are connected, this is the tree geometry as projected into the world XY plane.  This is used to determine the tree coverage of the pavement.
        pavementSrf: The pavement terrian as projected into the world XY plane.  The area of this surface along with the grass surface is used to determine all other geometric parameters.
        grassSrf: The grass terrian as projected into the world XY plane.  The area of this surface along with the pavement surface is used to determine all other geometric parameters.
"""

ghenv.Component.Name = "Dragonfly_UWG City"
ghenv.Component.NickName = 'City'
ghenv.Component.Message = 'VER 0.0.01\nOCT_29_2016'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "01::UWG"
ghenv.Component.AdditionalHelpFromDocStrings = "2"



