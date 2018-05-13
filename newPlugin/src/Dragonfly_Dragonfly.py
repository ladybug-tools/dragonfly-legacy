# This is the heart of Dragonfly
#
# Dragonfly: A Plugin for Climate Data Generation (GPL) started by Chris Mackey <chris@ladybug.tools> 
# 
# This file is part of Dragonfly.
# 
# Copyright (c) 2015, Chris Mackey <chris@ladybug.tools> 
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
Provided by Dragonfly 0.0.02
    Args:
        defaultFolder_: Optional input for Dragonfly default folder.
                       If empty default folder will be set to C:\ladybug or C:\Users\%USERNAME%\AppData\Roaming\Ladybug\
    Returns:
        report: Current Dragonfly mood!!!
"""

ghenv.Component.Name = "Dragonfly_Dragonfly"
ghenv.Component.NickName = 'Dragonfly'
ghenv.Component.Message = 'VER 0.0.02\nMAY_12_2018'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "0 | Dragonfly"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc
import Grasshopper.Kernel as gh
import Grasshopper
import math
import os
import System
System.Net.ServicePointManager.SecurityProtocol = System.Net.SecurityProtocolType.Tls12
import datetime
import zipfile
import copy

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
            # Differenciate on platform used
            # If windows
            # Normally would use sys.platform but it will return 'cli' since
            # this is IronPython.
            # The shortcoming of os.name is that it returns "posix" for both
            # Mac and Linux, here we don't care (and anyways, rhino isn't on linux)
            if os.name =='nt':
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
            # If macOS
            elif os.name == 'posix':
                default_path = os.path.expanduser('~/ladybug/')
                # folder already exists and there is write privileges, or
                # there's write privileges for the parent folder
                if (os.path.exists(default_path) and  os.access(os.path.dirname(default_path), os.F_OK)) or (os.access(os.path.expanduser('~'), os.F_OK)):
                    sc.sticky["Dragonfly_DefaultFolder"] = default_path
                else:
                     # let's use the Rhino AppData folder
                    try:
                        appdata = rc.RhinoApp.GetDataDirectory(True, False)
                    except AttributeError:
                        appdata = False
                    assert appdata, 'Failed to set up the folder.\n' \
                        'Try to set it up manually using defaultFolder_ input.'
                    sc.sticky["Dragonfly_DefaultFolder"] = os.path.join(appdata, "ladybug/")
            else:
                raise PlatformError("Unsupported platform {}. Isn't Rhino only available for Windows and Mac?".format(sys.platform))
        
        self.updateCategoryIcon()
    
    def updateCategoryIcon(self):
        try:
            url = "https://raw.githubusercontent.com/chriswmackey/Dragonfly/master/resources/icon_16_16.png"
            icon = os.path.join(sc.sticky["Dragonfly_DefaultFolder"], "DF_icon_16_16.png")
            if not os.path.isfile(icon):
                client = System.Net.WebClient()
                client.DownloadFile(url, icon)
            
            iconBitmap = System.Drawing.Bitmap(icon)
            Grasshopper.Instances.ComponentServer.AddCategoryIcon("Dragonfly", iconBitmap)
        except:
            pass
            
        Grasshopper.Instances.ComponentServer.AddCategoryShortName("Dragonfly", "DF")
        Grasshopper.Instances.ComponentServer.AddCategorySymbolName("Dragonfly", "D")
        Grasshopper.Kernel.GH_ComponentServer.UpdateRibbonUI() #Reload the Ribbon
    
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
    
    def checkForUpdates(self, DF = True):
        
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
        try: version = code.split("compatibleDFVersion")[1].split("=")[1].split("\n")[0].strip()
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
    
    def isInputMissing(self, GHComponent):
        isInputMissing = False
        
        for param in GHComponent.Params.Input:
            if param.NickName.startswith("_") and \
                not param.NickName.endswith("_") and \
                not param.VolatileDataCount:
                    warning = "Input parameter %s failed to collect data!"%param.NickName
                    GHComponent.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
                    isInputMissing = True
        
        return isInputMissing


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
    
    def __init__(self):
        # transform to project things into the XY plane
        self.groundProjection = rc.Geometry.Transform.PlanarProjection(rc.Geometry.Plane.WorldXY)
        
        # unit conversions
        units = sc.doc.ModelUnitSystem
        if `units` == 'Rhino.UnitSystem.Meters': self.linearConversionFac = 1.00
        elif `units` == 'Rhino.UnitSystem.Centimeters': self.linearConversionFac = 0.01
        elif `units` == 'Rhino.UnitSystem.Millimeters': self.linearConversionFac = 0.001
        elif `units` == 'Rhino.UnitSystem.Feet': self.linearConversionFac = 0.305
        elif `units` == 'Rhino.UnitSystem.Inches': self.linearConversionFac = 0.0254
        else:
            self.linearConversionFac = 1.00
            print "Your're Kidding me! Which units are you using?"+ `units`+'?'
            print 'Please use Meters, Centimeters, Millimeters, Inches or Feet'
        
        self.areaConversionFac = math.pow(self.linearConversionFac, 2)
    
    def getSrfCenPtandNormal(self, surface):
        """Extracts the center point and normal from a surface.
        
        Args:
            surface: A rhino surface to extract points from.
        Returns:
            centerPt: The center point of the surface.
            normalVector: The normal of the surface.
        
        """
        
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
    
    def separateBrepSrfs(self, brep, maxRoofAngle=45, maxFloorAngle=60):
        """Separates the surfaces of a brep into those facing up, down and sideways
        
        Args:
            brep: A closed rhino brep representing a building.
            maxRoofAngle: The roof normal angle from the positive Z axis (in degrees) beyond 
                which a surface is no longer considered a roof. Default is 45.
            maxFloorAngle: The floor normal angle from the negative Z axis (in degrees) beyond 
                which a surface is no longer considered a floor. Default is 60.
        
        Returns:
            down: The brep surfaces facing down.
            up: The brep surfaces facing up.
            side: The brep surfaces facing to the side.
            sideNormals: The normals of the surfaces facing to the side.
            roofNormals: The normals of the surfaces facing upwards.
            bottomNormVectors: The normals of the surfaces facing down.
            bottomCentPts: The genter points of the surfaces facing down.
        """
        
        up = []
        down = []
        side = []
        bottomNormVectors = []
        bottomCentPts = []
        roofNormals = []
        sideNormals = []
        for i in range(brep.Faces.Count):
            surface = brep.Faces[i].DuplicateFace(False)
            # find the normal
            findNormal = self.getSrfCenPtandNormal(surface)
            
            #Get the angle to the Z-axis
            if findNormal:
                normal = findNormal[1]
                angle2Z = math.degrees(rc.Geometry.Vector3d.VectorAngle(normal, rc.Geometry.Vector3d.ZAxis))
            else:
                angle2Z = 0
            
            if  angle2Z < maxRoofAngle or angle2Z > 360- maxRoofAngle:
                up.append(surface)
                roofNormals.append((90 - angle2Z)/90)
            elif  180 - maxFloorAngle < angle2Z < 180 + maxFloorAngle:
                down.append(surface)
                bottomNormVectors.append(normal)
                bottomCentPts.append(findNormal[0])
            else:
                side.append(surface)
                sideNormals.append((90 - angle2Z)/90)
        
        return down, up, side, sideNormals, roofNormals, bottomNormVectors, bottomCentPts
    
    def unionAllBreps(self, bldgBreps):
        """Unioned breps into one so that correct facade areas can be computed.
        
        Args:
            bldgBreps: A list of closed rhino brep representing a building.
        
        Returns:
            result: The building breps after being unioned.
        """
        
        try:
            return rc.Geometry.Brep.CreateBooleanUnion(bldgBreps, sc.doc.ModelAbsoluteTolerance)
        except:
            return bldgBreps
    
    def calculateFootprints(self, srfBreps, solid=False):
        """Extracts the footprint and area of a surface in the XY plane
        
        Args:
            srfBreps: A list of Rhino surfaces.
        
        Returns:
            footprintArea: The footprint area of the surfaces in the XY plane.
            footprintBreps: The srfBreps projected into the XY plane.
        """
        footprintArea = 0
        footprintBreps = []
        
        for srfBrep in srfBreps:
            brepCopy = copy.deepcopy(srfBrep)
            brepCopy.Transform(self.groundProjection)
            footprintBreps.append(brepCopy)
            if solid == True:
                footprintArea += (rc.Geometry.AreaMassProperties.Compute(brepCopy).Area/2)
            else:
                footprintArea += rc.Geometry.AreaMassProperties.Compute(brepCopy).Area
        
        footprintArea = footprintArea * self.areaConversionFac
        
        return footprintArea, footprintBreps
    
    def calculateBldgFootprint(self, bldgBrep, maxFloorAngle=60):
        """Extracts building footprint and footprint area
        
        Args:
            bldgBrep: A closed rhino brep representing a building.
            maxFloorAngle: The floor normal angle from the negative Z axis (in degrees) beyond 
                which a surface is no longer considered a floor. Default is 60.
        
        Returns:
            footprintArea: The footprint area of the building.
            footprintBrep: A Brep representing the footprint of the building.
        """
        
        # separate out the surfaces of the building brep.
        footPrintBreps, upSrfs, sideSrfs, sideNormals, roofNormals, bottomNormVectors, bottomCentPts = \
            self.separateBrepSrfs(bldgBrep, 45, maxFloorAngle)
        
        # check to see if there are any building breps that self-intersect once they are projected into the XYPlane. 
        # if so, the building cantilevers over itslef and we have to use an alternative method to get the footprint.
        meshedBrep = rc.Geometry.Mesh.CreateFromBrep(bldgBrep, rc.Geometry.MeshingParameters.Coarse)
        selfIntersect = False
        for count, normal in enumerate(bottomNormVectors):
            srfRay = rc.Geometry.Ray3d(bottomCentPts[count], normal)
            for mesh in meshedBrep:
                intersectTest = rc.Geometry.Intersect.Intersection.MeshRay(mesh, srfRay)
                if intersectTest <= sc.doc.ModelAbsoluteTolerance: pass
                else: selfIntersect = True
        
        if selfIntersect == True:
            # Use any downward-facing surfaces that we can identify as part of the building footprint.
            # Boolean them together to get the projected area.
            groundBreps = []
            for srf in footPrintBreps:
                srf.Transform(self.groundProjection)
                groundBreps.append(srf)
            booleanSrf = rc.Geometry.Brep.CreateBooleanUnion(groundBreps, sc.doc.ModelAbsoluteTolerance)[0]
            footprintBrep = booleanSrf
            footprintArea = rc.Geometry.AreaMassProperties.Compute(booleanSrf).Area
        else:
            #Project the whole building brep into the X/Y plane and take half its area.
            brepCopy = copy.deepcopy(bldgBrep)
            brepCopy.Transform(self.groundProjection)
            footprintBrep = brepCopy
            footprintArea = rc.Geometry.AreaMassProperties.Compute(brepCopy).Area/2
        
        return footprintArea, footprintBrep
    
    def extractBldgHeight(self, bldgBrep):
        """Extracts building height
        
        Args:
            bldgBrep: A closed rhino brep representing a building.
        
        Returns:
            bldgHeight: The height of the building.
        """
        
        bldgBBox = rc.Geometry.Brep.GetBoundingBox(bldgBrep, rc.Geometry.Plane.WorldXY)
        bldgHeight = bldgBBox.Diagonal[2]
        
        return bldgHeight
    
    def extractBldgFacades(self, bldgBreps, maxRoofAngle=45, maxFloorAngle=60):
        """Extracts building facades and facade area
        
        Args:
            bldgBrep: A closed rhino brep representing a building.
            maxRoofAngle: The roof normal angle from the positive Z axis (in degrees) beyond 
                which a surface is no longer considered a roof. Default is 45.
            maxFloorAngle: The floor normal angle from the negative Z axis (in degrees) beyond 
                which a surface is no longer considered a floor. Default is 60.
        
        Returns:
            facadeArea: The footprint area of the building.
            facadeBreps: A list if breps representing the facades of the building.
        """
        
        facadeAreas = []
        facadeBreps = []
        
        for bldgBrep in bldgBreps:
            # separate out the surfaces of the building brep.
            footPrintBreps, upSrfs, sideSrfs, sideNormals, roofNormals, bottomNormVectors, bottomCentPts = \
                self.separateBrepSrfs(bldgBrep, maxRoofAngle, maxFloorAngle)
            
            # calculate the facade area
            facadeBreps.extend(sideSrfs)
            fArea = 0
            for srf in sideSrfs:
                fArea += rc.Geometry.AreaMassProperties.Compute(srf).Area
            facadeAreas.append(fArea)
        
        facadeArea = sum(facadeAreas)
        
        return facadeArea, facadeBreps
    
    def calculateTypologyGeoParams(self, bldgBreps, maxRoofAngle=45, maxFloorAngle=60):
        """Extracts building footprint and footprint area
        
        Args:
            bldgBreps: A list of closed rhino brep representing buildings of the same typology.
            maxRoofAngle: The roof normal angle from the positive Z axis (in degrees) beyond 
                which a surface is no longer considered a roof. Default is 45.
            maxFloorAngle: The floor normal angle from the negative Z axis (in degrees) beyond 
                which a surface is no longer considered a floor. Default is 60.
        
        Returns:
            avgBldgHeight: The average height of the buildings in the typology
            footprintArea: The footprint area of the buildings in this typology.
            facadeArea: The facade are of the buildings in this typology.
            footprintBreps: A list of breps representing the footprints of the buildings.
            facadeBreps: A list of breps representing the exposed facade surfaces of the typology.
        """
        
        bldgHeights = []
        footprintAreas = []
        footprintBreps = []
        
        for bldgBrep in bldgBreps:
            # get the building height
            bldgHeights.append(self.extractBldgHeight(bldgBrep))
            
            # get the footprint area
            ftpA, ftpBrep = self.calculateBldgFootprint(bldgBrep, maxFloorAngle)
            footprintAreas.append(ftpA)
            footprintBreps.append(ftpBrep)
        
        # get the area-weighted hieght of the buildings and total footprint area
        footprintArea = sum(footprintAreas)
        footprintWeights = [(y/footprintArea) for y in footprintAreas]
        avgBldgHeight = sum([x*footprintWeights[i] for i,x in enumerate(bldgHeights)])
        
        # compute the facade area of all of the building breps after they have been boolean unioned.
        unionedBreps = self.unionAllBreps(bldgBreps)
        facadeArea, facadeBreps = self.extractBldgFacades(unionedBreps, maxRoofAngle, maxFloorAngle)
        #facadeArea, facadeBreps = self.extractBldgFacades(bldgBreps, maxRoofAngle, maxFloorAngle)
        
        avgBldgHeight = avgBldgHeight * self.linearConversionFac
        footprintArea = footprintArea * self.areaConversionFac
        facadeArea = facadeArea * self.areaConversionFac
        
        return avgBldgHeight, footprintArea, facadeArea, footprintBreps, facadeBreps

class Utilities(object):
    
    def __init__(self):
        """Class that contains general checks"""
    
    def weighted_average(self, data, weights):
        totalWeight = sum(weights)
        normWeights = []
        avg = 0
        for i, x in enumerate(data):
            nWeight = weights[i]/totalWeight
            normWeights.append(nWeight)
            avg += x*nWeight
        
        return avg, normWeights

class GeneralChecks(object):
    
    def __init__(self):
        """Class that contains general checks"""
    
    def in_range(self, val, low, high, paramName='parameter'):
        if val <= high and val >= low:
            return val
        else:
            raise ValueError(
                    "{} must be between {} and {}. Current value is {}".format(paramName, str(low), str(high), str(val))
                )
    
    def length_match(self, list1, list2, list1Name='list1', list2Name='list2'):
        if len(list1) == len(list2):
            return True
        else:
            raise ValueError(
                    "Length of {} : {} does not match the length of {} : {}".format(list1Name, str(len(list1)), list2Name, str(len(list1)))
                )
    
    def make_type_error(self, inputName, objectName):
        raise TypeError (
                "{} are not a valid dragonfly {} object.".format(inputName, objectName)
            )

class DFBuildingTypes(object):
    
    def __init__(self):
        """Class that contains all of the accepted building typologies and contruction years"""
        
        # dictionary of building programs.
        self.programsDict = {
            'FULLSERVICERESTAURANT': 'FullServiceRestaurant',
            'HOSPITAL': 'Hospital',
            'LARGEHOTEL': 'LargeHotel',
            'LARGEOFFICE': 'LargeOffice',
            'MEDIUMOFFICE': 'MediumOffice',
            'MIDRISEAPARTMENT': 'MidRiseApartment',
            'OUTPATIENT': 'OutPatient',
            'PRIMARYSCHOOL': 'PrimarySchool',
            'QUICKSERVICERESTAURANT': 'QuickServiceRestaurant',
            'SECONDARYSCHOOL': 'SecondarySchool',
            'SMALLHOTEL': 'SmallHotel',
            'SMALLOFFICE': 'SmallOffice',
            'STANDALONERETAIL': 'StandAloneRetail',
            'STRIPMALL': 'StripMall',
            'SUPERMARKET': 'SuperMarket',
            'WAREHOUSE': 'Warehouse',
            
            'FULL SERVICE RESTAURANT': 'FullServiceRestaurant',
            'LARGE HOTEL': 'LargeHotel',
            'LARGE OFFICE': 'LargeOffice',
            'MEDIUM OFFICE': 'MediumOffice',
            'MIDRISE APARTMENT': 'MidRiseApartment',
            'OUT PATIENT': 'OutPatient',
            'PRIMARY SCHOOL': 'PrimarySchool',
            'QUICK SERVICE RESTAURANT': 'QuickServiceRestaurant',
            'SECONDARY SCHOOL': 'SecondarySchool',
            'SMALL HOTEL': 'SmallHotel',
            'SMALL OFFICE': 'SmallOffice',
            'STANDALONE RETAIL': 'StandAloneRetail',
            'STRIP MALL': 'StripMall',
            
            '0': 'LargeOffice',
            '1': 'StandAloneRetail',
            '2': 'MidRiseApartment',
            '3': 'PrimarySchool',
            '4': 'SecondarySchool',
            '5': 'SmallHotel',
            '6': 'LargeHotel',
            '7': 'Hospital',
            '8': 'OutPatient',
            '9': 'Warehouse',
            '10': 'SuperMarket',
            '11': 'FullServiceRestaurant',
            '12': 'QuickServiceRestaurant',
            
            'Office': 'LargeOffice',
            'Retail': 'StandAloneRetail'
        }
        
        # dictionary of building ages.
        self.ageDict = {
            'PRE1980S': 'Pre1980s',
            '1980SPRESENT': '1980sPresent',
            'NEWCONSTRUCTION': 'NewConstruction',
            
            '0': 'Pre1980s',
            '1': '1980sPresent',
            '2': 'NewConstruction',
            
            "Pre-1980's": 'Pre1980s',
            "1980's-Present": '1980sPresent',
            'New Construction': 'NewConstruction'
        }
    
    def check_program(self, bldg_program):
        if str(bldg_program).upper() in self.programsDict.keys():
            return self.programsDict[str(bldg_program).upper()]
        else:
            raise ValueError(
                "Building Program {} not recognized.".format('"' + str(bldg_program) + '"')
            )
    
    def check_age(self, bldg_age):
        if str(bldg_age).upper() in self.ageDict.keys():
            return self.ageDict[str(bldg_age).upper()]
        else:
            raise ValueError(
                "Building Age {} not recognized.".format('"' + str(bldg_age) + '"')
            )

class DFTypology(object):
    """Represents a group of buildings of the same typology in an urban area.
    
    Attributes:
        average_height: The average height of the buildings of this typology in meters.
        footprint_area: The footprint area of the buildings of this typology in square meteres.
        facade_area: The facade area of the buildings of this typology in square meters.
        bldg_program: A text string representing one of the 16 DOE building program types to be 
            used as a template for this typology.  Choose from the following options:
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
        bldg_age: A text string that sets the age of the buildings represented by this typology.  
            This is used to determine what constructions make up the walls, roofs, and windows 
            based on international building codes over the last several decades.  Choose from 
            the following options:
                Pre1980s
                1980sPresent
                NewConstruction
        fract_heat_to_canyon: A number from 0 to 1 that represents the fraction the building's waste 
            heat from air conditioning that gets rejected into the urban canyon (as opposed to 
            through rooftop equipment or into a ground source loop).  The default is set to 0.5.
        glz_ratio: An optional number from 0 to 1 that represents the fraction of the walls of the building typology
            that are glazed. If no value is input here, a default will be used that comes from the DoE building 
            template from the bldg_program and bldg_age.
    """
    
    def __init__(self, average_height, footprint_area, facade_area, bldg_program, 
                bldg_age, fract_heat_to_canyon=None, glz_ratio=None, roof_veg_fraction=None):
        """Initialize a dragonfly building typology"""
        # get dependencies
        self.bldgTypes = DFBuildingTypes()
        self.genChecks = GeneralChecks()
        
        # critical geometry parameters that all typologies must have.
        self._average_height = float(average_height)
        self._footprint_area = float(footprint_area)
        self._facade_area = float(facade_area)
        
        # critical program parameters that all typologies must have.
        self._bldg_program = self.bldgTypes.check_program(bldg_program)
        self._bldg_age = self.bldgTypes.check_age(bldg_age)
        
        # optional parameters with default values.
        if glz_ratio is not None:
            self._glz_ratio = self.genChecks.in_range(float(glz_ratio), 0, 1, 'glz_ratio')
        else:
            self._glz_ratio = 'Auto'
        if fract_heat_to_canyon is not None:
            self._fract_heat_to_canyon = self.genChecks.in_range(float(fract_heat_to_canyon), 0, 1, 'fract_heat_to_canyon')
        else:
            self._fract_heat_to_canyon = 0.5
    
    @classmethod
    def from_geometry(cls, bldg_breps, bldg_program, bldg_age, fract_heat_to_canyon=None, 
        glz_ratio=None):
        """Initialize a building typology from closed building brep geometry
        Args:
            bldg_breps: A list of closed rhino breps representing buildings of the typology.
            bldg_program: A text string representing one of the 16 DOE building program types to be 
                used as a template for this typology.
            bldg_age: A text string that sets the age of the buildings represented by this typology.
            fract_heat_to_canyon: A number from 0 to 1 that represents the fraction the building's waste 
                heat from air conditioning that gets rejected into the urban canyon (as opposed to 
                through rooftop equipment or into a ground source loop).  The default is set to 0.5.
        
        Returns:
            typology: The dragonfly typology object
            footprintBreps: A list of breps representing the footprints of the buildings.
            facadeBreps: A list of breps representing the exposed facade surfaces of the typology.
        """
        geometryLib = UWGGeometry()
        avgBldgHeight, footprintArea, facadeArea, footprintBreps, facadeBreps = geometryLib.calculateTypologyGeoParams(bldg_breps)
        
        typology = cls(avgBldgHeight, footprintArea, facadeArea, bldg_program, bldg_age, fract_heat_to_canyon, glz_ratio)
        
        return typology, footprintBreps, facadeBreps
    
    @property
    def average_height(self):
        """Return the average height of the building typology in meters."""
        return self._average_height
    
    @property
    def footprint_area(self):
        """Return the footprint of the buildings in the typology in square meters."""
        return self._footprint_area
    
    @property
    def facade_area(self):
        """Return the facade area of the buildings in the typology in square meters."""
        return self._facade_area
    
    @property
    def bldg_program(self):
        """Return the program of the buildings in the typology."""
        return self._bldg_program
    
    @property
    def bldg_age(self):
        """Return the construction time of buildings in the typology."""
        return self._bldg_age
    
    @property
    def fract_heat_to_canyon(self):
        """Return the fraction of the building's heat that is rejected to the urban canyon."""
        return self._fract_heat_to_canyon
    
    @property
    def glz_ratio(self):
        """Return the glazing ratio of the buildings in the typology."""
        return self._glz_ratio
    
    @property
    def isDFTypology(self):
        """Return True for DFTypology."""
        return True
    
    def __repr__(self):
        return 'Building Typology: ' + self._bldg_program + ", " + self._bldg_age + \
               '\n  Average Height: ' + str(int(self._average_height)) + " m" + \
               '\n  Footprint Area: ' + str(int(self._footprint_area)) + " m2" + \
               '\n  Facade Area: ' + str(int(self._facade_area)) + " m2" + \
               '\n-------------------------------------'

class DFCity(object):
    """Represents a an entire uban area inclluding buildings, pavement, vegetation, and traffic.
    
    Attributes:
        average_bldg_height: The average height of the buildings of the city in meters.
        site_coverage_ratio: A number between 0 and 1 that represents the fraction of the city terrain 
            the building footprints occupy.  It describes how close the buildings are to one another in the city.
        facade_to_site_ratio: A number that represents the ratio of vertical urban surface area [walls] to 
            the total terrain area of the city.  This value can be greater than 1.
        bldg_types: A list of text strings that represent the building programs and building ages in the city separated by a 
            comma (eg. MidRiseApartment,1980sPresent). Choose from the following 16 DOE building program types:
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
            ...and from the following building ages:
                Pre1980s
                1980sPresent
                NewConstruction
        bldg_type_ratios: A list of values with the same length as the bldg_types.  This list contains values between 0 and 1 
            that represent the fraction of the urban area occupied by each of the buildings in the bldg_types.  The 
            values in this list should sum to 1.
        traffic_parameters: A dragonfly TrafficPar object that defines the traffic within an urban area.
        tree_coverage_ratio: An number from 0 to 1 that defines the fraction of the entire urban area 
            (including both pavement and roofs) that is covered by trees.  The default is set to 0.
        grass_coverage_ratio: An number from 0 to 1 that defines the fraction of the entire urban area 
            (including both pavement and roofs) that is covered by grass/vegetation.  The default is set to 0.
        fract_heat_to_canyon: A number from 0 to 1 that represents the fraction the building's waste 
            heat from air conditioning that gets rejected into the urban canyon (as opposed to 
            through rooftop equipment or into a ground source loop).  The default is set to 0.5.
        glz_ratios: A list of values with the same length as the bldg_types.  This list contains values between 0 and 1 
            that represent the fraction of the walls in the city that are glazed. The default is to use a value that 
            comes from the DoE building template from the bldg_program and bldg_age.
        vegetation_parameters: A dragonfly VegetationPar object that defines the behaviour of vegetation within an urban area.
        pavement_parameters: A dragonfly PavementPar object that defines the makeup of pavement within the urban area.
        characteristic_length: A number representing the radius of a circle that encompasses the whole neighborhood in meters.
            The default is set to 500 m, which was found to be the recomendation for a typical mid-density urban area.
            Street, Michael A. (2013). Comparison of simplified models of urban climate for improved prediction of building 
            energy use in cities. Thesis (S.M. in Building Technology)--Massachusetts Institute of Technology, Dept. of Architecture,
            http://hdl.handle.net/1721.1/82284
    """
    
    def __init__(self, average_bldg_height, site_coverage_ratio, facade_to_site_ratio, bldg_types, 
                bldg_type_ratios, traffic_parameters, tree_coverage_ratio=None, grass_coverage_ratio=None, 
                fract_heat_to_canyon=None, glz_ratios=None, vegetation_parameters=None,
                pavement_parameters=None, characteristic_length=500):
        """Initialize a dragonfly city"""
        # get dependencies
        bldgTypes = DFBuildingTypes()
        genChecks = GeneralChecks()
        
        # critical geometry parameters that all cities must have.
        self._average_bldg_height = float(average_bldg_height)
        self._site_coverage_ratio = genChecks.in_range(float(site_coverage_ratio), 0, 1, 'site_coverage_ratio')
        self._facade_to_site_ratio = float(facade_to_site_ratio)
        
        # critical program parameters that all typologies must have.
        self._bldg_types = []
        for type in bldg_types:
            try:
                bldg_program, bldg_age = type.split(',')
                _bldg_program = bldgTypes.check_program(bldg_program)
                _bldg_age = bldgTypes.check_age(bldg_age)
                self._bldg_types.append(_bldg_program + ',' + _bldg_age)
            except:
                raise Exception (
                    "Building Type {} is not in the correct format of BuildingProgram,BuildingAge.".format('"' + str(type) + '"')
                )
        
        if genChecks.length_match(bldg_types, bldg_type_ratios, 'bldg_types', 'bldg_type_ratios') == True:
            self._bldg_type_ratios = [float(x) for x in bldg_type_ratios]
        if sum(self._bldg_type_ratios) != 1:
            raise Exception (
                    "Building Type ratios sum to {}.  They must sum to 1.".format(str(sum(self._bldg_type_ratios)))
                )
        
        # glazing ratios
        if glz_ratios is not None:
            if genChecks.length_match(bldg_types, glz_ratios, 'bldg_types', 'glz_ratios') == True:
                self._glz_ratios = glz_ratios
        else:
            self._glz_ratios = ['Auto' for x in bldg_types]
        
        # parameter objects that define things within the city
        if hasattr(traffic_parameters, 'isTrafficPar'):
            self._traffic_parameters = traffic_parameters
        else:
            genChecks.make_type_error('traffic_parameters', 'TrafficPar')
        if vegetation_parameters is not None:
            if hasattr(vegetation_parameters, 'isVegetationPar'):
                self._vegetation_parameters = vegetation_parameters
            else:
                genChecks.make_type_error('vegetation_parameters', 'VegetationPar')
        else:
            self._vegetation_parameters = DFVegetationPar()
        if pavement_parameters is not None:
            if hasattr(pavement_parameters, 'isPavementPar'):
                self._pavement_parameters = pavement_parameters
            else:
                genChecks.make_type_error('pavement_parameters', 'PavementPar')
        else:
            self._pavement_parameters = DFPavementPar()
        
        # vegetation coverage.
        if tree_coverage_ratio is not None:
            self._tree_coverage_ratio = genChecks.in_range(float(tree_coverage_ratio), 0, 1, 'tree_coverage_ratio')
        else:
            self._tree_coverage_ratio = 0
        
        if grass_coverage_ratio is not None:
            self._grass_coverage_ratio = genChecks.in_range(float(grass_coverage_ratio), 0, 1, 'grass_coverage_ratio')
        else:
            self._grass_coverage_ratio = 0
        
        # fraction of heat to canyon.
        if fract_heat_to_canyon is not None:
            self._fract_heat_to_canyon = genChecks.in_range(float(fract_heat_to_canyon), 0, 1, 'fract_heat_to_canyon')
        else:
            self._fract_heat_to_canyon = 0.5
        
        # characteristic length.
        self._characteristic_length = float(characteristic_length)
    
    @classmethod
    def from_typologies(cls, typologies, terrian, traffic_parameters, tree_coverage_ratio=None, 
        grass_coverage_ratio=None, vegetation_parameters=None, pavement_parameters=None):
        """Initialize a city from a list of building typologies
        Args:
            typologies: A list of dragonfly Typology objects.
            terrian: A dragonfly Terrain object.
            traffic_parameters: A dragonfly TrafficPar object that defines the traffic within an urban area.
            tree_coverage_ratio: An number from 0 to 1 that defines the fraction of the entire urban area 
                (including both pavement and roofs) that is covered by trees.  The default is set to 0.
            grass_coverage_ratio: An number from 0 to 1 that defines the fraction of the entire urban area 
                (including both pavement and roofs) that is covered by grass/vegetation.  The default is set to 0.
            vegetation_parameters: A dragonfly VegetationPar object that defines the behaviour of vegetation within an urban area.
            pavement_parameters: A dragonfly PavementPar object that defines the makeup of pavement within the urban area.
        
        Returns:
            city: The dragonfly city object
        """
        
        genChecks = GeneralChecks()
        utilities = Utilities()
        
        # pull the relevating info off of the building typologies
        footprintAreas = []
        facadeAreas = []
        bldgHeights = []
        bldgTypes = []
        glzRatios = []
        fractsToCanyon = []
        
        for bType in typologies:
            if hasattr(bType, 'isDFTypology'):
                footprintAreas.append(bType.footprint_area)
                facadeAreas.append(bType.facade_area)
                bldgHeights.append(bType.average_height)
                bldgTypes.append(bType.bldg_program + ',' + bType.bldg_age)
                glzRatios.append(bType.glz_ratio)
                fractsToCanyon.append(bType.fract_heat_to_canyon)
            else:
                genChecks.make_type_error('typology', 'Typology')
        
        # process the terrain surface.
        if hasattr(terrian, 'isDFTerrain'):
            terrainArea = terrian.area
        else:
            genChecks.make_type_error('terrian', 'Terrain')
        
        # compute the critical variables for the city
        avgBldgHeight, typologyRatios = utilities.weighted_average(bldgHeights, footprintAreas)
        bldgCoverage = sum(footprintAreas)/terrainArea
        facadeToSite = sum(facadeAreas)/terrainArea
        
        volWeights = [a*bldgHeights[i] for i, a in enumerate(footprintAreas)]
        weightedFractToCanyon, typVolRatios = utilities.weighted_average(fractsToCanyon, volWeights)
        
        # return the city object.
        return cls(avgBldgHeight, bldgCoverage, facadeToSite, bldgTypes, typologyRatios, 
            traffic_parameters, tree_coverage_ratio, grass_coverage_ratio, weightedFractToCanyon,
            glzRatios, vegetation_parameters, pavement_parameters, terrian.characteristic_length)
    
    @property
    def average_bldg_height(self):
        """Return the average height of the buildings in the city."""
        return self._average_bldg_height
    
    @property
    def site_coverage_ratio(self):
        """Return the site coverage ratio of buildings to terrain."""
        return self._site_coverage_ratio
    
    @property
    def facade_to_site_ratio(self):
        """Return the facade to site ratio."""
        return self._facade_to_site_ratio
    
    @property
    def bldg_types(self):
        """Return a list of building types in the city."""
        return self._bldg_program
    
    @property
    def bldg_type_ratios(self):
        """Return the a list of ratios corresponding to the building types."""
        return self._bldg_type_ratios
    
    @property
    def traffic_parameters(self):
        """Return the traffic parameter object that describes the city's traffic."""
        return self._traffic_parameters
    
    @property
    def vegetation_parameters(self):
        """Return the vegetation parameter object that describes the city's vegetation."""
        return self._vegetation_parameters
    
    @property
    def pavement_parameters(self):
        """Return the pavement parameter object that describes the city's pavement."""
        return self._pavement_parameters
    
    @property
    def tree_coverage_ratio(self):
        """Return the ratio of the entire site area of the city covered in trees."""
        return self._tree_coverage_ratio
    
    @property
    def grass_coverage_ratio(self):
        """Return the ratio of the entire site area of the city covered in grass."""
        return self._grass_coverage_ratio
    
    @property
    def fract_heat_to_canyon(self):
        """Return the fraction of the building's heat that is rejected to the urban canyon."""
        return self._fract_heat_to_canyon
    
    @property
    def glz_ratios(self):
        """Return a list of the the glazing ratios for each of the typologies in the city."""
        return self._glz_ratios
    
    @property
    def characteristic_length(self):
        """Returns the caracteristic length of the city."""
        return self._characteristic_length
    
    @property
    def isDFCity(self):
        """Return True for DFCity."""
        return True
    
    def __repr__(self):
        typologyList = ''
        for i, x in enumerate(self._bldg_types):
            typologyList = typologyList + '\n     ' + str(round(self._bldg_type_ratios[i], 2)) + ' - ' + x
        return 'Dragonfly City: ' + \
               '\n  Average Bldg Height: ' + str(int(self._average_bldg_height)) + " m" + \
               '\n  Site Coverage Ratio: ' + str(round(self._site_coverage_ratio, 2)) + \
               '\n  Facade-to-Site Ratio: ' + str(round(self._facade_to_site_ratio, 2)) + \
               '\n  Tree Coverage Ratio: ' + str(round(self._tree_coverage_ratio, 2)) + \
               '\n  Grass Coverage Ratio: ' + str(round(self._grass_coverage_ratio, 2)) + \
               '\n  ------------------------' + \
               '\n  Building Typologies: ' + typologyList


class DFTerrain(object):
    """Represents the terrain on which an urban area sits.
    
    Attributes:
        area: The area of the urban terrain surface in square meters (projected into the XY plane).
        characteristic_length:  A number representing the radius of a circle that encompasses the 
            whole neighborhood in meters.  If no value is input here, it will be auto-calculated 
            assuming that the area above is cicular.
    """
    
    def __init__(self, area, characteristic_length=None):
        """Initialize a dragonfly terrain surface"""
        self._area = float(area)
        
        if characteristic_length is not None:
            self._characteristic_length = float(characteristic_length)
        else:
            self._characteristic_length = math.sqrt(self._area/math.pi)
    
    @classmethod
    def from_geometry(cls, terrainSrfs):
        """Initialize a dragonfly terrain surface from a list of terrain breps
        Args:
            terrainSrfs: A list of Rhino surfaces representing the terrian.
        
        Returns:
            terrain: The dragonfly terrain object.
            surfaceBreps: The srfBreps representing the terrain (projected into the XY plane).
        """
        geometryLib = UWGGeometry()
        surfaceArea, surfaceBreps = geometryLib.calculateFootprints(terrainSrfs)
        terrain = cls(surfaceArea)
        
        return terrain, surfaceBreps
    
    @property
    def area(self):
        """Return the area of the terrain surface in the XY plane."""
        return self._area
    
    @property
    def characteristic_length(self):
        """Return the characteristic length."""
        return self._characteristic_length
    
    @property
    def isDFTerrain(self):
        """Return True for DFTerrain."""
        return True
    
    def __repr__(self):
        return 'Terrain Surface: ' + \
               '\n  Area: ' + str(int(self._area)) + " m2" + \
               '\n  Radius: ' + str(int(self._characteristic_length)) + " m"

class DFVegetation(object):
    """Represents vegetation (either grass or trees) within an urban area.
    
    Attributes:
        area: The area of the urban terrain covered by the vegetation in square meters 
            (projected into the XY plane).
        is_trees: A boolean value that denotes whether the vegetation object represents 
            trees (True) or grass (False).
    """
    
    def __init__(self, area, is_trees=False):
        """Initialize a dragonfly vegetation object"""
        self._area = float(area)
        self._is_trees = bool(is_trees)
    
    @classmethod
    def from_geometry(cls, veg_breps, is_trees=False):
        """Initialize a dragonfly tree object from a list of closed tree breps
        Args:
            veg_breps: A list of closed Rhino breps representing the tree canopy.
            is_trees: A boolean value that denotes whether the vegetation object 
                represents trees (True) or grass (False).
        
        Returns:
            vegetation: The dragonfly vegetation object.
            projected_breps: The veg_breps projected into the XY plane.
        """
        geometryLib = UWGGeometry()
        surfaceArea, projected_breps = geometryLib.calculateFootprints(veg_breps, is_trees)
        vegetation = cls(surfaceArea, is_trees)
        
        return vegetation, projected_breps
    
    @property
    def area(self):
        """Return the area of the vegetation in the XY plane."""
        return self._area
    
    @property
    def is_trees(self):
        """Return a true/false value depending on whether the vegetation represents trees/grass."""
        return self._is_trees
    
    @property
    def isDFVegetation(self):
        """Return True for DFDFVegetation."""
        return True
    
    def computeCoverage(self, terrain):
        """Initialize a dragonfly tree object from a list of closed tree breps
        Args:
            terrain: A dragonfly terrin object with which to compute coverage.
        
        Returns:
            coverage: A number between 0 and 1 representing the fraction of 
                the terrain covered by the vegetation.
        """
        genChecks = GeneralChecks()
        if hasattr(terrain, 'isDFTerrain'):
            coverage = genChecks.in_range((self._area/terrain.area), 0, 1, 'vegetation_coverage')
        else:
            genChecks.make_type_error('terrian', 'Terrain')
        
        return coverage
    
    def __repr__(self):
        vegType = 'Trees' if self._is_trees else 'Grass'
        return 'Vegetation: ' + vegType + \
               '\n  Area: ' + str(int(self._area)) + " m2"

class DFTrafficPar(object):
    """Represents the traffic within an urban area.
    
    Attributes:
        sensible_heat: A number representing the maximum sensible anthropogenic heat flux of the urban area 
            in watts per square meter. This input is required.
        latent_heat:  A number representing the maximum latent anthropogenic heat flux of the urban area 
            in watts per square meter. Default is set to 0.
        weekday_schedule: A list of 24 fractional values that will be multiplied by the sensible_heat
            and latent_heat to produce hourly values for heat on the weekday of the simulation.  The default is
            a typical traffic schedule for a commerical area.
        saturday_schedule: A list of 24 fractional values that will be multiplied by the sensible_heat
            and latent_heat to produce hourly values for heat on Saturdays of the simulation.  The default is
            a typical traffic schedule for a commerical area.
        sunday_schedule: A list of 24 fractional values that will be multiplied by the sensible_heat
            and latent_heat to produce hourly values for heat on Sundays of the simulation.  The default is
            a typical traffic schedule for a commerical area.
    """
    
    def __init__(self, sensible_heat, latent_heat=None, weekday_schedule=[], 
                saturday_schedule=[], sunday_schedule=[]):
        """Initialize dragonfly traffic parameters"""
        # get dependencies
        self.genChecks = GeneralChecks()
        
        self._sensible_heat = float(sensible_heat)
        
        if latent_heat is not None:
            self._latent_heat = latent_heat
        else:
            self._latent_heat = 0
        
        if weekday_schedule != []:
            print weekday_schedule
            self._weekday_schedule = self.checkSchedule(weekday_schedule)
        else:
            self._weekday_schedule = [0.2,0.2,0.2,0.2,0.2,0.4,0.7,0.9,0.9,0.6,0.6, \
                0.6,0.6,0.6,0.7,0.8,0.9,0.9,0.8,0.8,0.7,0.3,0.2,0.2]
        
        if saturday_schedule != []:
            self._saturday_schedule = self.checkSchedule(saturday_schedule)
        else:
            self._saturday_schedule = [0.2,0.2,0.2,0.2,0.2,0.3,0.5,0.5,0.5,0.5,0.5, \
                0.5,0.5,0.5,0.6,0.7,0.7,0.7,0.7,0.5,0.4,0.3,0.2,0.2]
        
        if sunday_schedule != []:
            self._sunday_schedule = self.checkSchedule(sunday_schedule)
        else:
            self._sunday_schedule = [0.2,0.2,0.2,0.2,0.2,0.3,0.4,0.4,0.4,0.4,0.4,0.4, \
                0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.3,0.3,0.2,0.2]
    
    @property
    def sensible_heat(self):
        """Return the max sensible heat flux of the traffic."""
        return self._sensible_heat
    
    @property
    def latent_heat(self):
        """Return the max latent heat of the traffic."""
        return self._latent_heat
    
    @property
    def weekday_schedule(self):
        """Return the weekday traffic schedule as a list."""
        return self._weekday_schedule
    
    @property
    def saturday_schedule(self):
        """Return the Saturday traffic schedule as a list."""
        return self._saturday_schedule
    
    @property
    def sunday_schedule(self):
        """Return the Sunday traffic schedule as a list."""
        return self._sunday_schedule
    
    @property
    def isTrafficPar(self):
        """Return True for isTrafficPar."""
        return True
    
    def __repr__(self):
        return 'Traffic Parameters: ' + \
               '\n  Sensible Heat: ' + str(self._sensible_heat) + \
               '\n  Latent Heat: ' + str(self._latent_heat)
    
    def checkSchedule(self, schedule):
        if len(schedule) is 24:
            return [fixRange(x,0,1) for x in schedule]
        else:
            raise Exception(
                "Current schedule has length " + str(len(schedule)) + \
                ". Schedules must be lists of 24 values."
            )
    
    def fixRange(self, val, low, high):
        if val > high:
            return high
        elif val < low:
            return low
        else:
            return float(val)

class DFVegetationPar(object):
    """Represents the behaviour of vegetation within an urban area.
    
    Attributes:
        vegetation_start_month: An integer from 1 to 12 that represents the month at which 
            vegetation begins to affect the urban climate.  The default is set to 0, which will 
            automatically determine the vegetation start month by analyzing the epw to see which 
            months have an average monthly temperature above 10 C.
        vegetation_end_month: An integer from 1 to 12 that represents the last month at which 
            vegetation affect the urban climate.  The default is set to 0, which will 
            automatically determine the vegetation end month by analyzing the epw to see which 
            months have an average monthly temperature above 10 C.
        vegetation_albedo: A number between 0 and 1 that represents the ratio of reflected radiation 
            from vegetated surfaces to incident radiation upon them.  If no value is input here, the 
            UWG will assume a typical vegetation albedo of 0.25.
        tree_latent_fraction: A number between 0 and 1 that represents the the fraction of absorbed 
            solar energy by trees that is given off as latent heat (evapotranspiration). This affects 
            the moisture balance and temperature in the urban area.  If no value is input here, a typical 
            value of 0.7 will be assumed.
        grass_latent_fraction: A number between 0 and 1 that represents the the fraction of absorbed solar 
            energy by grass that is given off as latent heat (evapotranspiration). This affects the 
            moisture balance and temperature in the urban area.  If no value is input here, a typical 
            value of 0.5 will be assumed.
    """
    
    def __init__(self, vegetation_start_month=None, vegetation_end_month=None, vegetation_albedo=None, 
                tree_latent_fraction=None, grass_latent_fraction=None):
        """Initialize dragonfly vegetation parameters"""
        # get dependencies
        self.genChecks = GeneralChecks()
        
        if vegetation_start_month is not None:
            self._vegetation_start_month = self.genChecks.in_range(int(vegetation_start_month), 0, 12, 'vegetation_start_month')
        else:
            self._vegetation_start_month = 0
        
        if vegetation_end_month is not None:
            self._vegetation_end_month = self.genChecks.in_range(int(vegetation_end_month), 0, 12, 'vegetation_end_month')
        else:
            self._vegetation_end_month = 0
        
        if vegetation_albedo is not None:
            self._vegetation_albedo = self.genChecks.in_range(float(vegetation_albedo), 0, 1, 'vegetation_albedo')
        else:
            self._vegetation_albedo = 0.25
        
        if tree_latent_fraction is not None:
            self._tree_latent_fraction = self.genChecks.in_range(float(tree_latent_fraction), 0, 1, 'tree_latent_fraction')
        else:
            self._tree_latent_fraction = 0.7
        
        if grass_latent_fraction is not None:
            self._grass_latent_fraction = self.genChecks.in_range(float(grass_latent_fraction), 0, 1, 'grass_latent_fraction')
        else:
            self._grass_latent_fraction = 0.5
        
        # dictionary of months for start and end month
        self.monthsDict = {
            0: 'Autocalc',
            1: 'Jan',
            2: 'Feb',
            3: 'Mar',
            4: 'Apr',
            5: 'May',
            6: 'Jun',
            7: 'Jul',
            8: 'Aug',
            9: 'Sep',
            10: 'Oct',
            11: 'Nov',
            12: 'Dec' 
            }
    
    @property
    def vegetation_start_month(self):
        """Return the vegetation start month."""
        return self._vegetation_start_month
    
    @property
    def vegetation_end_month(self):
        """Return the vegetation end month."""
        return self._vegetation_end_month
    
    @property
    def vegetation_albedo(self):
        """Return the vegetation albedo."""
        return self._vegetation_albedo
    
    @property
    def tree_latent_fraction(self):
        """Return the tree latent fraction."""
        return self._tree_latent_fraction
    
    @property
    def grass_latent_fraction(self):
        """Return the grass latent fraction."""
        return self._grass_latent_fraction
    
    @property
    def isVegetationPar(self):
        """Return True for isVegetationPar."""
        return True
    
    def __repr__(self):
        return 'Vegetation Parameters: ' + \
               '\n  Vegetation Time: ' + self.monthsDict[self._vegetation_start_month] + ' - ' + self.monthsDict[self._vegetation_end_month] +\
               '\n  Albedo: ' + str(self._vegetation_albedo) + \
               '\n  Tree | Grass Latent: ' + str(self._tree_latent_fraction) + ' | ' + str(self._grass_latent_fraction)

class DFPavementPar(object):
    """Represents the makeup of pavement within the urban area.
    
    Attributes:
        albedo: A number between 0 and 1 that represents the surface albedo (or reflectivity) 
            of the pavement.  The default is set to 0.1, which is typical of fresh asphalt.
        thickness: A number that represents the thickness of the pavement material in meters (m).  
            The default is set to 0.5 meters.
        conductivity: A number representing the conductivity of the pavement material in W/m-K.  
            The default is set to 1 W/m-K, which is typical of asphalt.
        volumetric_heat_capacity: A number representing the volumetric heat capacity of 
            the pavement material in J/m3-K.  This is the number of joules needed to raise 
            one cubic meter of the material by 1 degree Kelvin.  The default is set to 
            1,600,000 J/m3-K, which is typical of asphalt.
    """
    
    def __init__(self, albedo=None, thickness=None, conductivity=None, volumetric_heat_capacity=None):
        """Initialize dragonfly pavement parameters"""
        # get dependencies
        self.genChecks = GeneralChecks()
        
        if albedo is not None:
            self._albedo = self.genChecks.in_range(float(albedo), 0, 1, 'albedo')
        else:
            self._albedo = 0.1
        if thickness is not None:
            self._thickness = float(thickness)
        else:
            self._thickness = 0.5
        if conductivity is not None:
            self._conductivity = float(conductivity)
        else:
            self._conductivity = 1
        if volumetric_heat_capacity is not None:
            self._volumetric_heat_capacity = float(volumetric_heat_capacity)
        else:
            self._volumetric_heat_capacity = 1600000
    
    @property
    def albedo(self):
        """Return the albedo."""
        return self._albedo
    
    @property
    def thickness(self):
        """Return the thickness."""
        return self._thickness
    
    @property
    def conductivity(self):
        """Return the conductivity."""
        return self._conductivity
    
    @property
    def volumetric_heat_capacity(self):
        """Return the volumetric heat capacity."""
        return self._volumetric_heat_capacity
    
    @property
    def isPavementPar(self):
        """Return True for isPavementPar."""
        return True
    
    def __repr__(self):
        return 'Pavement Parameters: ' + \
               '\n  Albedo: ' + str(self._albedo) + \
               '\n  Thickness: ' + str(self._thickness) + \
               '\n  Conductivity: ' + str(self._conductivity) + \
               '\n  Vol Heat Capacity: ' + str(self._volumetric_heat_capacity)



try:
    checkIn.checkForUpdates(True)
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
            if os.path.isdir("C:\\ladybug" + "\\UWG\\"):
                folders.UWGPath = "C:\\ladybug" + "\\UWG\\"
            else:
                # Try to download these files in the background.
                try:
                    ## download File
                    print 'Downloading UWG to ', "C:\\ladybug\\UWG\\"
                    updatedLink = "https://github.com/hansukyang/UWG_Matlab/raw/master/ArchivedCodes/UWG.zip"
                    localFilePath = "C:\\ladybug" + 'UWG.zip'
                    client = System.Net.WebClient()
                    client.DownloadFile(updatedLink, localFilePath)
                    #Unzip the file
                    unzip(localFilePath, "C:\\ladybug")
                    os.rename("C:\\ladybug" + '\\UWG\\UWGEngine_mcr\\META\\', "C:\\ladybug" + '\\UWG\\UWGEngine_mcr\\.META\\')
                    folders.UWGPath = "C:\\ladybug" + "\\UWG\\"
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
        sc.sticky["dragonfly_BuildingTypology"] = DFTypology
        sc.sticky["dragonfly_City"] = DFCity
        sc.sticky["dragonfly_Terrain"] = DFTerrain
        sc.sticky["dragonfly_Vegetation"] = DFVegetation
        sc.sticky["dragonfly_TrafficPar"] = DFTrafficPar
        sc.sticky["dragonfly_VegetationPar"] = DFVegetationPar
        sc.sticky["dragonfly_PavementPar"] = DFPavementPar
        
        
        print "Hi " + os.getenv("USERNAME")+ "!\n" + \
              "Dragonfly is Flying! Vviiiiiiizzz...\n\n" + \
              "Default path is set to: " + sc.sticky["Dragonfly_DefaultFolder"] + "\n" + \
              "UWGEngine path is set to: " + sc.sticky["dragonfly_folders"]["UWGPath"]
        
        # push ladybug component to back
        ghenv.Component.OnPingDocument().SelectAll()
        ghenv.Component.Attributes.Selected = False
        ghenv.Component.OnPingDocument().BringSelectionToTop()
        ghenv.Component.OnPingDocument().DeselectAll()