# Dragonfly: A Plugin for Climate Modeling (GPL) started by Chris Mackey <chris@ladybug.tools> 
# This file is part of Dragonfly.
#
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Use this component to morph a rural or airport EPW to reflect the conditions within an urban street canyon.  The properties of this urban street canyon are specified in the connected _UWGCity, which should come from one of the 'Dragonfly_UWG Ccity' component.
_
For definitions of the inputs of the Urban Weather Generator, please see this page of the MIT Urban Microclimate Group:
http://urbanmicroclimate.scripts.mit.edu/uwg_parameters.php#ref
_
For a full list of publications on the Urban Weather Generator, please see this page of the MIT Urban Microclimate Group:
http://urbanmicroclimate.scripts.mit.edu/publications.php
-
Provided by Dragonfly 0.0.02
    Args:
        _epwFile: An .epw file path on your system as a text string.  This is the rural or airport file that will be morphed to reflect the climate conditions within an urban canyon.
        _UWGCity: A list of parameters from one of the 'Dragonfly_UWG Parameters' components.  This list describes describes the characteristics of the urban street canyon for which an epw file will be produced.
        _analysisPeriod_: An optional analysis period from the 'Ladybug_Analysis Period' component.  If no Analysis period is given, the Urban Weather Generator will be run for the enitre year.
        _simTimestep_: A number representing the timestep at which the simulation is run in seconds.  The default is set to 300 seconds (5 minutes).  Note that all restuls are still reported on an hour-by-hour basis in the otuput EPW and this only changes how the calculation is run in the UWG.
        --------------------: ...
        epwSitePar_: An optional list of Reference EPW Site Parameters from the "Dragonfly_Reference EPW Site Par" component.
        boundLayerPar_: Optional Boundary Layer Parameters from the "Dragonfly_Boundary Layer Par" component.
        --------------------: ...
        _runUWG: Set to "True" to have the component morph the EPW using the Urban Weather Generator (UWG) and the attached UWGCity.
        --------------------: ...
        _workingDir_: An optional working directory to a folder on your system, into which the morphed EPW files will be written.  The default will write these files in the folder that contains the connected epwFile_.
        _epwFileName_: An optional text string which will be used to name of your morphed EPW files.  Change this to aviod over-writing results of previous runs of the Urban Weather Generator.
    Returns:
        readMe!: ...
        ---------------: ...
        epwFileAddress: The file path of the morphed EPW file that has been generated on your machine.  This only happens when you set "runUWG_" to "True."
        ---------------: ...
        uwgObject: The python UWG object that can be edited and simulated using the methods on the UWG.
"""

ghenv.Component.Name = "Dragonfly_Run Urban Weather Generator"
ghenv.Component.NickName = 'RunUWG'
ghenv.Component.Message = 'VER 0.0.02\nJUN_03_2018'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "00::UWG"
#compatibleDFVersion = VER 0.0.02\nMAY_25_2018
ghenv.Component.AdditionalHelpFromDocStrings = "1"


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


if initCheck == True and _runUWG == True:
    pass
