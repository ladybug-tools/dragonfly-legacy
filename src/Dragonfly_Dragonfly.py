# This is the heart of Dragonfly
#
# Dragonfly: A Plugin for Environmental Analysis (GPL) started by Chris Mackey
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
ghenv.Component.Message = 'VER 0.0.01\nSEP_19_2015'
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
    
    def checkForUpdates(self, LB= True, HB= True, OpenStudio = True, template = True):
        
        url = "https://github.com/mostaphaRoudsari/ladybug/raw/master/resources/versions.txt"
        versionFile = os.path.join(sc.sticky["Dragonfly_DefaultFolder"], "versions.txt")
        client = System.Net.WebClient()
        client.DownloadFile(url, versionFile)
        with open("c:/ladybug/versions.txt", "r")as vf:
            versions= eval("\n".join(vf.readlines()))
        
        if LB:
            ladybugVersion = versions['Ladybug']
            currentLadybugVersion = self.getComponentVersion() # I assume that this function will be called inside Ladybug_ladybug Component
            if self.isNewerVersionAvailable(currentLadybugVersion, ladybugVersion):
                msg = "There is a newer version of Ladybug available to download! " + \
                      "We strongly recommend you to download the newer version from Food4Rhino: " + \
                      "http://www.food4rhino.com/project/ladybug-honeybee"
                print msg
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        if HB:
            honeybeeVersion = versions['Honeybee']
            currentHoneybeeVersion = self.getComponentVersion() # I assume that this function will be called inside Honeybee_Honeybee Component
            if self.isNewerVersionAvailable(currentHoneybeeVersion, honeybeeVersion):
                msg = "There is a newer version of Honeybee available to download! " + \
                      "We strongly recommend you to download the newer version from Food4Rhino: " + \
                      "http://www.food4rhino.com/project/ladybug-honeybee"
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


if checkIn.letItFly:
    sc.sticky["dragonfly_release"] = versionCheck()       
    
    if sc.sticky.has_key("dragonfly_release") and sc.sticky["dragonfly_release"]:
        folders = df_findFolders()
        sc.sticky["dragonfly_folders"] = {}
        if folders.UWGPath == None:
            if os.path.isdir("c:\\Program Files (x86)\\UWG"):
                folders.UWGPath = "c:\\Program Files (x86)\\UWG"
            else:
                msg1 = "Dragonfly cannot find the Urban Weather Generator (UWG) folder on your system.\n" + \
                     "Make sure you have both the Urban Weather Generator (UWG) and the Matlab Runtime Compiler v 8.5 (MRC 8.5) installed on your system.\n" + \
                     "You won't be able to warp EPW files to account for urban heat island effects without these two applications installed.\n" + \
                     "You can download the UWG application from here:"
                msg2 = "http://urbanmicroclimate.scripts.mit.edu/uwg.php"
                msg3 = "And you can download the Matlab Runtime Compiler v 8.5 (MRC 8.5) from here:"
                msg4 = "http://www.mathworks.com/products/compiler/mcr/index.html"
                
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg1)
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg2)
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg3)
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg4)
                
                folders.UWGPath = ""
        
        
        print "Hi " + os.getenv("USERNAME")+ "!\n" + \
              "Dragonfly is Flying! Vviiiiiiizzz...\n\n" + \
              "Default path is set to: " + sc.sticky["Dragonfly_DefaultFolder"]