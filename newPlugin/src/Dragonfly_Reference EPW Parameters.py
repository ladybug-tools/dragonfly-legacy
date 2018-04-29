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
        pavementConstr_: A text string representing the construction of the uban pavement.  This construction can be either from the OpenStudio Library (the "Honeybee_Call from EP Construction Library" component) or it can be a custom construction from the "Honeybee_EnergyPlus Construction" component.  If no construction is input here, a default construction for asphalt will be used for simulating all paved areas of the urban neighborhood.
        vegetationCoverage_: A number between 0 and 1 that represents that fraction of the _pavementBrep that is covered in grass. If nothing is input here, it will be assumed that half of the EPW site is covered in grass.
        inclinationAngle_: A number between 0 and 1 that that represents the dinensionless inclination angle of the ground surfaces of the reference site:
            _
            0 = Perfectly vertical surface  (like a wall)
            0.5 = Sloped surfacece that is 45 degrees from the horizontal.
            1 = Perfectly horizontal surface (like a flat roof)
        tempMeasureHeight_: A number that represents the height in meters at which temperature is measured on the weather station.  The default is set to 10 meters as this is the standard measurement height for UD Department of Energy EPW files.
        windMeasureHeight_: A number that represents the height in meters at which wind speed is measured on the weather station.  The default is set to 10 meters as this is the standard measurement height for UD Department of Energy EPW files.
    Returns:
        pavementPar: A list of refernce EPW site parameters that can be plugged into the "Dragonfly_Run Urban Weather Generator" component.
"""

ghenv.Component.Name = "Dragonfly_Reference EPW Parameters"
ghenv.Component.NickName = 'RefEPWPar'
ghenv.Component.Message = 'VER 0.0.02\nAPR_29_2018'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "01::UWG"
ghenv.Component.AdditionalHelpFromDocStrings = "5"


