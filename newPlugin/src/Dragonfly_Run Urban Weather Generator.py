# Dragonfly: A Plugin for Climate Modeling (GPL) started by Chris Mackeu
# This file is part of Dragonfly.
#
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Use this component to morph a rural or airport EPW to reflect the conditions within an urban street canyon.  The properties of this urban street canyon are specified in the connected _UWGParemeters, which should come from one of the 'Dragonfly_UWG Parameters' components.
_
For definitions of the inputs of the Urban Weather Generator, please see this page of the MIT Urban Microclimate Group:
http://urbanmicroclimate.scripts.mit.edu/uwg_parameters.php#ref
_
For a full list of publications on the Urban Weather Generator, please see this page of the MIT Urban Microclimate Group:
http://urbanmicroclimate.scripts.mit.edu/publications.php
-
Provided by Dragonfly 0.0.01
    Args:
        _epwFile: An .epw file path on your system as a text string.  This is the rural or airport file that will be morphed to reflect the climate conditions within an urban canyon.
        _UWGCity: A list of parameters from one of the 'Dragonfly_UWG Parameters' components.  This list describes describes the characteristics of the urban street canyon for which an epw file will be produced.
        analysisPeriod_: An optional analysis period from the 'Ladybug_Analysis Period' component.  If no Analysis period is given, the Urban Weather Generator will be run for the enitre year.
        --------------------: ...
        epwSitePar_: An optional list of Reference EPW Site Parameters from the "Dragonfly_Reference EPW Site Par" component.
        boundLayerPar_: Optional Boundary Layer Parameters from the "Dragonfly_Boundary Layer Par" component.
        --------------------: ...
        _writeXML: Set to "True" to have the component take your connected UWGParemeters and write them into an XML file.  The file path of the resulting XML file will appear in the xmlFileAddress output of this component.  Note that only setting this to "True" and not setting the output below to "True" will not automatically run the XML through the Urban Weather Generator for you.
        runUWG_: Set to "True" to have the component run your XML and EPW files through the Urban Weather Generator (UWG).  This will ensure that a morphed EPW file path appears in the epwFileAddress output. Set to 2 if you want the analysis to run in background. This option is useful for parametric runs when you don't want to see command shells.
        --------------------: ...
        _workingDir_: An optional working directory to a folder on your system, into which your XML and morphed EPW files will be written.  The default will write these files in the folder that contains the connected epwFile_.  NOTE THAT DIRECTORIES INPUT HERE SHOULD NOT HAVE ANY SPACES OR UNDERSCORES IN THE FILE PATH.
        _xmlFileName_: An optional text string which will be used to name your XML and morphed EPW files.  Change this to aviod over-writing results of previous runs of the Urban Weather Generator.
    Returns:
        readMe!: ...
        xmlText: The text written into the XML file.
        xmlFileAddress: The file path of the XML file that has been generated on your machine.
        epwFileAddress: The file path of the morphed EPW file that has been generated on your machine.  This only happens when you set "runUWG_" to "True."
"""

ghenv.Component.Name = "Dragonfly_Run Urban Weather Generator"
ghenv.Component.NickName = 'RunUWG'
ghenv.Component.Message = 'VER 0.0.01\nOCT_29_2016'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "01::UWG"
ghenv.Component.AdditionalHelpFromDocStrings = "1"


