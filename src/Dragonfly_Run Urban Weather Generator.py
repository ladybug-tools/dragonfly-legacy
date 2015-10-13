# Run the Urban Weather Generator
#
# Dragonfly: A Plugin for Climate Data Generation (GPL) started by Chris Mackey
# 
# This file is part of Dragonfly.
# 
# Copyright (c) 2015, Chris Mackey <Chris@MackeyArchitecture.com> 
# Dragonfly is free software; you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published 
# by the Free Software Foundation; either version 3 of the License, 
# or (at your option) any later version. 
# 
# Dragonfly is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details.
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
        _UWGParameters: A list of parameters from one of the 'Dragonfly_UWG Parameters' components.  This list describes describes the characteristics of the urban street canyon for which an epw file will be produced.
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
ghenv.Component.Message = 'VER 0.0.01\nOCT_12_2015'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "2 | GenerateUrbanClimate"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import scriptcontext as sc
import Rhino as rc
import os

from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh


def checkTheInputs(df_textGen, lb_preparation):
    # Set a warning variable.
    w = gh.GH_RuntimeMessageLevel.Warning
    
    #Check to be sure that the EPW file is on the person's system.
    checkData1 = True
    if not os.path.isfile(_epwFile):
        checkData1 = False
        warning1 = "Could not find the connected _epwFile on your system. \n Make sure that you have the file on your system at this address:"
        warning2 = _epwFile
        print warning1
        print warning2
        ghenv.Component.AddRuntimeMessage(w, warning1)
        ghenv.Component.AddRuntimeMessage(w, warning2)
    
    #Check to be sure that the _UWGParameters are valid.
    checkData2 = True
    if not _UWGParameters.startswith('<?xml version="1.0" encoding="utf-8"?>\n<xml_input>'):
        checkData2 = False
        warning = "The connected _UWGParameters are not valid parameters fromt one of the 'Dragonfly_UWG Parameters' components."
        print warning
        ghenv.Component.AddRuntimeMessage(w, warning)
    
    #Check if there is a workingDir connected and, if not set a default. Create the directory on the person's system. 
    checkData3 = True
    if _workingDir_: workingDir = _workingDir_
    else: workingDir = sc.sticky["Ladybug_DefaultFolder"] + 'unnamed\\UWG\\'
    if not os.path.exists(workingDir):
        try:
            os.makedirs(workingDir)
        except:
            checkData3 = False
            warning =  'cannot create the working directory as: ', workingDir + \
                  '\nPlease set a new working directory'
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    print 'Current working directory is set to: ' + workingDir
    
    #Set a default filename.
    if _xmlFileName_:
        if _xmlFileName_.endswith('.xml'): xmlFileName = _xmlFileName_
        else: xmlFileName = _xmlFileName_ + '.xml'
    else: xmlFileName = 'unnamed.xml'
    
    #Check the epwSitePar_ and, if there are none, set default ones.
    checkData4 = True
    if len(epwSitePar_) != 0:
        try:
            epwSiteParString, tempHeight, windHeight = epwSitePar_
        except:
            checkData4 = False
            warning =  'epwSitePar_ is not valid.'
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    else:
        epwSiteParString = df_textGen.defaultRefSitePar
        tempHeight = 10
        windHeight = 10
    
    #Check the boundLayerPar_ and, if there are none, leave the default ones.
    checkData5 = True
    if boundLayerPar_:
        if not boundLayerPar_.startswit('    <daytimeBLHeight>'):
            checkData5 = False
            warning =  'boundLayerPar_ is not valid.'
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    
    #Check the analysisPeriod and, if there is none, run the simulation for the whole year.
    if analysisPeriod_:
        stMonth, stDay, stHour, endMonth, endDay, endHour = lb_preparation.readRunPeriod(analysisPeriod)
        startDOY = int(lb_preparation.getJD(stMonth, stDay))
        endDOY = int(lb_preparation.getJD(endMonth, endDay))
        simDuration = endDOY - startDOY
        stHOY = lb_preparation.date2Hour(stMonth, stDay, 1)
    else:
        stMonth = 1
        stDay = 1
        simDuration = 365
        stHOY = 1
    analysisPeriodStr = '    <simuStartMonth>' + str(stMonth) + '</simuStartMonth>\n' +\
                        '    <simuStartDay>' + str(stDay) + '</simuStartDay>\n' +\
                        '    <simuDuration>' + str(simDuration) + '</simuDuration>\n'
    
    #Grab default untouchable parameters.
    ### Note that I only say they are 'untochable' because there is no documentation about them on the UWG site the last time that I checked:
    # http://urbanmicroclimate.scripts.mit.edu/uwg_parameters.php
    untouchablePar = df_textGen.untouchablePar
    
    #Do a final check of everything and, if it's good, project any goemtry that needs to be projected in order to extract relevant parameters.
    checkData = False
    if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True  and checkData5 == True:
        checkData = True
    
    return checkData, workingDir, xmlFileName, _epwFile, epwSiteParString, tempHeight, windHeight, boundLayerPar_, analysisPeriodStr, stHOY, untouchablePar


def main(workingDir, xmlFileName, epwFile, epwSiteParString, tempHeight, windHeight, boundLayerPar, analysisPeriodStr, stHOY, untouchablePar, df_textGen, lb_preparation):
    #Extract the latitude, longitude, and start temperature for the analysis period fromt he EPW file.
    locationData = lb_preparation.epwLocation(epwFile)
    latitude = locationData[1]
    longitude = locationData[2]
    
    dbTemp = []
    epwfile = open(epwFile,"r")
    lnum = 1 # line number
    for line in epwfile:
        if lnum > 8:
            dbTemp.append(float(line.split(',')[6]))
        lnum += 1
    epwfile.close()
    startTemp = dbTemp[stHOY]
    
    #Assemble the reference site string.
    refSiteStr = '  <referenceSite>\n'
    refSiteStr = refSiteStr + '    <latitude>' + str(latitude) + '</latitude>\n'
    refSiteStr = refSiteStr + '    <longitude>' + str(longitude) + '</longitude>\n'
    refSiteStr = refSiteStr + epwSiteParString
    refSiteStr = refSiteStr + '  </referenceSite>\n'
    
    #Assemble the parameter string.
    paramStr = '  <parameter>\n'
    paramStr = paramStr + '    <tempHeight>' + str(tempHeight) + '</tempHeight>\n'
    paramStr = paramStr + '    <windHeight>' + str(windHeight) + '</windHeight>\n'
    paramStr = paramStr + untouchablePar
    paramStr = paramStr + analysisPeriodStr
    paramStr = paramStr + '  </parameter>\n'
    
    #Bring the whole string together.
    xmlStr = _UWGParameters + refSiteStr + paramStr + '</xml_input>'
    
    #Replace the starting temperatures in the _UWGParameters with the starting temperature of the EPWFile.
    xmlStrSplit = xmlStr.split('setByEPW')
    newXmlStr = xmlStrSplit[0]
    for count, string in enumerate(xmlStrSplit):
        if count != 0: newXmlStr = newXmlStr + str(startTemp) + string
    xmlStr = newXmlStr
    
    #Write the string into an XML file.
    xmlFilePath = workingDir + xmlFileName
    xmlFile = open(xmlFilePath, "w")
    xmlFile.write(xmlStr)
    xmlFile.close()
    
    #If the user has selected to run the UWG, run the XML and EPW through the UWG.
    #if runUWG_:
    #    #Copy the original epwfile into the direcotry.
    #    epwFileName = 
    #    if 
    
    
    return xmlStr, xmlFilePath, None



#Check to be sure that Dragonfly is flying.
initCheck = False
if sc.sticky.has_key("dragonfly_release"):
    df_textGen = sc.sticky["dragonfly_UWGText"]()
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    initCheck = True
else:
    if not sc.sticky.has_key("ladybug_release"):
        warning = "You need to let Ladybug fly to use this component."
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    if not sc.sticky.has_key("dragonfly_release"):
        warning = "You need to let Dragonfly fly to use this component."
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)



if initCheck == True and _writeXML == True and _epwFile and _UWGParameters:
    checkData, workingDir, xmlFileName, epwFile, epwSiteParString, tempHeight, windHeight, boundLayerPar, analysisPeriodStr, stHOY, untouchablePar = checkTheInputs(df_textGen, lb_preparation)
    if checkData == True:
        xmlText, xmlFileAddress, epwFileAddress = main(workingDir, xmlFileName, epwFile, epwSiteParString, tempHeight, windHeight, boundLayerPar, analysisPeriodStr, stHOY, untouchablePar, df_textGen, lb_preparation)

