# This is the heart of Dragonfly
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
This component carries all of Dragonfly's main classes. Other components refer to these
classes to run the studies. Therefore, you need to let her fly before running the studies so the
classes will be copied to Rhinos shared space. So let her fly!

-
Dragonfly: A Plugin for Environmental Analysis (GPL) started by Chris Mackey
You should have received a copy of the GNU General Public License
along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.

@license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

Source code is available at: https://github.com/mostaphaRoudsari/ladybug

-
Provided by Dragonfly 0.0.01
    Args:
        defaultFolder_: Optional input for Dragonfly default folder.
                       If empty default folder will be set to C:\ladybug or C:\Users\%USERNAME%\AppData\Roaming\Ladybug\
    Returns:
        report: Current Dragonfly mood!!!
"""

ghenv.Component.Name = "Dragonfly_Dragonfly"
ghenv.Component.NickName = 'Dragonfly'
ghenv.Component.Message = 'VER 0.0.01\nSEP_13_2017'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "0 | Dragonfly"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc
import Grasshopper.Kernel as gh
import math
import shutil
import sys
import os
import System.Threading.Tasks as tasks
import System
import time
from itertools import chain
import datetime
import zipfile

PI = math.pi
rc.Runtime.HostUtils.DisplayOleAlerts(False)


class CheckIn():
    
    def __init__(self, defaultFolder, folderIsSetByUser = False):
        
        self.folderIsSetByUser = folderIsSetByUser
        self.letItFly = True
        
        if defaultFolder:
            # user is setting up the folder
            defaultFolder = os.path.normpath(defaultFolder) + os.sep
            
            # check if path has white space
            if (" " in defaultFolder):
                msg = "Default file path can't have white space. Please set the path to another folder." + \
                      "\nDragonfly failed to fly! :("
                print msg
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                sc.sticky["Dragonfly_DefaultFolder"] = ""
                self.letItFly = False
                return
            else:
                # create the folder if it is not created
                if not os.path.isdir(defaultFolder):
                    try: os.mkdir(defaultFolder)
                    except:
                        msg = "Cannot create default folder! Try a different filepath" + \
                              "\Dragonfly failed to fly! :("
                        print msg
                        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                        sc.sticky["Dragonfly_DefaultFolder"] = ""
                        self.letItFly = False
                        return
            
            # looks fine so let's set it up
            sc.sticky["Dragonfly_DefaultFolder"] = defaultFolder
            self.folderIsSetByUser = True
        
        #set up default pass
        if not self.folderIsSetByUser:
            if os.path.exists("c:\\ladybug\\") and os.access(os.path.dirname("c:\\ladybug\\"), os.F_OK):
                # folder already exists so it is all fine
                sc.sticky["Dragonfly_DefaultFolder"] = "c:\\ladybug\\"
            elif os.access(os.path.dirname("c:\\"), os.F_OK):
                #the folder does not exists but write privileges are given so it is fine
                sc.sticky["Dragonfly_DefaultFolder"] = "c:\\ladybug\\"
            else:
                # let's use the user folder
                username = os.getenv("USERNAME")
                # make sure username doesn't have space
                if (" " in username):
                    msg = "User name on this system: " + username + " has white space." + \
                          " Default fodelr cannot be set.\nUse defaultFolder_ to set the path to another folder and try again!" + \
                          "\nDragonfly failed to fly! :("
                    print msg
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                    sc.sticky["Dragonfly_DefaultFolder"] = ""
                    self.letItFly = False
                    return
                
                sc.sticky["Dragonfly_DefaultFolder"] = os.path.join("C:\\Users\\", username, "AppData\\Roaming\\Ladybug\\")
    
    def getComponentVersion(self):
        monthDict = {'JAN':'01', 'FEB':'02', 'MAR':'03', 'APR':'04', 'MAY':'05', 'JUN':'06',
                     'JUL':'07', 'AUG':'08', 'SEP':'09', 'OCT':'10', 'NOV':'11', 'DEC':'12'}
        # convert component version to standard versioning
        ver, verDate = ghenv.Component.Message.split("\n")
        ver = ver.split(" ")[1].strip()
        month, day, year = verDate.split("_")
        month = monthDict[month.upper()]
        version = ".".join([year, month, day, ver])
        return version
        
    def isNewerVersionAvailable(self, currentVersion, availableVersion):
        # print int(availableVersion.replace(".", "")), int(currentVersion.replace(".", ""))
        return int(availableVersion.replace(".", "")) > int(currentVersion.replace(".", ""))
    
    def checkForUpdates(self, LB= True, HB= True, OpenStudio = True, template = True, DF = True):
        
        url = "https://github.com/mostaphaRoudsari/ladybug/raw/master/resources/versions.txt"
        versionFile = os.path.join(sc.sticky["Dragonfly_DefaultFolder"], "versions.txt")
        client = System.Net.WebClient()
        client.DownloadFile(url, versionFile)
        with open("c:/ladybug/versions.txt", "r")as vf:
            versions= eval("\n".join(vf.readlines()))
        
        if DF:
            dragonflyVersion = versions['Dragonfly']
            currentDragonflyVersion = self.getComponentVersion()
            if self.isNewerVersionAvailable(currentDragonflyVersion, dragonflyVersion):
                msg = "There is a newer version of Dragonfly available to download! " + \
                      "We strongly recommend you to download the newer version from the Dragonfly github: " + \
                      "https://github.com/chriswmackey/Dragonfly/archive/master.zip"
                print msg
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
            
        if OpenStudio:
            # This should be called inside OpenStudio component which means Honeybee is already flying
            # check if the version file exist
            openStudioLibFolder = os.path.join(sc.sticky["Honeybee_DefaultFolder"], "OpenStudio")
            versionFile = os.path.join(openStudioLibFolder, "osversion.txt")
            isNewerOSAvailable= False
            if not os.path.isfile(versionFile):
                isNewerOSAvailable= True
            else:
                # read the file
                with open(versionFile) as verFile:
                    currentOSVersion= eval(verFile.read())['version']
            
            OSVersion = versions['OpenStudio']
            
            if isNewerOSAvailable or self.isNewerVersionAvailable(currentOSVersion, OSVersion):
                sc.sticky["isNewerOSAvailable"] = True
            else:
                sc.sticky["isNewerOSAvailable"] = False
                
        if template:
            honeybeeDefaultFolder = sc.sticky["Honeybee_DefaultFolder"]
            templateFile = os.path.join(honeybeeDefaultFolder, 'OpenStudioMasterTemplate.idf')
            
            # check file doesn't exist then it should be downloaded
            if not os.path.isfile(templateFile):
                return True
            
            # find the version
            try:
                with open(templateFile) as tempFile:
                    templateVersion = eval(tempFile.readline().split("!")[-1].strip())["version"]
            except Exception, e:
                return True
            
            # finally if the file exist and already has a version, compare the versions
            currentTemplateVersion = versions['Template']
            
            return self.isNewerVersionAvailable(currentTemplateVersion, templateVersion)

checkIn = CheckIn(defaultFolder_)



class versionCheck(object):
    
    def __init__(self):
        self.version = self.getVersion(ghenv.Component.Message)
    
    def getVersion(self, LBComponentMessage):
        monthDict = {'JAN':'01', 'FEB':'02', 'MAR':'03', 'APR':'04', 'MAY':'05', 'JUN':'06',
                     'JUL':'07', 'AUG':'08', 'SEP':'09', 'OCT':'10', 'NOV':'11', 'DEC':'12'}
        # convert component version to standard versioning
        try: ver, verDate = LBComponentMessage.split("\n")
        except: ver, verDate = LBComponentMessage.split("\\n")
        ver = ver.split(" ")[1].strip()
        month, day, year = verDate.split("_")
        month = monthDict[month.upper()]
        version = ".".join([year, month, day, ver])
        return version
    
    def isCurrentVersionNewer(self, desiredVersion):
        return int(self.version.replace(".", "")) >= int(desiredVersion.replace(".", ""))
    
    def isCompatible(self, LBComponent):
        code = LBComponent.Code
        # find the version that is supposed to be flying
        try: version = code.split("compatibleLBVersion")[1].split("=")[1].split("\n")[0].strip()
        except: self.giveWarning(LBComponent)
        
        desiredVersion = self.getVersion(version)
        
        if not self.isCurrentVersionNewer(desiredVersion):
            self.giveWarning(LBComponent)
            return False
        
        return True
        
    def giveWarning(self, GHComponent):
        warningMsg = "You need a newer version of Dragonfly to use this compoent." + \
                     "Use updateDragonfly component to update userObjects.\n" + \
                     "If you have already updated userObjects drag Dragonfly_Dragonfly component " + \
                     "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        GHComponent.AddRuntimeMessage(w, warningMsg)


class df_findFolders(object):
    
    def __init__(self):
        self.UWGPath, self.UWGFile = self.which('UWGEngine.exe')
    
    def which(self, program):
        """
        Check for path. Modified from this link:
        http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
        """
        def is_exe(fpath):
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
        
        fpath, fname = os.path.split(program)
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return path, exe_file
        return None, None


class UWGGeometry(object):
    
    
    def getSrfCenPtandNormal(self, surface):
        brepFace = surface.Faces[0]
        if brepFace.IsPlanar and brepFace.IsSurface:
            u_domain = brepFace.Domain(0)
            v_domain = brepFace.Domain(1)
            centerU = (u_domain.Min + u_domain.Max)/2
            centerV = (v_domain.Min + v_domain.Max)/2
            
            centerPt = brepFace.PointAt(centerU, centerV)
            normalVector = brepFace.NormalAt(centerU, centerV)
        else:
            centroid = rc.Geometry.AreaMassProperties.Compute(brepFace).Centroid
            uv = brepFace.ClosestPoint(centroid)
            centerPt = brepFace.PointAt(uv[1], uv[2])
            normalVector = brepFace.NormalAt(uv[1], uv[2])
        
        return centerPt, normalVector
    
    # Make a function that attempts to extract the building footprint surfaces.
    def separateBrepSrfs(self, brep, maxRoofAngle, maxFloorAngle):
        up = []
        down = []
        side = []
        topNormVectors = []
        topCentPts = []
        allNormVectors = []
        roofNormals = []
        sideNormals = []
        for i in range(brep.Faces.Count):
            surface = brep.Faces[i].DuplicateFace(False)
            # find the normal
            findNormal = self.getSrfCenPtandNormal(surface)
            
            #Get the angle to the Z-axis
            if findNormal:
                normal = findNormal[1]
                allNormVectors.append(normal)
                angle2Z = math.degrees(rc.Geometry.Vector3d.VectorAngle(normal, rc.Geometry.Vector3d.ZAxis))
            else:
                angle2Z = 0
            
            if  angle2Z < maxRoofAngle or angle2Z > 360- maxRoofAngle:
                up.append(surface)
                roofNormals.append((90 - angle2Z)/90)
            elif  180 - maxFloorAngle < angle2Z < 180 + maxFloorAngle:
                down.append(surface)
                topNormVectors.append(normal)
                topCentPts.append(findNormal[0])
            else:
                side.append(surface)
                sideNormals.append((90 - angle2Z)/90)
        
        return down, up, side, sideNormals, roofNormals, topNormVectors, topCentPts, allNormVectors


class UWGTextGeneration(object):
    def __init__(self):
        
        self.defaultPavementStr = '    <urbanRoad>\n' + \
        '      <albedo>0.165</albedo>\n' + \
        '      <emissivity>0.95</emissivity>\n' + \
        '      <materials name="Default">\n' + \
        '        <names>\n' + \
        '          <item>asphalt</item>\n' + \
        '        </names>\n' + \
        '        <thermalConductivity>\n' + \
        '          <item>1</item>\n' + \
        '        </thermalConductivity>\n' + \
        '        <volumetricHeatCapacity>\n' + \
        '          <item>1600000</item>\n' + \
        '        </volumetricHeatCapacity>\n' + \
        '        <thickness>1.25</thickness>\n' + \
        '      </materials>\n' + \
        '      <vegetationCoverage>valToReplace</vegetationCoverage>\n' + \
        '      <inclination>1</inclination>\n' + \
        '      <initialTemperature>setByEPW</initialTemperature>\n' + \
        '    </urbanRoad>\n'
        
        self.defaultVegStr = '    <treeLatent>0.7</treeLatent>\n' + \
        '    <grassLatent>0.6</grassLatent>\n' + \
        '    <vegAlbedo>0.25</vegAlbedo>\n' + \
        '    <vegStart>findInEPW</vegStart>\n' + \
        '    <vegEnd>findInEPW</vegEnd>\n'
        
        self.defaultRefSitePar = '    <averageObstacleHeight>0.1</averageObstacleHeight>\n' + \
            '    <ruralRoad>\n' + \
            '        <albedo>0.25</albedo>\n' + \
            '        <emissivity>0.95</emissivity>\n' + \
            '        <materials name="Default">\n' + \
            '          <names>\n' + \
            '            <item>asphalt</item>\n' + \
            '          </names>\n' + \
            '          <thermalConductivity>\n' + \
            '            <item>1</item>\n' + \
            '          </thermalConductivity>\n' + \
            '          <volumetricHeatCapacity>\n' + \
            '            <item>1600000</item>\n' + \
            '          </volumetricHeatCapacity>\n' + \
            '          <thickness>1.25</thickness>\n' + \
            '        </materials>\n' + \
            '        <vegetationCoverage>0.5</vegetationCoverage>\n' + \
            '        <inclination>1</inclination>\n' + \
            '        <initialTemperature>setByEPW</initialTemperature>\n' + \
            '      </ruralRoad>\n'
        
        self.untouchablePar = '    <circCoeff>1.2</circCoeff>\n' + \
            '    <dayThreshold>200</dayThreshold>\n' + \
            '    <nightThreshold>50</nightThreshold>\n' + \
            '    <windMin>0.1</windMin>\n' + \
            '    <windMax>10</windMax>\n' + \
            '    <wgmax>0.005</wgmax>\n' + \
            '    <exCoeff>0.3</exCoeff>\n'
        
        self.wallConductByClimate = [0.1, 0.064195, 0.046769, 0.041895, 0.041895, 0.039754, 0.033948, 0.027743, 0.017693]
        self.roofConductByClimate = [0.1, 0.048999, 0.041123, 0.041123, 0.041123, 0.039754, 0.035685, 0.035685, 0.025749]
        self.windowUValByClimate = [10, 5.84, 4.258698, 3.690871, 2.271305, 1.987392, 1.987392, 1.987392, 1.987392]
        self.windowSHGCByClimate = [0.9, 0.25, 0.25, 0.25, 0.31, 0.31, 0.31, 0.35, 0.35]
    
    
    def createBlankTypology(self, typNum):
        blankTypo = '  <typology' + str(typNum) + ' dist="0" name="blankTypology' + str(typNum) + '">\n' + \
            '    <dist>0</dist>\n' + \
            '    <construction>\n' + \
            '      <wall>\n' + \
            '        <albedo>0.5</albedo>\n' + \
            '        <emissivity>0.9</emissivity>\n' + \
            '        <materials>\n' + \
            '          <names>\n' + \
            '            <item>Wood Siding</item>\n' + \
            '          </names>\n' + \
            '          <thermalConductivity>\n' + \
            '            <item>0.11</item>\n' + \
            '          </thermalConductivity>\n' + \
            '          <volumetricHeatCapacity>\n' + \
            '            <item>658990</item>\n' + \
            '          </volumetricHeatCapacity>\n' + \
            '          <thickness>[0.2]</thickness>\n' + \
            '        </materials>\n' + \
            '        <vegetationCoverage>0</vegetationCoverage>\n' + \
            '        <inclination>0</inclination>\n' + \
            '        <initialTemperature>20</initialTemperature>\n' + \
            '      </wall>\n' + \
            '      <roof>\n' + \
            '        <albedo>0.25</albedo>\n' + \
            '        <emissivity>0.9</emissivity>\n' + \
            '        <materials name="Boston R Roof">\n' + \
            '          <names>\n' + \
            '            <item>Insulation</item>\n' + \
            '          </names>\n' + \
            '          <thermalConductivity>\n' + \
            '            <item>0.5</item>\n' + \
            '          </thermalConductivity>\n' + \
            '          <volumetricHeatCapacity>\n' + \
            '            <item>221752</item>\n' + \
            '          </volumetricHeatCapacity>\n' + \
            '          <thickness>[0.1273]</thickness>\n' + \
            '        </materials>\n' + \
            '        <vegetationCoverage>0.2</vegetationCoverage>\n' + \
            '        <inclination>1</inclination>\n' + \
            '        <initialTemperature>20</initialTemperature>\n' + \
            '      </roof>\n' + \
            '      <mass>\n' + \
            '        <albedo>0.5</albedo>\n' + \
            '        <emissivity>0.9</emissivity>\n' + \
            '        <materials name="Boston R IM">\n' + \
            '          <names>\n' + \
            '            <item>Concrete HW</item>\n' + \
            '          </names>\n' + \
            '          <thermalConductivity>\n' + \
            '            <item>1.31</item>\n' + \
            '          </thermalConductivity>\n' + \
            '          <volumetricHeatCapacity>\n' + \
            '            <item>1874432</item>\n' + \
            '          </volumetricHeatCapacity>\n' + \
            '          <thickness>[0.1]</thickness>\n' + \
            '        </materials>\n' + \
            '        <vegetationCoverage>0</vegetationCoverage>\n' + \
            '        <inclination>1</inclination>\n' + \
            '        <initialTemperature>20</initialTemperature>\n' + \
            '      </mass>\n' + \
            '      <glazing name="Boston R">\n' + \
            '        <glazingRatio>0.15</glazingRatio>\n' + \
            '        <windowUvalue>3.8</windowUvalue>\n' + \
            '        <windowSHGC>0.39</windowSHGC>\n' + \
            '      </glazing>\n' + \
            '    </construction>\n' + \
            '    <building name="BOS Commericial">\n' + \
            '      <floorHeight>3</floorHeight>\n' + \
            '      <dayInternalGains>24.7145454545455</dayInternalGains>\n' + \
            '      <nightInternalGains>5.58725274725274</nightInternalGains>\n' + \
            '      <radiantFraction>0.5</radiantFraction>\n' + \
            '      <latentFraction>0.09</latentFraction>\n' + \
            '      <infiltration>0.176785714285714</infiltration>\n' + \
            '      <ventilation>1</ventilation>\n' + \
            '      <coolingSystemType>air</coolingSystemType>\n' + \
            '      <coolingCOP>3.7</coolingCOP>\n' + \
            '      <daytimeCoolingSetPoint>25</daytimeCoolingSetPoint>\n' + \
            '      <nighttimeCoolingSetPoint>26</nighttimeCoolingSetPoint>\n' + \
            '      <daytimeHeatingSetPoint>20</daytimeHeatingSetPoint>\n' + \
            '      <nighttimeHeatingSetPoint>17</nighttimeHeatingSetPoint>\n' + \
            '      <coolingCapacity>205</coolingCapacity>\n' + \
            '      <heatingEfficiency>0.8</heatingEfficiency>\n' + \
            '      <nightSetStart>19</nightSetStart>\n' + \
            '      <nightSetEnd>5</nightSetEnd>\n' + \
            '      <heatReleasedToCanyon>0</heatReleasedToCanyon>\n' + \
            '      <initialT>20</initialT>\n' + \
            '    </building>\n' + \
            '  </typology' + str(typNum) + '>\n'
        
        return blankTypo
    
    
    def defaultCommTypology(self, flr2Flr, glzRatio, climateZone, wallVeg, roofVeg):
        #Create the Commercial Typology.
        commTypo = '  <typology1 dist="TBDPercent" name="DefaultCommercial">\n' + \
            '    <dist>TBDPercent</dist>\n' + \
            '    <construction>\n' + \
            '      <wall>\n' + \
            '        <albedo>0.4</albedo>\n' + \
            '        <emissivity>0.9</emissivity>\n' + \
            '        <materials name="ASHRAE 90.1-2010 EXTWALL METAL">\n' + \
            '          <names>\n' + \
            '            <item>Metal Building Wall Insulation</item>\n' + \
            '            <item>1/2IN Gypsum</item>\n' + \
            '          </names>\n' + \
            '          <thermalConductivity>\n' + \
            '            <item>0.049</item>\n' + \
            '            <item>' + str(self.wallConductByClimate[climateZone]) + '</item>\n' + \
            '          </thermalConductivity>\n' + \
            '          <volumetricHeatCapacity>\n' + \
            '            <item>221752.0</item>\n' + \
            '            <item>651467.000000</item>\n' + \
            '          </volumetricHeatCapacity>\n' + \
            '          <thickness>[0.0815632376352, 0.012699999999999999]</thickness>\n' + \
            '        </materials>\n' + \
            '        <vegetationCoverage>' + str(wallVeg) + '</vegetationCoverage>\n' + \
            '        <inclination>0</inclination>\n' + \
            '        <initialTemperature>15.6</initialTemperature>\n' + \
            '      </wall>\n' + \
            '      <roof>\n' + \
            '        <albedo>0.2</albedo>\n' + \
            '        <emissivity>0.9</emissivity>\n' + \
            '        <materials name="ASPHALTROOF">\n' + \
            '          <names>\n' + \
            '            <item>ASPHALTMEMBRANE</item>\n' + \
            '            <item>METAL ROOF INSULATION</item>\n' + \
            '            <item>METAL DECKING</item>\n' + \
            '          </names>\n' + \
            '          <thermalConductivity>\n' + \
            '            <item>0.02</item>\n' + \
            '            <item>' + str(self.roofConductByClimate[climateZone]) + '</item>\n' + \
            '            <item>45.006</item>\n' + \
            '          </thermalConductivity>\n' + \
            '          <volumetricHeatCapacity>\n' + \
            '            <item>1637083</item>\n' + \
            '            <item>221752.0</item>\n' + \
            '            <item>3213312.0</item>\n' + \
            '          </volumetricHeatCapacity>\n' + \
            '          <thickness>[0.01, 0.12602578716560001, 0.0015]</thickness>\n' + \
            '        </materials>\n' + \
            '        <vegetationCoverage>' + str(roofVeg) + '</vegetationCoverage>\n' + \
            '        <inclination>1</inclination>\n' + \
            '        <initialTemperature>15.6</initialTemperature>\n' + \
            '      </roof>\n' + \
            '      <mass>\n' + \
            '        <albedo>0.3</albedo>\n' + \
            '        <emissivity>0.9</emissivity>\n' + \
            '        <materials name="Interior Floor">\n' + \
            '          <names>\n' + \
            '            <item>F16 Acoustic tile</item>\n' + \
            '            <item>F05 Ceiling air space resistance</item>\n' + \
            '            <item>M11 100mm lightweight concrete</item>\n' + \
            '          </names>\n' + \
            '          <thermalConductivity>\n' + \
            '            <item>0.06</item>\n' + \
            '            <item>0.555555555556</item>\n' + \
            '            <item>0.53</item>\n' + \
            '          </thermalConductivity>\n' + \
            '          <volumetricHeatCapacity>\n' + \
            '            <item>217120.000000</item>\n' + \
            '            <item>1211.025</item>\n' + \
            '            <item>1075200.0</item>\n' + \
            '          </volumetricHeatCapacity>\n' + \
            '          <thickness>[0.019099999999999999, 0.10000000000000001, 0.1016]</thickness>\n' + \
            '        </materials>\n' + \
            '        <vegetationCoverage>0</vegetationCoverage>\n' + \
            '        <inclination>1</inclination>\n' + \
            '        <initialTemperature>15.6</initialTemperature>\n' + \
            '      </mass>\n' + \
            '      <glazing name="ASHRAE 90.1-2010 EXTWINDOW METAL">\n' + \
            '        <glazingRatio>' + str(glzRatio) + '</glazingRatio>\n' + \
            '        <windowUvalue>' + str(self.windowUValByClimate[climateZone]) + '</windowUvalue>\n' + \
            '        <windowSHGC>' + str(self.windowSHGCByClimate[climateZone]) + '</windowSHGC>\n' + \
            '      </glazing>\n' + \
            '    </construction>\n' + \
            '    <building name="OfficeBuilding">\n' + \
            '      <floorHeight>' + str(flr2Flr) + '</floorHeight>\n' + \
            '      <dayInternalGains>16.6907306330</dayInternalGains>\n' + \
            '      <nightInternalGains>4.73692433306</nightInternalGains>\n' + \
            '      <radiantFraction>0.540530874392</radiantFraction>\n' + \
            '      <latentFraction>0.061651734104</latentFraction>\n' + \
            '      <infiltration>0.160149750871</infiltration>\n' + \
            '      <ventilation>0.417711093299</ventilation>\n' + \
            '      <coolingSystemType>air</coolingSystemType>\n' + \
            '      <coolingCOP>3.0</coolingCOP>\n' + \
            '      <daytimeCoolingSetPoint>24.4167123288</daytimeCoolingSetPoint>\n' + \
            '      <nighttimeCoolingSetPoint>26.0243835616</nighttimeCoolingSetPoint>\n' + \
            '      <daytimeHeatingSetPoint>20.1665753425</daytimeHeatingSetPoint>\n' + \
            '      <nighttimeHeatingSetPoint>16.9512328767</nighttimeHeatingSetPoint>\n' + \
            '      <coolingCapacity>205</coolingCapacity>\n' + \
            '      <heatingEfficiency>0.8</heatingEfficiency>\n' + \
            '      <nightSetStart>20</nightSetStart>\n' + \
            '      <nightSetEnd>8</nightSetEnd>\n' + \
            '      <heatReleasedToCanyon>0.5</heatReleasedToCanyon>\n' + \
            '      <initialT>15.6</initialT>\n' + \
            '    </building>\n' + \
            '  </typology1>\n'
        
        return commTypo
    
    
    def defaultResidTypology(self, flr2Flr, glzRatio, climateZone, wallVeg, roofVeg):
        #Create the Residential Typology.
        residTypo = '  <typology1 dist="TBDPercent" name="DefaultResidence">\n' + \
            '    <dist>TBDPercent</dist>\n' + \
            '    <construction>\n' + \
            '      <wall>\n' + \
            '        <albedo>0.22</albedo>\n' + \
            '        <emissivity>0.9</emissivity>\n' + \
            '        <materials name="ASHRAE 90.1-2010 EXTWALL WOODFRAME">\n' + \
            '          <names>\n' + \
            '            <item>Wood Siding</item>\n' + \
            '            <item>Wood Frame Wall Insulation</item>\n' + \
            '            <item>1/2IN Gypsum</item>\n' + \
            '          </names>\n' + \
            '          <thermalConductivity>\n' + \
            '            <item>0.11</item>\n' + \
            '            <item>' + str(self.wallConductByClimate[climateZone]) + '</item>\n' + \
            '            <item>0.16</item>\n' + \
            '          </thermalConductivity>\n' + \
            '          <volumetricHeatCapacity>\n' + \
            '            <item>658990.2</item>\n' + \
            '            <item>221752.0</item>\n' + \
            '            <item>651467.000000</item>\n' + \
            '          </volumetricHeatCapacity>\n' + \
            '          <thickness>[0.01, 0.0815632376352, 0.012699999999999999]</thickness>\n' + \
            '        </materials>\n' + \
            '        <vegetationCoverage>' + str(wallVeg) + '</vegetationCoverage>\n' + \
            '        <inclination>0</inclination>\n' + \
            '        <initialTemperature>21.1000003815</initialTemperature>\n' + \
            '      </wall>\n' + \
            '      <roof>\n' + \
            '        <albedo>0.2</albedo>\n' + \
            '        <emissivity>0.9</emissivity>\n' + \
            '        <materials name="ASPHALTROOF">\n' + \
            '          <names>\n' + \
            '            <item>ASPHALTMEMBRANE</item>\n' + \
            '            <item>IEAD ROOF INSULATION</item>\n' + \
            '            <item>METAL DECKING</item>\n' + \
            '          </names>\n' + \
            '          <thermalConductivity>\n' + \
            '            <item>0.02</item>\n' + \
            '            <item>' + str(self.roofConductByClimate[climateZone]) + '</item>\n' + \
            '            <item>45.006</item>\n' + \
            '          </thermalConductivity>\n' + \
            '          <volumetricHeatCapacity>\n' + \
            '            <item>1637083</item>\n' + \
            '            <item>221752.0</item>\n' + \
            '            <item>3213312.0</item>\n' + \
            '          </volumetricHeatCapacity>\n' + \
            '          <thickness>[0.01, 0.12733264797253799, 0.0015]</thickness>\n' + \
            '        </materials>\n' + \
            '        <vegetationCoverage>' + str(roofVeg) + '</vegetationCoverage>\n' + \
            '        <inclination>1</inclination>\n' + \
            '        <initialTemperature>21.1000003815</initialTemperature>\n' + \
            '      </roof>\n' + \
            '      <mass>\n' + \
            '        <albedo>0.7</albedo>\n' + \
            '        <emissivity>0.9</emissivity>\n' + \
            '        <materials name="Interior Floor">\n' + \
            '          <names>\n' + \
            '            <item>F16 Acoustic tile</item>\n' + \
            '            <item>F05 Ceiling air space resistance</item>\n' + \
            '            <item>M11 100mm lightweight concrete</item>\n' + \
            '          </names>\n' + \
            '          <thermalConductivity>\n' + \
            '            <item>0.06</item>\n' + \
            '            <item>0.555555555556</item>\n' + \
            '            <item>0.53</item>\n' + \
            '          </thermalConductivity>\n' + \
            '          <volumetricHeatCapacity>\n' + \
            '            <item>217120.000000</item>\n' + \
            '            <item>1211.025</item>\n' + \
            '            <item>1075200.0</item>\n' + \
            '          </volumetricHeatCapacity>\n' + \
            '          <thickness>[0.019099999999999999, 0.10000000000000001, 0.1016]</thickness>\n' + \
            '        </materials>\n' + \
            '        <vegetationCoverage>0</vegetationCoverage>\n' + \
            '        <inclination>1</inclination>\n' + \
            '        <initialTemperature>21.1000003815</initialTemperature>\n' + \
            '      </mass>\n' + \
            '      <glazing name="ASHRAE 90.1-2010 EXTWINDOW METAL CLIMATEZONE 1">\n' + \
            '        <glazingRatio>' + str(glzRatio) + '</glazingRatio>\n' + \
            '        <windowUvalue>' + str(self.windowUValByClimate[climateZone]) + '</windowUvalue>\n' + \
            '        <windowSHGC>' + str(self.windowSHGCByClimate[climateZone]) + '</windowSHGC>\n' + \
            '      </glazing>\n' + \
            '    </construction>\n' + \
            '    <building name="ResidenceBuilding">\n' + \
            '      <floorHeight>' + str(flr2Flr) + '</floorHeight>\n' + \
            '      <dayInternalGains>7.50688450751</dayInternalGains>\n' + \
            '      <nightInternalGains>10.0155473446</nightInternalGains>\n' + \
            '      <radiantFraction>0.535689045372</radiantFraction>\n' + \
            '      <latentFraction>0.0795843900193</latentFraction>\n' + \
            '      <infiltration>0.271882332363</infiltration>\n' + \
            '      <ventilation>0.0</ventilation>\n' + \
            '      <coolingSystemType>air</coolingSystemType>\n' + \
            '      <coolingCOP>1.7</coolingCOP>\n' + \
            '      <daytimeCoolingSetPoint>23.8999996185</daytimeCoolingSetPoint>\n' + \
            '      <nighttimeCoolingSetPoint>23.8999996185</nighttimeCoolingSetPoint>\n' + \
            '      <daytimeHeatingSetPoint>21.1000003815</daytimeHeatingSetPoint>\n' + \
            '      <nighttimeHeatingSetPoint>21.1000003815</nighttimeHeatingSetPoint>\n' + \
            '      <coolingCapacity>205</coolingCapacity>\n' + \
            '      <heatingEfficiency>0.8</heatingEfficiency>\n' + \
            '      <nightSetStart>20</nightSetStart>\n' + \
            '      <nightSetEnd>8</nightSetEnd>\n' + \
            '      <heatReleasedToCanyon>1.0</heatReleasedToCanyon>\n' + \
            '      <initialT>21.1000003815</initialT>\n' + \
            '    </building>\n' + \
            '  </typology1>\n'
        
        return residTypo
    
    def createXMLFromEPConstr(self, epConstr, type, vegCoverage, startSetPt):
        #Call the materials in the EP Construction.
        hb_EPMaterialAUX = sc.sticky["honeybee_EPMaterialAUX"]()
        materials, comments, UValue_SI, UValue_IP = hb_EPMaterialAUX.decomposeEPCnstr(epConstr.upper())
        
        ### Get all of the properties of the EP Materials.
        conductivities = []
        heatCapacities = []
        thicknesses = []
        albedo = 0
        emissivity = 0
        for count, matName in enumerate(materials):
            values, comments, UValue_SI, UValue_IP = hb_EPMaterialAUX.decomposeMaterial(matName.upper(), ghenv.Component)
            if values[0] == 'Material':
                if float(values[2]) >= 0.01:
                    #Typical EP Opaque Material.
                    conductivities.append(values[3])
                    heatCapacities.append(float(values[4]) * float(values[5]))
                    thicknesses.append(float(values[2]))
                
                #If it's the outer-most construction, grab it's albedo and emissivity.
                if count == 0:
                    albedo = 1 - float(values[7])
                    emissivity = values[6]
            elif values[0] == 'Material:NoMass':
                #Typical NoMass EP Opaque Material.  I took heat capacities and thickness here from a roof membrane material.
                print "You have connected a zone with a NoMass material but the UWG requires that all constructions have a mass.  As such, a very low heat cpacity of 1637 kJ/m3-K will be used with a thickness of 1 cm."
                conductivities.append((1/float(values[2]))*0.01)
                heatCapacities.append(1637083)
                thicknesses.append(0.01)
                
                #If it's the outer-most construction, grab it's albedo and emissivity.
                if count == 0:
                    albedo = 1 - float(values[4])
                    emissivity = values[3]
            
            elif values[0] == 'Material:AirGap':
                #Typical Air EP Material.
                conductivities.append(0.1/float(values[1]))
                heatCapacities.append(1211.025)
                thicknesses.append(0.1)
                
                #If it's the outer-most construction, that's really frickin' weird.  Tell the user they did something worng!
                if count == 0:
                    warning = "You have input a material or zone that has an air resistance material on the outer layer.  \n I have no idea what reflectance or emissivity you want me to use for this material. \n Please use constructions that make sense."
                    print warning
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
                    albedo = 0.5
                    emissivity = 0.9
        
        
        ### Build the construction string from the properties.
        #Start by building the header
        constrStr = '      <' + type + '>\n'
        constrStr = constrStr + '        <albedo>' + str(albedo) + '</albedo>\n'
        constrStr = constrStr + '        <emissivity>' + str(emissivity) + '</emissivity>\n'
        constrStr = constrStr + '        <materials name="' + epConstr + '">\n'
        
        # Next, write in the material names.
        constrStr = constrStr + '          <names>\n'
        for mat in materials:
            constrStr = constrStr + '            <item>' + mat + '</item>\n'
        constrStr = constrStr + '          </names>\n'
        
        # Next, write in the thermal conductivities.
        constrStr = constrStr + '          <thermalConductivity>\n'
        for cond in conductivities:
            constrStr = constrStr + '            <item>' + str(cond) + '</item>\n'
        constrStr = constrStr + '          </thermalConductivity>\n'
        
        # Next, write in the heat capacities.
        constrStr = constrStr + '          <volumetricHeatCapacity>\n'
        for cap in heatCapacities:
            constrStr = constrStr + '            <item>' + str(cap) + '</item>\n'
        constrStr = constrStr + '          </volumetricHeatCapacity>\n'
        
        # Finally, write in the thicknesses and close out the material properties.
        constrStr = constrStr + '          <thickness>' +  str(thicknesses) + '</thickness>\n'
        constrStr = constrStr + '        </materials>\n'
        
        
        ### Write in other surface properties.
        constrStr = constrStr + '        <vegetationCoverage>' + str(vegCoverage) + '</vegetationCoverage>\n'
        if type == 'wall': constrStr = constrStr + '        <inclination>0</inclination>\n'
        else: constrStr = constrStr + '        <inclination>1</inclination>\n'
        constrStr = constrStr + '        <initialTemperature>' + str(startSetPt) + '</initialTemperature>\n'
        constrStr = constrStr + '      </' + type + '>\n'
        
        
        return constrStr
    
    def createXMLFromEPWindow(self, glzRatio, glzConstrs, glzAreas):
        #Get a name of the construction from the construction that has the most area.
        glzAreasSort, glzConstrsSort = zip(*sorted(zip(glzAreas, glzConstrs)))
        glzName = glzConstrsSort[-1]
        
        #Get a weighted average U-value and SHGC.
        uValues = []
        SHGCs = []
        avgUVal = 0
        avgSHGC = 0
        #Call the materials in the EP Construction.
        hb_EPMaterialAUX = sc.sticky["honeybee_EPMaterialAUX"]()
        for winConstr in glzConstrs:
            materials, comments, UValue_SI, UValue_IP = hb_EPMaterialAUX.decomposeEPCnstr(winConstr.upper())
            uValues.append(UValue_SI)
            shgc = 1
            for glzMat in materials:
                values, comments, UValue_SI, UValue_IP = hb_EPMaterialAUX.decomposeMaterial(glzMat.upper(), ghenv.Component)
                if values[0] == 'WindowMaterial:Glazing':
                    #Full EP Glass material.
                    shgc = shgc * float(values[4])
                elif values[0] == 'WindowMaterial:SimpleGlazingSystem':
                    #Simple window material.
                    shgc = shgc * float(values[2])
            SHGCs.append(shgc)
        
        for count, val in enumerate(uValues):
            avgUVal = avgUVal + (val * (glzAreas[count]/sum(glzAreas)))
        for count, val in enumerate(SHGCs):
            avgSHGC = avgSHGC + (val * (glzAreas[count]/sum(glzAreas)))
        
        
        #Build the string.
        glzStr = '      <glazing name="' + glzName + '">\n'
        glzStr = glzStr + '        <glazingRatio>' + str(glzRatio) + '</glazingRatio>\n'
        glzStr = glzStr + '        <windowUvalue>' + str(avgUVal) + '</windowUvalue>\n'
        glzStr = glzStr + '        <windowSHGC>' + str(avgSHGC) + '</windowSHGC>\n'
        glzStr = glzStr + '      </glazing>\n'
        
        return glzStr
    
    #Have a function that separate day and night variables from the list.
    def separateDayAndNight(self, schedule):
        nightVals = []
        dayVals = []
        daycount = 0
        startHour = 1
        for val in schedule:
            if startHour < 8:
                nightVals.append(val)
                startHour += 1
            elif startHour < 19:
                dayVals.append(val)
                startHour += 1
            else:
                daycount+=1
                dayVals.append(val)
                startHour = startHour - 23
        
        return nightVals, dayVals
    
    def constructIntGainString(self, equipSched, lightSched, pplSched):
        #Define defalut heat fractions for different types of loads.
        #These numbers were copied from the rcommended values on the online UWG documentation:
        #http://urbanmicroclimate.scripts.mit.edu/uwg_parameters.php
        equipRadFrac = 0.5
        lightRadFrac = 0.7
        pplRadFrac = 0.3
        equipLatFrac = 0
        lightLatFrac = 0
        pplLatFrac = 0.3
        
        
        #Get the day and night values of each type of heat gain.
        equipNightVals, equipDayVals = self.separateDayAndNight(equipSched)
        equipNightVal = sum(equipNightVals)/len(equipNightVals)
        equipDayVal = sum(equipDayVals)/len(equipDayVals)
        
        lightNightVals, lightDayVals = self.separateDayAndNight(lightSched)
        lightNightVal = sum(lightNightVals)/len(lightNightVals)
        lightDayVal = sum(lightDayVals)/len(lightDayVals)
        
        pplNightVals, pplDayVals = self.separateDayAndNight(pplSched)
        pplNightVal = sum(pplNightVals)/len(pplNightVals)
        pplDayVal = sum(pplDayVals)/len(pplDayVals)
        
        #Calculate the total heat gain and weighted-average radiant + latent fractions.
        dayInternalGain = equipDayVal + lightDayVal + pplDayVal
        nightInternalGain = equipNightVal + lightNightVal + pplNightVal
        totalGain = (dayInternalGain + nightInternalGain) / 2
        if totalGain != 0:
            radiantFraction = ((((equipNightVal+equipDayVal)/2)/totalGain)*equipRadFrac) + ((((lightNightVal+lightDayVal)/2)/totalGain)*lightRadFrac) + ((((pplNightVal+pplDayVal)/2)/totalGain)*pplRadFrac)
            latentFraction = ((((equipNightVal+equipDayVal)/2)/totalGain)*equipLatFrac) + ((((lightNightVal+lightDayVal)/2)/totalGain)*lightLatFrac) + ((((pplNightVal+pplDayVal)/2)/totalGain)*pplLatFrac)
        else:
            radiantFraction = 0
            latentFraction = 0
        
        #Write the resulting intGains into a string.
        intGainString = '      <dayInternalGains>' + str(dayInternalGain) + '</dayInternalGains>\n'
        intGainString = intGainString + '      <nightInternalGains>' + str(nightInternalGain) + '</nightInternalGains>\n'
        intGainString = intGainString + '      <radiantFraction>' + str(radiantFraction) + '</radiantFraction>\n'
        intGainString = intGainString + '      <latentFraction>' + str(latentFraction) + '</latentFraction>\n'
        
        return intGainString
    
    
    def constructSetPtString(self, coolSched, heatSched):
        #Get the day and night values of each type of heat gain.
        coolNightVals, coolDayVals = self.separateDayAndNight(coolSched)
        coolNightVal = sum(coolNightVals)/len(coolNightVals)
        coolDayVal = sum(coolDayVals)/len(coolDayVals)
        
        #Get the day and night values of each type of heat gain.
        heatNightVals, heatDayVals = self.separateDayAndNight(heatSched)
        heatNightVal = sum(heatNightVals)/len(heatNightVals)
        heatDayVal = sum(heatDayVals)/len(heatDayVals)
        
        #Write the resulting intGains into a string.
        setPtString = '      <daytimeCoolingSetPoint>' + str(coolDayVal) + '</daytimeCoolingSetPoint>\n'
        setPtString = setPtString + '      <nighttimeCoolingSetPoint>' + str(coolNightVal) + '</nighttimeCoolingSetPoint>\n'
        setPtString = setPtString + '      <daytimeHeatingSetPoint>' + str(heatDayVal) + '</daytimeHeatingSetPoint>\n'
        setPtString = setPtString + '      <nighttimeHeatingSetPoint>' + str(heatNightVal) + '</nighttimeHeatingSetPoint>\n'
        
        return setPtString



try:
    checkIn.checkForUpdates(LB= True, HB= False, OpenStudio = False, template = False)
except:
    # no internet connection
    pass

now = datetime.datetime.now()

def checkGHPythonVersion(target = "0.6.0.3"):
    
    currentVersion = int(ghenv.Version.ToString().replace(".", ""))
    targetVersion = int(target.replace(".", ""))
    
    if targetVersion > currentVersion: return False
    else: return True

GHPythonTargetVersion = "0.6.0.3"

try:
    if not checkGHPythonVersion(GHPythonTargetVersion):
        assert False
except:
    msg =  "Dragonfly failed to fly! :(\n" + \
           "You are using an old version of GHPython. " +\
           "Please update to version: " + GHPythonTargetVersion
    print msg
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
    checkIn.letItFly = False
    sc.sticky["dragonfly_release"] = False



def unzip(source_filename, dest_dir):
    with zipfile.ZipFile(source_filename) as zf:
        for member in zf.infolist():
            # Path traversal defense copied from
            # http://hg.python.org/cpython/file/tip/Lib/http/server.py#l789
            words = member.filename.split('\\')
            path = dest_dir
            for word in words[:-1]:
                drive, word = os.path.splitdrive(word)
                head, word = os.path.split(word)
                if word in (os.curdir, os.pardir, ''): continue
                path = os.path.join(path, word)
            zf.extract(member, path)



if checkIn.letItFly:
    sc.sticky["dragonfly_release"] = versionCheck()       
    
    if sc.sticky.has_key("dragonfly_release") and sc.sticky["dragonfly_release"]:
        folders = df_findFolders()
        sc.sticky["dragonfly_folders"] = {}
        if folders.UWGPath == None:
            if os.path.isdir(sc.sticky["Dragonfly_DefaultFolder"] + "\\UWG\\"):
                folders.UWGPath = sc.sticky["Dragonfly_DefaultFolder"] + "\\UWG\\"
            else:
                # Try to download these files in the background.
                try:
                    ## download File
                    print 'Downloading UWG to ', sc.sticky["Dragonfly_DefaultFolder"]
                    updatedLink = "https://github.com/hansukyang/UWG_Matlab/raw/master/ArchivedCodes/UWG.zip"
                    localFilePath = sc.sticky["Dragonfly_DefaultFolder"] + 'UWG.zip'
                    client = System.Net.WebClient()
                    client.DownloadFile(updatedLink, localFilePath)
                    #Unzip the file
                    unzip(localFilePath, sc.sticky["Dragonfly_DefaultFolder"])
                    os.rename('C:\\ladybug\\UWG\\UWGEngine_mcr\\META\\','C:\\ladybug\\UWG\\UWGEngine_mcr\\.META\\')
                    folders.UWGPath = sc.sticky["Dragonfly_DefaultFolder"] + "\\UWG\\"
                except:
                    msg1 = "Dragonfly failed to download the Urban Weather Generator (UWG) folder in the background.\n" + \
                         "Download the following file and unzip it into the C:\ drive of your system:"
                    msg2 = "https://github.com/hansukyang/UWG_Matlab/raw/master/ArchivedCodes/UWG.zip"
                    
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg1)
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg2)
                    
                    folders.UWGPath = ""
        
        if os.path.isdir("c:\\Program Files\\MATLAB\\MATLAB Runtime\\v90\\"):
            folders.matlabPath = "c:\\Program Files\\MATLAB\\MATLAB Runtime\\v90\\"
        else:
            
            msg3 = "Dragonfly cannot find the correct version of the Matlab Runtime Compiler v9.0 (MRC 9.0) in your system. \n" + \
            "You won't be able to morph EPW files to account for urban heat island effects without this application. \n" + \
            "You can download an installer for the the Matlab Runtime Compiler from this link on the UWG github:"
            msg4 = "https://www.mathworks.com/supportfiles/downloads/R2015b/deployment_files/R2015b/installers/win64/MCR_R2015b_win64_installer.exe"
            
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg3)
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg4)
            
            folders.matlabPath = ""
        
        sc.sticky["dragonfly_folders"]["UWGPath"] = folders.UWGPath
        sc.sticky["dragonfly_folders"]["matlabPath"] = folders.matlabPath
        sc.sticky["dragonfly_UWGGeometry"] = UWGGeometry
        sc.sticky["dragonfly_UWGText"] = UWGTextGeneration
        
        
        print "Hi " + os.getenv("USERNAME")+ "!\n" + \
              "Dragonfly is Flying! Vviiiiiiizzz...\n\n" + \
              "Default path is set to: " + sc.sticky["Dragonfly_DefaultFolder"] + "\n" + \
              "UWGEngine path is set to: " + sc.sticky["dragonfly_folders"]["UWGPath"]