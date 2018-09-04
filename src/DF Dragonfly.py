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
Provided by Dragonfly 0.0.03
    Args:
        default_folder_: Optional input for Dragonfly default folder.
                       If empty default folder will be set to C:\ladybug or C:\Users\%USERNAME%\AppData\Roaming\Ladybug\
    Returns:
        report: ...
"""

ghenv.Component.Name = "DF Dragonfly"
ghenv.Component.NickName = 'Dragonfly'
ghenv.Component.Message = 'VER 0.0.03\nJUL_11_2018'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "0 | Dragonfly"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import Rhino as rc
import scriptcontext as sc
import Grasshopper.Kernel as gh
import Grasshopper
import math
import os
import System
import datetime
import zipfile
import cPickle
from copy import deepcopy

System.Net.ServicePointManager.SecurityProtocol = System.Net.SecurityProtocolType.Tls12
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
                              " Default fodelr cannot be set.\nUse default_folder_ to set the path to another folder and try again!" + \
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
                        'Try to set it up manually using default_folder_ input.'
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
                not param.NickName.endswith("_"):
                if not param.VolatileDataCount:
                    warning = "Input parameter %s failed to collect data!"%param.NickName
                    GHComponent.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
                    isInputMissing = True

        return isInputMissing


class Geometry(object):

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

    def calculate_area(self, area_srfs):
        """Calculate the area of a surface.

        Args:
            area_srfs: A Rhino surface.

        Returns:
            result: The area of the surface.
        """
        return rc.Geometry.AreaMassProperties.Compute(area_srfs).Area

    def unionAllBreps(self, bldgBreps):
        """Unioned breps into one so that correct facade areas can be computed.

        Args:
            bldgBreps: A list of closed rhino brep representing a building.

        Returns:
            result: The building breps after being unioned.
        """
        try:
            union = rc.Geometry.Brep.CreateBooleanUnion(bldgBreps, sc.doc.ModelAbsoluteTolerance)
            if union is not None:
                return union
            else:
                return bldgBreps
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
            brepCopy = deepcopy(srfBrep)
            brepCopy.Transform(self.groundProjection)
            footprintBreps.append(brepCopy)
            if solid == True:
                footprintArea += (rc.Geometry.AreaMassProperties.Compute(brepCopy).Area/2)
            else:
                footprintArea += rc.Geometry.AreaMassProperties.Compute(brepCopy).Area

        footprintArea = footprintArea * self.areaConversionFac

        return footprintArea, footprintBreps

    def getFloorBreps(self, buildingMass, floorHeight=3.05):
        """Extracts a series of surfaces representing the interior floors of a building

        Args:
            buildingMass: A closed brep representing the building volume
            floorHeight: The average floor-to-floor height between floors in meters.
                The default is 3.05 meters

        Returns:
            floorArea: The total floor area of the building.
            floorBreps: A list of breps representing the floors of the building.
        """

        # draw a bounding box around the mass and use the lowest Z point to set the base point.
        massBB = buildingMass.GetBoundingBox(rc.Geometry.Plane.WorldXY)
        fullRange = massBB.Max.Z - massBB.Min.Z
        numCrvs = int(math.floor(fullRange / floorHeight))
        flrRanges = range(0, numCrvs)
        flrHeights = [x*floorHeight + massBB.Min.Z for x in flrRanges]

        # get the floor area curve at each of the floor heights.
        floorBreps = []
        floorArea = 0
        for count, h in enumerate(flrHeights):
            floorBasePt = rc.Geometry.Point3d(0,0,h)
            sectionPlane = rc.Geometry.Plane(floorBasePt, rc.Geometry.Vector3d.ZAxis)
            floorCrvs = rc.Geometry.Brep.CreateContourCurves(buildingMass, sectionPlane)
            try:
                floorBrep = rc.Geometry.Brep.CreatePlanarBreps(floorCrvs, sc.doc.ModelAbsoluteTolerance)
            except TypeError:
                floorBrep = rc.Geometry.Brep.CreatePlanarBreps(floorCrvs)
            floorArea += rc.Geometry.AreaMassProperties.Compute(floorBrep).Area
            floorBreps.extend(floorBrep)

        return floorArea, floorBreps

    def isGeoEquivalent(self, surface1, surface2):
        """ Checks whether the area, XY centerpoint and XY first point match between two surfaces.

        Args:
            surface1: First surface to check.
            surface1: Second surface to check.

        Returns:
            isEquivalent:A boolean value indicating whether surface1 is geometrically equivalent to surface 2.
        """

        # check wether the center points match within tolerance.
        tol = sc.doc.ModelAbsoluteTolerance
        surface1am = rc.Geometry.AreaMassProperties.Compute(surface1)
        surface2am = rc.Geometry.AreaMassProperties.Compute(surface2)
        srf1Cent = surface1am.Centroid
        srf2Cent = surface2am.Centroid
        if srf1Cent.X <= srf2Cent.X + tol and srf1Cent.X >= srf2Cent.X - tol and srf1Cent.Y <= srf2Cent.Y + tol and srf1Cent.Y >= srf2Cent.Y - tol:
            pass
        else:
            return False

        # check whether areas match within tolerance
        areaTol = tol*tol
        srf1Area = surface1am.Area
        srf2Area = surface2am.Area
        if srf1Area <= srf2Area + areaTol and srf1Area >= srf2Area - areaTol:
            pass
        else:
            return False

        # check wether the point at start matches within tolerance
        pt1 = surface1.Edges[0].PointAtStart
        pt2 = surface2.Edges[0].PointAtStart
        if pt1.X <= pt2.X + tol and pt1.X >= pt2.X - tol and pt1.Y <= pt2.Y + tol and pt1.Y >= pt2.Y - tol:
            pass
        else:
            return False

        return True

    def calculateBldgFootprint(self, floorBreps):
        """Extracts building footprint and footprint area

        Args:
            floorBreps: A list of breps representing the floors of the building.

        Returns:
            footprintArea: The footprint area of the building.
            footprintBrep: A Brep representing the footprint of the building in Rhino units.
        """
        # check to be sure that there are floors
        if len(floorBreps) == 0:
            return 0, None

        # grab all unique breps
        uniqueBreps = [floorBreps[0]]
        for brep1 in floorBreps[1:]:
            matchFound = False
            for brep2 in uniqueBreps:
                if self.isGeoEquivalent(brep1, brep2):
                    matchFound = True
            if matchFound == False:
                uniqueBreps.append(brep1)

        # check to be sure all unique breps are facing up (necessary for a clean boolean union).
        for brep in uniqueBreps:
            centerPt, normalVector = self.getSrfCenPtandNormal(brep)
            if normalVector.Z < 0:
                brep.Flip()

        # union any remaining surfaces.
        if len(uniqueBreps) > 1:
            projectedBreps = []
            for brep in uniqueBreps:
                brepCopy = deepcopy(brep)
                brepCopy.Transform(self.groundProjection)
                projectedBreps.append(brepCopy)

            footprintBrep = rc.Geometry.Brep.CreateBooleanUnion(projectedBreps, sc.doc.ModelAbsoluteTolerance)
            if footprintBrep is not None:
                footprintBrep = footprintBrep[0]
            else:
                footprintBrep = projectedBreps[0]
            footprintCurves = footprintBrep.DuplicateNakedEdgeCurves(True, True)
            footprintOutline = rc.Geometry.Curve.JoinCurves(footprintCurves, sc.doc.ModelAbsoluteTolerance)
            try:
                footprintBrep = rc.Geometry.Brep.CreatePlanarBreps(footprintOutline, sc.doc.ModelAbsoluteTolerance)[0]
            except TypeError:
                footprintBrep = rc.Geometry.Brep.CreatePlanarBreps(footprintOutline)[0]
        else:
            footprintBrep = deepcopy(uniqueBreps[0])
            footprintBrep.Transform(self.groundProjection)

        # calculate area
        footprintArea = rc.Geometry.AreaMassProperties.Compute(footprintBrep).Area

        return footprintArea, footprintBrep

    def extractBldgHeight(self, bldgBrep):
        """Extracts building height

        Args:
            bldgBrep: A closed rhino brep representing a building.

        Returns:
            bldgHeight: The height of the building.
        """

        bldgBBox = rc.Geometry.Brep.GetBoundingBox(bldgBrep, rc.Geometry.Plane.WorldXY)
        bldgHeight = bldgBBox.Max.Z - bldgBBox.Min.Z

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

    def calculateTypologyGeoParams(self, bldgBreps, floorHeight=3.05, maxRoofAngle=45, maxFloorAngle=60):
        """Extracts all properties needed to create a typology from closed solid building breps.

        Args:
            bldgBreps: A list of closed rhino brep representing buildings of the same typology.
            floorHeight: The average floor-to-floor height between floors in meters.
                The default is 3.05 meters
            maxRoofAngle: The roof normal angle from the positive Z axis (in degrees) beyond
                which a surface is no longer considered a roof. Default is 45.
            maxFloorAngle: The floor normal angle from the negative Z axis (in degrees) beyond
                which a surface is no longer considered a floor. Default is 60.

        Returns:
            avgBldgHeight: The average height of the buildings in the typology
            footprintArea: The footprint area of the buildings in this typology.
            floorArea: The total interior floor area of the buildings.
            facadeArea: The facade are of the buildings in this typology.
            footprintBreps: A list of breps representing the footprints of the buildings.
            floorBreps: A list of breps representing the floors of the buildings.
            facadeBreps: A list of breps representing the exposed facade surfaces of the typology.
        """
        # default floor height
        if floorHeight is None:
            floorHeight = 3.05

        # lists of outputs to be filled.
        bldgHeights = []
        footprintAreas = []
        footprintBreps = []
        floorAreas = []
        floorBreps = []

        # extract data from the geometries
        for i, bldgBrep in enumerate(bldgBreps):
            # check that the geometry is closed
            assert (bldgBrep.IsSolid == True),"Brep {} in bldgBreps is not closed.".format(str(i))

            # get the building height
            bldgHeights.append(self.extractBldgHeight(bldgBrep))

            # get the floor area
            flrA, flrBrep = self.getFloorBreps(bldgBrep, floorHeight)
            floorAreas.append(flrA)
            floorBreps.extend(flrBrep)

            # get the footprint area
            ftpA, ftpBrep = self.calculateBldgFootprint(flrBrep)
            footprintAreas.append(ftpA)
            if ftpBrep is not None:
                footprintBreps.append(ftpBrep)

        # compute the facade area of all of the building breps after they have been boolean unioned.
        unionedBreps = self.unionAllBreps(bldgBreps)
        facadeArea, facadeBreps = self.extractBldgFacades(unionedBreps, maxRoofAngle, maxFloorAngle)

        # calculate the final metrics
        floorArea = sum(floorAreas)
        footprintArea = sum(footprintAreas)
        footprintWeights = [(y/footprintArea) for y in footprintAreas]
        avgBldgHeight = sum([x*footprintWeights[i] for i,x in enumerate(bldgHeights)])

        # account for Rhino model units.
        avgBldgHeight = avgBldgHeight * self.linearConversionFac
        footprintArea = footprintArea * self.areaConversionFac
        facadeArea = facadeArea * self.areaConversionFac

        return avgBldgHeight, footprintArea, floorArea, facadeArea, footprintBreps, floorBreps, facadeBreps

    def calculateFootprintGeoParams(self, footprint_breps):
        """Extracts all properties needed to create a typology from footprint breps.

        Args:
            footprint_breps: A list of surface rhino breps representing the building footprints of the typology.

        Returns:
            footprint_area: The footprint area of the buildings in this typology.
            perimeter_length: The length of the exterior-exposed perimeters of the footprints.
            perimeter_curves: The exterior-exposed curves of the footprints.
        """
        # join the footprint breps
        joined_footprints = rc.Geometry.Brep.JoinBreps(footprint_breps, sc.doc.ModelAbsoluteTolerance)

        # extract the relevant paramters.
        footprint_area = 0
        perimeter_length = 0
        perimeter_curves = []
        for f_print in joined_footprints:
            footprint_area += rc.Geometry.AreaMassProperties.Compute(f_print).Area
            perim_cs = rc.Geometry.Curve.JoinCurves(f_print.DuplicateNakedEdgeCurves(True, True))
            for crv in perim_cs:
                perimeter_length += crv.GetLength()
            perimeter_curves.extend(perim_cs)

        # account for Rhino model units.
        footprint_area = footprint_area * self.areaConversionFac
        perimeter_length = perimeter_length * self.linearConversionFac

        return footprint_area, perimeter_length, perimeter_curves

class Utilities(object):

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

    def checkSchedule(self, schedule):
        if len(schedule) == 24:
            return [self.in_range(x, 0, 1, 'schedule value') for x in schedule]
        else:
            raise Exception(
                "Current schedule has length " + str(len(schedule)) + \
                ". Daily schedules must be lists of 24 values."
            )

    def fixRange(self, val, low, high):
        if val > high:
            return high
        elif val < low:
            return low
        else:
            return float(val)

class BuildingTypes(object):

    def __init__(self, readDOE_file_path):
        """Class that contains all of the accepted building typologies and contruction years"""

        # load up all of the building characteristcs from the urban weather generator pickle file.
        if not os.path.exists(readDOE_file_path):
            raise Exception("readDOE.pkl file: '{}' does not exist.".format(readDOE_file_path))
        readDOE_file = open(readDOE_file_path, 'rb') # open pickle file in binary form
        self.refDOE = cPickle.load(readDOE_file)
        self.refBEM = cPickle.load(readDOE_file)
        readDOE_file.close()

        # dictionary to go from building programs to numbers understood by the uwg.
        self.bldgtype = {
            'FullServiceRestaurant': 0,
            'Hospital': 1,
            'LargeHotel': 2,
            'LargeOffice': 3,
            'MedOffice': 4,
            'MidRiseApartment': 5,
            'OutPatient': 6,
            'PrimarySchool': 7,
            'QuickServiceRestaurant': 8,
            'SecondarySchool': 9,
            'SmallHotel': 10,
            'SmallOffice': 11,
            'StandAloneRetail': 12,
            'StripMall': 13,
            'SuperMarket': 14,
            'Warehouse':15
            }

        # dictionary to go from construction era to numbers understood by the uwg.
        self.builtera = {
            'Pre1980s':0,
            '1980sPresent':1,
            'NewConstruction':2
            }

        # dictionary to go from climate zone numbers understood by the uwg to a human-readable format.
        self.zonetype = {
            0: '1A',
            1: '2A',
            2: '2B',
            3: '3A',
            4: '3B-CA',
            5: '3B',
            6: '3C',
            7: '4A',
            8: '4B',
            9: '4C',
            10: '5A',
            11: '5B',
            12: '6A',
            13: '6B',
            14: '7',
            15: '8'
            }

        # dictionary of acceptable ASHRAE climate zone inputs.
        self.zoneconverter = {
            '1A': 0,
            '2A': 1,
            '2B': 2,
            '3A': 3,
            '3B-CA': 4,
            '3B': 5,
            '3C': 6,
            '4A': 7,
            '4B': 8,
            '4C': 9,
            '5A': 10,
            '5B': 11,
            '6A': 12,
            '6B': 13,
            '7': 14,
            '8': 15,

            '1': 0,
            '2': 1,
            '3': 3,
            '4': 7,
            '5': 10,
            '6': 12,

            '1B': 0,
            '1C': 0,
            '2C': 1,
            '5C': 10,
            '6C': 12,
            '7A': 14,
            '7B': 14,
            '7C': 14,
            '8A': 15,
            '8B': 15,
            '8C': 15
        }

        # dictionary to go from uwg building type to Dragonfly convention.
        self.uwg_bldg_type = {
            'FullServiceRestaurant': 'FullServiceRestaurant',
            'Hospital': 'Hospital',
            'LargeHotel': 'LargeHotel',
            'LargeOffice': 'LargeOffice',
            'MedOffice': 'MedOffice',
            'MidRiseApartment': 'MidRiseApartment',
            'OutPatient': 'OutPatient',
            'PrimarySchool': 'PrimarySchool',
            'QuickServiceRestaurant': 'QuickServiceRestaurant',
            'SecondarySchool': 'SecondarySchool',
            'SmallHotel': 'SmallHotel',
            'SmallOffice': 'SmallOffice',
            'StandAloneRetail': 'StandAloneRetail',
            'StripMall': 'StripMall',
            'SuperMarket': 'SuperMarket',
            'WareHouse': 'Warehouse'
            }

        # dictionary to go from uwg construction era to Dragonfly convention.
        self.uwg_built_era = {
            'Pre80': 'Pre1980s',
            'Pst80': '1980sPresent',
            'New': 'NewConstruction'
            }

        # dictionary of acceptable building program inputs.
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

        # dictionary of acceptable building ages.
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
        assert isinstance(bldg_program, str), 'bldg_program must be a text string got {}'.format(type(bldg_program))
        assert bldg_program.upper() in self.programsDict.keys(), "bldg_program {} is not recognized as a valid program.".format('"' + bldg_program + '"')
        return self.programsDict[str(bldg_program).upper()]

    def check_age(self, bldg_age):
        assert isinstance(bldg_age, str), 'bldg_age must be a text string got {}'.format(type(bldg_age))
        assert bldg_age.upper() in self.ageDict.keys(), "bldg_age {} is not recognized as a valid building age.".format('"' + bldg_age + '"')
        return self.ageDict[str(bldg_age).upper()]

    def check_cimate_zone(self, climate_zone):
        assert isinstance(climate_zone, str), 'climate_zone must be a text string got {}'.format(type(climate_zone))
        assert climate_zone.upper() in self.zoneconverter.keys(), 'climate_zone {} is not recognized as a valid climate zone'.format(climate_zone)
        return self.zoneconverter[climate_zone.upper()]

class DFObject(object):
    """Base class for Dragonfly typology, city, terrain, and vegetation."""

    @property
    def isDFObject(self):
        """Return True."""
        return True

class DFParameter(object):
    """Base class for Dragonfly trafficPar, vegetationPar, pavementPar, etc."""

    @property
    def isDFParameter(self):
        """Return True."""
        return True

class Typology(DFObject):
    """Represents a group of buildings of the same typology in an urban area.

    Properties:
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
        floor_to_floor: A number that represents the average distance between floors for the building
            typology.  The default is set to 3.05 meters.
        fract_heat_to_canyon: A number from 0 to 1 that represents the fraction the building's waste
            heat from air conditioning that gets rejected into the urban canyon. The default is set to 0.5.
        glz_ratio: An optional number from 0 to 1 that represents the fraction of the walls of the building typology
            that are glazed. If no value is input here, a default will be used that comes from the DoE building
            template from the bldg_program and bldg_age.
        floor_area: A number that represents the floor area of the buiding in square meteres. The default is auto-calculated
            using the footprint_area, average_height, and floor_to_floor.
        number_of_stories: An integer that represents the average number of stories for the building typology.
    """

    def __init__(self, average_height, footprint_area, facade_area, bldg_program,
                bldg_age, floor_to_floor=None, fract_heat_to_canyon=None,
                glz_ratio=None, floor_area=None):
        """Initialize a dragonfly building typology"""
        # get dependencies
        self.bldgTypes = sc.sticky["dragonfly_UWGBldgTypes"]
        self.genChecks = Utilities()

        # attribute to tract whether we need to update the geometry of the parent city.
        self._has_parent_city = False
        self._parent_city = None

        # critical geometry parameters that all typologies must have.
        self.average_height = average_height
        self.footprint_area = footprint_area
        self.facade_area = facade_area
        self.floor_to_floor = floor_to_floor
        self.floor_area = floor_area

        # critical program parameters that all typologies must have.
        self.bldg_program = bldg_program
        self.bldg_age = bldg_age

        # optional parameters with default values set by program.
        self.fract_heat_to_canyon = fract_heat_to_canyon
        self.glz_ratio = glz_ratio
        self.shgc = None
        self.wall_albedo = None
        self.roof_albedo = None
        self.roof_veg_fraction = None

    @classmethod
    def from_geometry(cls, bldg_breps, bldg_program, bldg_age, floor_to_floor=None,
        fract_heat_to_canyon=None, glz_ratio=None):
        """Initialize a building typology from closed building brep geometry

        Args:
            bldg_breps: A list of closed rhino breps representing buildings of the typology.
            bldg_program: A text string representing one of the 16 DOE building program types to be
                used as a template for this typology.
            bldg_age: A text string that sets the age of the buildings represented by this typology.
            floor_to_floor: A number that represents the average distance between floors. Default is set to 3.05 meters.
            glz_ratio: An optional number from 0 to 1 that represents the fraction of the walls of the building typology
                that are glazed. Default will come from the DoE building template from the bldg_program and bldg_age.
            fract_heat_to_canyon: An optional number from 0 to 1 that represents the fraction the building's waste
                heat from air conditioning that gets rejected into the urban canyon. The default is set to 0.5.

        Returns:
            typology: The dragonfly typology object
            footprint_breps: A list of breps representing the footprints of the buildings.
            floor_breps: A list of breps representing the floors of the buildings in the typology.
            facade_breps: A list of breps representing the exposed facade surfaces of the typology.
        """
        geometryLib = Geometry()
        avgBldgHeight, footprintArea, floorArea, facadeArea, footprint_breps, floor_breps, facade_breps = geometryLib.calculateTypologyGeoParams(bldg_breps, floor_to_floor)

        typology = cls(avgBldgHeight, footprintArea, facadeArea, bldg_program, bldg_age, floor_to_floor, fract_heat_to_canyon, glz_ratio, floorArea)

        return typology, footprint_breps, floor_breps, facade_breps

    @classmethod
    def from_footprints(cls, bldg_footprint_breps, num_stories, bldg_program, bldg_age, floor_to_floor=None,
        fract_heat_to_canyon=None, glz_ratio=None):
        """Initialize a building typology from surfaces representing building footprints and an average number of stories.

        Args:
            bldg_footprint_breps: A list of surface rhino breps representing the building footprints of the typology.
            num_stories: A float value (greater than or equal to 1) that represents the average number of stories of the
                buildings in the typology.
            bldg_program: A text string representing one of the 16 DOE building program types to be
                used as a template for this typology.
            bldg_age: A text string that sets the age of the buildings represented by this typology.
            floor_to_floor: A number that represents the average distance between floors. Default is set to 3.05 meters.
            glz_ratio: An optional number from 0 to 1 that represents the fraction of the walls of the building typology
                that are glazed. Default will come from the DoE building template from the bldg_program and bldg_age.
            fract_heat_to_canyon: An optional number from 0 to 1 that represents the fraction the building's waste
                heat from air conditioning that gets rejected into the urban canyon. The default is set to 0.5.

        Returns:
            typology: The dragonfly typology object
            perimeter_curves: The exterior-exposed curves of the footprints.
        """
        assert num_stories >= 1, 'num_stories must be greater than or equal to 1. Got {}'.format(str(num_stories))

        geometryLib = Geometry()
        footprint_area, perimeter_length, perimeter_curves = geometryLib.calculateFootprintGeoParams(bldg_footprint_breps)

        if floor_to_floor is not None:
            avg_bldg_height = floor_to_floor * num_stories
        else:
            avg_bldg_height = 3.05  * num_stories
        facade_area = perimeter_length * avg_bldg_height
        floor_area = footprint_area * num_stories

        typology = cls(avg_bldg_height, footprint_area, facade_area, bldg_program, bldg_age, floor_to_floor, fract_heat_to_canyon, glz_ratio, floor_area)

        return typology, perimeter_curves

    @classmethod
    def from_footprints_and_stories(cls, bldg_footprint_breps, num_stories, bldg_program, bldg_age, floor_to_floor=None,
        fract_heat_to_canyon=None, glz_ratio=None):
        """Initialize a building typology from surfaces representing building footprints and corresponding list of building stories.

        Args:
            bldg_footprint_breps: A list of surface rhino breps representing the building footprints of the typology.
            num_stories: A list of integer values (all greater than or equal to 1) that represent the
                number of stories for each of the surfaces in the bldg_footprint_breps.
            bldg_program: A text string representing one of the 16 DOE building program types to be
                used as a template for this typology.
            bldg_age: A text string that sets the age of the buildings represented by this typology.
            floor_to_floor: A number that represents the average distance between floors. Default is set to 3.05 meters.
            glz_ratio: An optional number from 0 to 1 that represents the fraction of the walls of the building typology
                that are glazed. Default will come from the DoE building template from the bldg_program and bldg_age.
            fract_heat_to_canyon: An optional number from 0 to 1 that represents the fraction the building's waste
                heat from air conditioning that gets rejected into the urban canyon. The default is set to 0.5.

        Returns:
            typology: The dragonfly typology object
            perimeter_curves: The exterior-exposed curves of the footprints.
        """
        geometry_lib = Geometry()
        weighted_num_stories = 0
        total_ftp_area = 0
        for i, floor_srf in enumerate(bldg_footprint_breps):
            f_area = geometry_lib.calculate_area(floor_srf)
            weighted_num_stories += f_area * num_stories[i]
            total_ftp_area += f_area
        avg_num_stories = weighted_num_stories / total_ftp_area

        return cls.from_footprints(bldg_footprint_breps, avg_num_stories, bldg_program,
            bldg_age, floor_to_floor, fract_heat_to_canyon, glz_ratio)

    @property
    def average_height(self):
        """Get or set the average height of the buildings in meters."""
        return self._average_height

    @average_height.setter
    def average_height(self, h):
        assert isinstance(h, (float, int)), 'average_height must be a number got {}'.format(type(h))
        assert (h >= 0),"average_height must be greater than 0"
        self._average_height = h
        if self.has_parent_city == True:
            self.parent_city.update_geo_from_typologies()

    @property
    def footprint_area(self):
        """Get or set the footprint of the buildings in square meters."""
        return self._footprint_area

    @footprint_area.setter
    def footprint_area(self, a):
        assert isinstance(a, (float, int)), 'footprint_area must be a number got {}'.format(type(a))
        assert (a >= 0),"footprint_area must be greater than 0"
        self._footprint_area = a
        if self.has_parent_city == True:
            self.parent_city.update_geo_from_typologies()

    @property
    def facade_area(self):
        """Get or set the facade area of the buildings in square meters."""
        return self._facade_area

    @facade_area.setter
    def facade_area(self, a):
        assert isinstance(a, (float, int)), 'facade_area must be a number got {}'.format(type(a))
        assert (a >= 0),"facade_area must be greater than 0"
        self._facade_area = a
        if self.has_parent_city == True:
            self.parent_city.update_geo_from_typologies()

    @property
    def floor_to_floor(self):
        """Get or set the facade area of the buildings in square meters."""
        return self._floor_to_floor

    @floor_to_floor.setter
    def floor_to_floor(self, x):
        if x is not None:
            assert isinstance(x, (float, int)), 'floor_to_floor must be a number got {}'.format(type(x))
            assert (x >= 0),"floor_to_floor must be greater than 0"
            self._floor_to_floor = x
        else:
            self._floor_to_floor = 3.05

    @property
    def number_of_stories(self):
        """Return the average number of stories in the buildings."""
        return int(round(self.average_height / self.floor_to_floor))

    @property
    def floor_area(self):
        """Get or set the interior floor area of the buildings in square meters."""
        return self._floor_area

    @floor_area.setter
    def floor_area(self, a):
        if a is not None:
            assert isinstance(a, (float, int)), 'floor_area must be a number got {}'.format(type(a))
            assert (a >= self._footprint_area),"floor_area cannot be smaller than the footprint_area"
            self._floor_area = a
        else:
            self._floor_area = self._footprint_area * self.number_of_stories
        if self.has_parent_city == True:
            self.parent_city.update_geo_from_typologies()

    @property
    def bldg_program(self):
        """Get or set the program of the buildings in the typology."""
        return self._bldg_program

    @bldg_program.setter
    def bldg_program(self, prog):
        self._bldg_program = self.bldgTypes.check_program(prog)

    @property
    def bldg_age(self):
        """Get or set the construction time of buildings in the typology."""
        return self._bldg_age

    @bldg_age.setter
    def bldg_age(self, age):
        self._bldg_age = self.bldgTypes.check_age(age)

    @property
    def fract_heat_to_canyon(self):
        """Get or set the fraction of the building's heat that is rejected to the urban canyon."""
        return self._fract_heat_to_canyon

    @fract_heat_to_canyon.setter
    def fract_heat_to_canyon(self, x):
        if x is not None:
            assert isinstance(x, (float, int)), 'fract_heat_to_canyon must be a number got {}'.format(type(x))
            self._fract_heat_to_canyon = self.genChecks.in_range(x, 0, 1, 'fract_heat_to_canyon')
        else:
            self._fract_heat_to_canyon = 0.5

    @property
    def glz_ratio(self):
        """Get or set the glazing ratio of the buildings in the typology."""
        return self._glz_ratio

    @glz_ratio.setter
    def glz_ratio(self, x):
        if x is not None:
            assert isinstance(x, (float, int)), 'glz_ratio must be a number got {}'.format(type(x))
            self._glz_ratio = self.genChecks.in_range(x, 0, 1, 'glz_ratio')
        else:
            self._glz_ratio = float(self.bldgTypes.refBEM[self.bldgTypes.bldgtype[self.bldg_program]][self.bldgTypes.builtera[self.bldg_age]][0].building.glazingRatio)

    @property
    def shgc(self):
        """Get or set the SHGC of the buildings in the typology."""
        return self._shgc

    @shgc.setter
    def shgc(self, x):
        self._shgc = None
        if x is not None:
            assert isinstance(x, (float, int)), 'shgc must be a number got {}'.format(type(x))
            self._shgc = self.genChecks.in_range(x, 0, 1, 'shgc')

    def get_default_shgc(self, climate_zone):
        """Get the solar heat gain coefficient of the buildings in the typology given the climate climate_zone."""
        zoneIndex = self.bldgTypes.check_cimate_zone(climate_zone)
        return float(self.bldgTypes.refBEM[self.bldgTypes.bldgtype[self.bldg_program]][self.bldgTypes.builtera[self.bldg_age]][zoneIndex].building.shgc)

    @property
    def wall_albedo(self):
        """Get or set the exterior wall albedo of the buildings in the typology."""
        return self._wall_albedo

    @wall_albedo.setter
    def wall_albedo(self, x):
        if x is not None:
            assert isinstance(x, (float, int)), 'wall_albedo must be a number got {}'.format(type(x))
            self._wall_albedo = self.genChecks.in_range(x, 0, 1, 'wall_albedo')
        else:
            self._wall_albedo = float(self.bldgTypes.refBEM[self.bldgTypes.bldgtype[self.bldg_program]][self.bldgTypes.builtera[self.bldg_age]][0].wall.albedo)

    @property
    def roof_albedo(self):
        """Get or set the exterior roof albedo of the buildings in the typology."""
        return self._roof_albedo

    @roof_albedo.setter
    def roof_albedo(self, x):
        if x is not None:
            assert isinstance(x, (float, int)), 'roof_albedo must be a number got {}'.format(type(x))
            self._roof_albedo = self.genChecks.in_range(x, 0, 1, 'roof_albedo')
        else:
            self._roof_albedo = float(self.bldgTypes.refBEM[self.bldgTypes.bldgtype[self.bldg_program]][self.bldgTypes.builtera[self.bldg_age]][0].roof.albedo)

    @property
    def roof_veg_fraction(self):
        """Get or set the roof vegetation fraction of the buildings in the typology."""
        return self._roof_veg_fraction

    @roof_veg_fraction.setter
    def roof_veg_fraction(self, x):
        if x is not None:
            assert isinstance(x, (float, int)), 'roof_veg_fraction must be a number got {}'.format(type(x))
            self._roof_veg_fraction = self.genChecks.in_range(x, 0, 1, 'roof_veg_fraction')
        else:
            self._roof_veg_fraction = 0.

    @property
    def has_parent_city(self):
        return self._has_parent_city

    @property
    def parent_city(self):
        return self._parent_city

    @property
    def isTypology(self):
        """Return True for Typology."""
        return True

    @classmethod
    def create_merged_typology(cls, typology_one, typology_two):
        """Creates a merged Dragonfly typology between two typologies of the same DoE building type and contruction period.

        Args:
            typology_one: The first Dragonfly building typology.
            typology_two: The second Dragonfly building typology.

        Returs:
            merged_typology: A Dragonfly typology representing the merged previous typologies.
        """
        # checks
        assert (hasattr(typology_one, 'isTypology')), 'typology_one must be a Dragonfly typology. got {}'.format(type(typology_one))
        assert (hasattr(typology_two, 'isTypology')), 'typology_two must be a Dragonfly typology. got {}'.format(type(typology_two))
        assert (typology_one.bldg_program == typology_two.bldg_program),"bldg_program of typology_one: {} does not match that of typology_two: {}".format(typology_one.bldg_program, typology_two.bldg_program)
        assert (typology_one.bldg_age == typology_two.bldg_age),"bldg_age of this typology_one: {} does not match that of typology_two: {}".format(typology_one.bldg_age, typology_two.bldg_age)

        # attributes that get totalled
        new_footprint_area = typology_one.footprint_area + typology_two.footprint_area
        new_facade_area = typology_one.facade_area + typology_two.facade_area
        new_floor_area = typology_one.floor_area + typology_two.floor_area
        _typology_one_glz_area = typology_one.facade_area * typology_one.glz_ratio # for window properties
        _typology_two_glz_area = typology_two.facade_area * typology_two.glz_ratio

        # atributes that get weighted averaged.
        new_average_height = (typology_one.average_height*typology_one.footprint_area + typology_two.average_height*typology_two.footprint_area)/new_footprint_area
        new_floor_to_floor = (typology_one.floor_to_floor*typology_one.floor_area + typology_two.floor_to_floor*typology_two.floor_area)/new_floor_area
        new_fract_heat_to_canyon = (typology_one.fract_heat_to_canyon*typology_one.floor_area + typology_two.fract_heat_to_canyon*typology_two.floor_area)/new_floor_area
        new_glz_ratio = (typology_one.glz_ratio*typology_one.facade_area + typology_two.glz_ratio*typology_two.facade_area)/new_facade_area
        new_wall_albedo = (typology_one.wall_albedo*typology_one.facade_area + typology_two.wall_albedo*typology_two.facade_area)/new_facade_area
        new_roof_albedo = (typology_one.roof_albedo*typology_one.footprint_area + typology_two.roof_albedo*typology_two.footprint_area)/new_footprint_area
        new_roof_veg_fraction = (typology_one.roof_veg_fraction*typology_one.footprint_area + typology_two.roof_veg_fraction*typology_two.footprint_area)/new_footprint_area
        new_shgc = (typology_one.shgc*_typology_one_glz_area + typology_two.shgc*_typology_two_glz_area)/(_typology_one_glz_area + _typology_two_glz_area)

        newtypology = cls(new_average_height, new_footprint_area, new_facade_area, typology_one.bldg_program, typology_one.bldg_age, new_floor_to_floor, new_fract_heat_to_canyon, new_glz_ratio, new_floor_area)
        newtypology.roof_albedo = new_roof_albedo
        newtypology.roof_veg_fraction = new_roof_veg_fraction
        newtypology.wall_albedo = new_wall_albedo
        newtypology.shgc = new_shgc

        return newtypology

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Represnt Dragonfly typology."""
        return 'Building Typology: ' + \
               '\n  ' + self._bldg_program + ", " + self._bldg_age + \
               '\n  Average Height: ' + str(int(self._average_height)) + " m" + \
               '\n  Number of Stories: ' + str(self.number_of_stories) + \
               '\n  Floor Area: {:,.0f}'.format(self.floor_area) + " m2" + \
               '\n  Footprint Area: {:,.0f}'.format(self.footprint_area) + " m2" + \
               '\n  Facade Area: {:,.0f}'.format(self.facade_area) + " m2" + \
               '\n  Glazing Ratio: ' + str(int(self.glz_ratio*100)) + "%"

class City(DFObject):
    """Represents a an entire uban area inclluding buildings, pavement, vegetation, and traffic.

    Properties:
        average_bldg_height: The average height of the buildings of the city in meters.
        site_coverage_ratio: A number between 0 and 1 that represents the fraction of the city terrain
            the building footprints occupy.  It describes how close the buildings are to one another in the city.
        facade_to_site_ratio: A number that represents the ratio of vertical urban surface area [walls] to
            the total terrain area of the city.  This value can be greater than 1.
        bldg_type_ratios: A dictoinary with keys that represent the DoE template building programs and building ages
            separated by a comma (eg. MidRiseApartment,1980sPresent).  Under each key of the dictionary, there should
            be a single decimal number indicative of the fraction of the urban area's floor area taken by the typology.
            The sum of all fractions in the dictionary should equal 1. Here is an example dictionary:
                { MidRiseApartment,Pre1980s : 0.7, LargeOffice,1980sPresent: 0.3 }
        climate_zone: A text string representing the ASHRAE climate zone. (eg. 5A). This is used to set
            default constructions for the buildings in the city.
        traffic_parameters: A dragonfly TrafficPar object that defines the traffic within an urban area.
        tree_coverage_ratio: An number from 0 to 1 that defines the fraction of the entire urban area
            (including both pavement and roofs) that is covered by trees.  The default is set to 0.
        grass_coverage_ratio: An number from 0 to 1 that defines the fraction of the entire urban area
            (including both pavement and roofs) that is covered by grass/vegetation.  The default is set to 0.
        vegetation_parameters: A dragonfly VegetationPar object that defines the behaviour of vegetation within an urban area.
        pavement_parameters: A dragonfly PavementPar object that defines the makeup of pavement within the urban area.
        characteristic_length: A number representing the linear dimension of the side of a square that encompasses the neighborhood in meters.
            The default is set to 500 m, which was found to be the recomendation for a typical mid-density urban area.
            Street, Michael A. (2013). Comparison of simplified models of urban climate for improved prediction of building
            energy use in cities. Thesis (S.M. in Building Technology)--Massachusetts Institute of Technology, Dept. of Architecture,
            http://hdl.handle.net/1721.1/82284
    """

    def __init__(self, average_bldg_height, site_coverage_ratio, facade_to_site_ratio,
                bldg_type_ratios, climate_zone, traffic_parameters, tree_coverage_ratio=None,
                grass_coverage_ratio=None, vegetation_parameters=None,
                pavement_parameters=None, characteristic_length=500):
        """Initialize a dragonfly city"""
        # get dependencies
        self.bldgTypes = sc.sticky["dragonfly_UWGBldgTypes"]
        self.genChecks = Utilities()

        # critical geometry parameters that all cities must have and are not set-able.
        assert isinstance(average_bldg_height, (float, int)), 'average_bldg_height must be a number got {}'.format(type(average_bldg_height))
        assert (average_bldg_height >= 0),"average_bldg_height must be greater than 0"
        self._average_bldg_height = average_bldg_height
        assert isinstance(site_coverage_ratio, (float, int)), 'site_coverage_ratio must be a number got {}'.format(type(site_coverage_ratio))
        self._site_coverage_ratio = self.genChecks.in_range(site_coverage_ratio, 0, 1, 'site_coverage_ratio')
        assert isinstance(facade_to_site_ratio, (float, int)), 'facade_to_site_ratio must be a number got {}'.format(type(facade_to_site_ratio))
        assert (facade_to_site_ratio >= 0),"facade_to_site_ratio must be greater than 0"
        self._facade_to_site_ratio = facade_to_site_ratio
        assert isinstance(characteristic_length, (float, int)), 'characteristic_length must be a number got {}'.format(type(characteristic_length))
        assert (characteristic_length >= 0),"characteristic_length must be greater than 0"
        self._characteristic_length = characteristic_length

        # critical program parameters that all typologies must have and are set-able.
        self._bldg_type_ratios = bldg_type_ratios
        self._building_typologies = None
        self._are_typologies_loaded = False

        # dragonfly parameter objects that define conditions within the city and are set-able.
        self.climate_zone = climate_zone
        self.traffic_parameters = traffic_parameters
        self.vegetation_parameters = vegetation_parameters
        self.pavement_parameters = pavement_parameters

        # vegetation coverage
        self.tree_coverage_ratio = tree_coverage_ratio
        self.grass_coverage_ratio = grass_coverage_ratio

    @classmethod
    def from_typologies(cls, typologies, terrian, climate_zone, traffic_parameters, tree_coverage_ratio=None,
        grass_coverage_ratio=None, vegetation_parameters=None, pavement_parameters=None):
        """Initialize a city from a list of building typologies
        Args:
            typologies: A list of dragonfly Typology objects.
            terrian: A dragonfly Terrain object.
            climate_zone: A text string representing the ASHRAE climate zone. (eg. 5A). This is used to set
                default constructions for the buildings in the city.
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
        # merge any typologies that are of the same DoE template.
        bldgTypes = {}
        mergedTypes = []
        uniqueCount = 0
        for bType in typologies:
            assert hasattr(bType, 'isTypology'), 'typology is not a dragonfly typolgy object. Got {}'.format(type(bType))
            bTypeName = bType.bldg_program + ',' + bType.bldg_age
            if bTypeName not in bldgTypes.keys():
                mergedTypes.append(bType)
                bldgTypes[bTypeName] = uniqueCount
                uniqueCount += 1
            else:
                typeToMerge = mergedTypes[bldgTypes[bTypeName]]
                mergedType = Typology.create_merged_typology(bType, typeToMerge)
                mergedTypes[bldgTypes[bTypeName]] = mergedType

        # process the terrain surface.
        assert hasattr(terrian, 'isTerrain'), 'terrian is not a dragonfly terrian object. Got {}'.format(type(terrian))
        terrainArea = terrian.area

        # compute the critical geometry variables for the city
        totalFootprintArea = 0
        weightedHeightSum = 0
        totalFacadeArea = 0
        floorAreas = []
        fullTypeNames = []
        for bType in mergedTypes:
            totalFootprintArea += bType.footprint_area
            weightedHeightSum += bType.average_height*bType.footprint_area
            totalFacadeArea += bType.facade_area
            floorAreas.append(bType.floor_area)
            fullTypeNames.append(bType.bldg_program + ',' + bType.bldg_age)
        avgBldgHeight = weightedHeightSum/totalFootprintArea
        bldgCoverage = totalFootprintArea/terrainArea
        facadeToSite = totalFacadeArea/terrainArea

        # build the dictionary of typology ratios
        totalWeight = sum(floorAreas)
        typologyRatios = [x/totalWeight for x in floorAreas]
        bldgTypeDict = {}
        for i, key in enumerate(fullTypeNames):
            bldgTypeDict[key] = typologyRatios[i]

        # create the city object.
        dfCity = cls(avgBldgHeight, bldgCoverage, facadeToSite, bldgTypeDict, climate_zone,
            traffic_parameters, tree_coverage_ratio, grass_coverage_ratio, vegetation_parameters,
            pavement_parameters, terrian.characteristic_length)

        # link the typologies to the city object
        for bTyp in mergedTypes:
            bTyp._has_parent_city = True
            bTyp._parent_city = dfCity
            if bTyp.shgc == None:
                bTyp.shgc = bTyp.get_default_shgc(dfCity.climate_zone)
        dfCity._building_typologies = mergedTypes
        dfCity._are_typologies_loaded = True

        return dfCity

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
    def characteristic_length(self):
        """Return the caracteristic length of the city."""
        return self._characteristic_length

    @property
    def bldg_types(self):
        """Return a list of the building types in the city."""
        return self._bldg_type_ratios.keys()

    @property
    def bldg_type_ratios(self):
        """Get or set the building types and corresponding ratios as a dictionary.

        Note that setting the typology ratios here completely overwrites the
        building_typologies currently associated with this city object.
        """
        return self._bldg_type_ratios

    @bldg_type_ratios.setter
    def bldg_type_ratios(self, bldg_type_dict):
        totalRatios = 0
        for type in bldg_type_dict.keys():
            assert isinstance(type, str), 'building_type must be a string got {}'.format(type(type))
            assert isinstance(bldg_type_dict[type], (float, int)), 'building_type ratio must be a number got {}'.format(type(bldg_type_dict[type]))
            totalRatios += bldg_type_dict[type]
            try:
                bldg_program, bldg_age = type.split(',')
                _bldg_program = self.bldgTypes.check_program(bldg_program)
                _bldg_age = self.bldgTypes.check_age(bldg_age)
            except:
                raise Exception (
                    "Building Type {} is not in the correct format of BuildingProgram,BuildingAge.".format('"' + str(type) + '"')
                )
        assert (totalRatios == 1),"Total building ratios do not sum to 1. Got {}".format(str(totalRatios))
        self._bldg_type_ratios = bldg_type_dict
        self._are_typologies_loaded = False

    @property
    def building_typologies(self):
        """Return a list of dragonfly building typology objects for the urban area."""
        if self.are_typologies_loaded == True:
            return self._building_typologies
        else:
            # build dragonfly typology objects from the dictionary of building type ratios.
            self._building_typologies = []
            for bType in self.bldg_type_ratios.keys():
                bldg_program, bldg_age = bType.split(',')
                cityFract = self.bldg_type_ratios[bType]
                site_area = math.pow(self.characteristic_length,2) * math.pi
                footprint_area = site_area * self.site_coverage_ratio * cityFract
                facade_area = site_area * self.facade_to_site_ratio * cityFract
                newType = Typology(self.average_bldg_height, footprint_area, facade_area, bldg_program, bldg_age)
                newType._parent_city = self
                newType._has_parent_city = True
                newType.shgc = newType.get_default_shgc(self.climate_zone)
                self._building_typologies.append(newType)
            self._are_typologies_loaded = True
            return self._building_typologies

    @property
    def climate_zone(self):
        """Get or set the ASHRAE climate zone that dictates the nature of the constructions of the buildings."""
        return self.bldgTypes.zonetype[self._climate_zone]

    @climate_zone.setter
    def climate_zone(self, z):
        assert isinstance(z, str), 'climate_zone must be a text string got {}'.format(type(z))
        assert z.upper() in self.bldgTypes.zoneconverter.keys(), 'climate_zone {} is not recognized as a valid climate zone'.format(z)
        self._climate_zone = self.bldgTypes.zoneconverter[z.upper()]

    @property
    def traffic_parameters(self):
        """Get or set the traffic parameter object that describes the city's traffic."""
        return self._traffic_parameters

    @traffic_parameters.setter
    def traffic_parameters(self, p):
        assert hasattr(p, 'isTrafficPar'), 'traffic_parameters is not a dragonfly traffic_parameters object. Got {}'.format(type(p))
        self._traffic_parameters = p

    @property
    def vegetation_parameters(self):
        """Get or set the vegetation parameter object that describes the city's vegetation."""
        return self._vegetation_parameters

    @vegetation_parameters.setter
    def vegetation_parameters(self, p):
        if p is not None:
            assert hasattr(p, 'isVegetationPar'), 'vegetation_parameters is not a dragonfly vegetation_parameters object. Got {}'.format(type(p))
            self._vegetation_parameters = p
        else:
            self._vegetation_parameters = VegetationPar()

    @property
    def pavement_parameters(self):
        """Get or set the pavement parameter object that describes the city's pavement."""
        return self._pavement_parameters

    @pavement_parameters.setter
    def pavement_parameters(self, p):
        if p is not None:
            assert hasattr(p, 'isPavementPar'), 'pavement_parameters is not a dragonfly pavement_parameters object. Got {}'.format(type(p))
            self._pavement_parameters = p
        else:
            self._pavement_parameters = PavementPar()

    @property
    def tree_coverage_ratio(self):
        """Get or set the ratio of the entire site area of the city covered in trees."""
        return self._tree_coverage_ratio

    @tree_coverage_ratio.setter
    def tree_coverage_ratio(self, x):
        if x is not None:
            assert isinstance(x, (float, int)), 'tree_coverage_ratio must be a number got {}'.format(type(x))
            self._tree_coverage_ratio = self.genChecks.in_range(x, 0, 1, 'tree_coverage_ratio')
        else:
            self._tree_coverage_ratio = 0

    @property
    def grass_coverage_ratio(self):
        """Get or set the ratio of the entire site area of the city covered in grass."""
        return self._grass_coverage_ratio

    @grass_coverage_ratio.setter
    def grass_coverage_ratio(self, x):
        if x is not None:
            assert isinstance(x, (float, int)), 'grass_coverage_ratio must be a number got {}'.format(type(x))
            self._grass_coverage_ratio = self.genChecks.in_range(x, 0, 1, 'grass_coverage_ratio')
        else:
            self._grass_coverage_ratio = 0

    @property
    def floor_height(self):
        """Get the average floor height of the buildings in the typology."""
        weighted_sum = 0
        totalFloorArea = 0
        for bldgType in self.building_typologies:
            weighted_sum += bldgType.floor_to_floor * bldgType.floor_area
            totalFloorArea += bldgType.floor_area
        return weighted_sum / totalFloorArea

    @property
    def fract_heat_to_canyon(self):
        """Return the fraction of the building's heat that is rejected to the urban canyon."""
        weighted_sum = 0
        totalFlrArea = 0
        for bldgType in self.building_typologies:
            weighted_sum += bldgType.fract_heat_to_canyon * bldgType.floor_area
            totalFlrArea += bldgType.floor_area
        return weighted_sum / totalFlrArea

    @property
    def glz_ratio(self):
        """Return the average glazing ratio of the buildings in the city."""
        weighted_sum = 0
        totalFacadeArea = 0
        for bldgType in self.building_typologies:
            weighted_sum += bldgType.glz_ratio*bldgType.facade_area
            totalFacadeArea += bldgType.facade_area
        return weighted_sum / totalFacadeArea

    @property
    def shgc(self):
        """Get the solar heat gain coefficient of the buildings in the typology."""
        weighted_sum = 0
        totalFacadeArea = 0
        for bldgType in self.building_typologies:
            if bldgType.shgc is None:
                bldgType.shgc = bldgType.get_default_shgc(self.climate_zone)
            weighted_sum += bldgType.shgc * bldgType.facade_area
            totalFacadeArea += bldgType.facade_area
        return weighted_sum / totalFacadeArea

    @property
    def wall_albedo(self):
        """Return the average wall albedo of the buildings in the city."""
        weighted_sum = 0
        totalFacadeArea = 0
        for bldgType in self.building_typologies:
            weighted_sum += bldgType.wall_albedo * bldgType.facade_area
            totalFacadeArea += bldgType.facade_area
        return weighted_sum / totalFacadeArea

    @property
    def roof_albedo(self):
        """Return the average roof albedo of the buildings in the city."""
        weighted_sum = 0
        total_roof_area = 0
        for bldg_type in self.building_typologies:
            weighted_sum += bldg_type.roof_albedo * bldg_type.footprint_area
            total_roof_area += bldg_type.footprint_area
        return weighted_sum / total_roof_area

    @property
    def roof_veg_fraction(self):
        """Return the average roof vegetated fraction of the buildings in the city."""
        weighted_sum = 0
        total_roof_area = 0
        for bldg_type in self.building_typologies:
            weighted_sum += bldg_type.roof_veg_fraction * bldg_type.footprint_area
            total_roof_area += bldg_type.footprint_area
        return weighted_sum / total_roof_area

    @property
    def are_typologies_loaded(self):
        """Return True when typologies need to be created or re-generated."""
        return self._are_typologies_loaded

    @property
    def isCity(self):
        """Return True for City."""
        return True

    def get_uwg_matrix(self):
        """Return a matrix of bldg typologies and construction eras that be assigned to the uwg."""
        bTypeMtx = [[0 for x in range(3)] for y in range(16)]
        for type in self.bldg_type_ratios.keys():
            fraction = round(self.bldg_type_ratios[type], 3)
            bldg_program, bldg_age = type.split(',')
            program_i = self.bldgTypes.bldgtype[bldg_program]
            age_i = self.bldgTypes.builtera[bldg_age]
            bTypeMtx[program_i][age_i] = fraction
        return bTypeMtx

    def update_geo_from_typologies(self):
        """Updates the city-wide geometry parameters whenever an individual building typology's have changed."""
        site_area = math.pow(self.characteristic_length,2) * math.pi
        totalFootprintArea = 0
        weightedHeightSum = 0
        totalFacadeArea = 0
        floorAreas = []
        fullTypeNames = []
        for bType in self.building_typologies:
            totalFootprintArea += bType.footprint_area
            weightedHeightSum += bType.average_height * bType.footprint_area
            totalFacadeArea += bType.facade_area
            floorAreas.append(bType.floor_area)
            fullTypeNames.append(bType.bldg_program + ',' + bType.bldg_age)
        self._average_bldg_height = weightedHeightSum/totalFootprintArea
        self._site_coverage_ratio = totalFootprintArea/site_area
        self._facade_to_site_ratio = totalFacadeArea/site_area

        totalWeight = sum(floorAreas)
        typologyRatios = [x/totalWeight for x in floorAreas]
        self._building_typologies = {}
        for i, key in enumerate(fullTypeNames):
            self._building_typologies[key] = typologyRatios[i]

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Represnt Dragonfly city."""
        typologyList = ''
        for x in self.bldg_types:
            typologyList = typologyList + '\n     ' + str(round(self.bldg_type_ratios[x], 2)) + ' - ' + x
        return 'City: ' + \
               '\n  Average Bldg Height: ' + str(int(self._average_bldg_height)) + " m" + \
               '\n  Site Coverage Ratio: ' + str(round(self._site_coverage_ratio, 2)) + \
               '\n  Facade-to-Site Ratio: ' + str(round(self._facade_to_site_ratio, 2)) + \
               '\n  Tree Coverage Ratio: ' + str(round(self._tree_coverage_ratio, 2)) + \
               '\n  Grass Coverage Ratio: ' + str(round(self._grass_coverage_ratio, 2)) + \
               '\n  ------------------------' + \
               '\n  Building Typologies: ' + typologyList

class Terrain(DFObject):
    """Represents the terrain on which an urban area sits.

    Properties:
        area: The area of the urban terrain surface in square meters (projected into the XY plane).
        characteristic_length:  A number representing the radius of a circle that encompasses the
            whole neighborhood in meters.  If no value is input here, it will be auto-calculated
            assuming that the area above is cicular.
    """

    def __init__(self, area, characteristic_length=None):
        """Initialize a dragonfly terrain surface"""
        self.area = area

    @classmethod
    def from_geometry(cls, terrainSrfs):
        """Initialize a dragonfly terrain surface from a list of terrain breps
        Args:
            terrainSrfs: A list of Rhino surfaces representing the terrian.

        Returns:
            terrain: The dragonfly terrain object.
            surfaceBreps: The srfBreps representing the terrain (projected into the XY plane).
        """
        geometryLib = Geometry()
        surfaceArea, surfaceBreps = geometryLib.calculateFootprints(terrainSrfs)
        terrain = cls(surfaceArea)

        return terrain, surfaceBreps

    @property
    def area(self):
        """Get or set the area of the terrain surface in the XY plane."""
        return self._area

    @area.setter
    def area(self, a):
        assert isinstance(a, (float, int)), 'area must be a number got {}'.format(type(a))
        assert (a >= 0),"area must be greater than 0"
        self._area = a
        self._characteristic_length = math.sqrt(self._area)

    @property
    def characteristic_length(self):
        """Return the characteristic length."""
        return self._characteristic_length

    @property
    def isTerrain(self):
        """Return True for Terrain."""
        return True

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Represnt Dragonfly terrain."""
        return 'Terrain: ' + \
               '\n  Area: ' + str(int(self._area)) + " m2" + \
               '\n  Radius: ' + str(int(self._characteristic_length)) + " m"

class Vegetation(DFObject):
    """Represents vegetation (either grass or trees) within an urban area.

    Properties:
        area: The area of the urban terrain covered by the vegetation in square meters
            (projected into the XY plane).
        is_trees: A boolean value that denotes whether the vegetation object represents
            trees (True) or grass (False).
    """

    def __init__(self, area, is_trees=False):
        """Initialize a dragonfly vegetation object"""
        self.area = area
        self._is_trees = is_trees

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
        geometryLib = Geometry()
        surfaceArea, projected_breps = geometryLib.calculateFootprints(veg_breps)
        vegetation = cls(surfaceArea, is_trees)

        return vegetation, projected_breps

    @property
    def area(self):
        """Get or set the area of the vegetation in the XY plane."""
        return self._area

    @area.setter
    def area(self, a):
        assert isinstance(a, (float, int)), 'area must be a number got {}'.format(type(a))
        assert (a >= 0),"area must be greater than 0"
        self._area = a

    @property
    def is_trees(self):
        """Get or set a boolean showing whether the vegetation represents trees or grass."""
        return self._is_trees

    @is_trees.setter
    def is_trees(self, a):
        assert isinstance(a, (bool)), 'is_trees must be a boolean got {}'.format(type(a))
        self._is_trees = a

    @property
    def isVegetation(self):
        """Return True for Vegetation."""
        return True

    def computeCoverage(self, terrain):
        """Initialize a dragonfly tree object from a list of closed tree breps
        Args:
            terrain: A dragonfly terrin object with which to compute coverage.

        Returns:
            coverage: A number between 0 and 1 representing the fraction of
                the terrain covered by the vegetation.
        """
        assert hasattr(terrain, 'isTerrain'), \
            'terrain must be Df terrain. Got {}'.format(type(terrain))

        genChecks = Utilities()
        coverage = genChecks.in_range((self._area/terrain.area), 0, 1, 'vegetation_coverage')

        return coverage

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Represnt Dragonfly vegetation."""
        vegType = 'Trees' if self._is_trees else 'Grass'
        return 'Vegetation: ' + vegType + \
               '\n  Area: ' + str(int(self._area)) + " m2"

class TrafficPar(DFParameter):
    """Represents the traffic within an urban area.

    Properties:
        sensible_heat: A number representing the maximum sensible anthropogenic heat flux of the urban area
            in watts per square meter. This input is required.
        weekday_schedule: A list of 24 fractional values that will be multiplied by the sensible_heat
            to produce hourly values for heat on the weekday of the simulation.  The default is
            a typical traffic schedule for a commerical area.
        saturday_schedule: A list of 24 fractional values that will be multiplied by the sensible_heat
            to produce hourly values for heat on Saturdays of the simulation.  The default is
            a typical traffic schedule for a commerical area.
        sunday_schedule: A list of 24 fractional values that will be multiplied by the sensible_heat
            to produce hourly values for heat on Sundays of the simulation.  The default is
            a typical traffic schedule for a commerical area.
    """

    def __init__(self, sensible_heat, weekday_schedule=[],
                saturday_schedule=[], sunday_schedule=[]):
        """Initialize dragonfly traffic parameters"""
        # get dependencies
        self.genChecks = Utilities()

        self.sensible_heat = sensible_heat
        self.weekday_schedule = weekday_schedule
        self.saturday_schedule = saturday_schedule
        self.sunday_schedule = sunday_schedule

    @property
    def sensible_heat(self):
        """Get or set the max sensible heat flux of the traffic."""
        return self._sensible_heat

    @sensible_heat.setter
    def sensible_heat(self, heat):
        assert isinstance(heat, (float, int)), 'sensible_heat must be a number got {}'.format(type(heat))
        assert (heat >= 0),"sensible_heat must be greater than 0"
        self._sensible_heat = heat

    @property
    def weekday_schedule(self):
        """Get or set the Weekday traffic schedule."""
        return self._weekday_schedule

    @weekday_schedule.setter
    def weekday_schedule(self, sched):
        if sched != []:
            self._weekday_schedule = self.genChecks.checkSchedule(sched)
        else:
            self._weekday_schedule = [0.2,0.2,0.2,0.2,0.2,0.4,0.7,0.9,0.9,0.6,0.6, \
                0.6,0.6,0.6,0.7,0.8,0.9,0.9,0.8,0.8,0.7,0.3,0.2,0.2]

    @property
    def saturday_schedule(self):
        """Get or set the Saturday traffic schedule."""
        return self._saturday_schedule

    @saturday_schedule.setter
    def saturday_schedule(self, sched):
        if sched != []:
            self._saturday_schedule = self.genChecks.checkSchedule(sched)
        else:
            self._saturday_schedule = [0.2,0.2,0.2,0.2,0.2,0.3,0.5,0.5,0.5,0.5,0.5, \
                0.5,0.5,0.5,0.6,0.7,0.7,0.7,0.7,0.5,0.4,0.3,0.2,0.2]

    @property
    def sunday_schedule(self):
        """Get or set the Sunday traffic schedule as a list."""
        return self._sunday_schedule

    @sunday_schedule.setter
    def sunday_schedule(self, sched):
        if sched != []:
            self._sunday_schedule = self.genChecks.checkSchedule(sched)
        else:
            self._sunday_schedule = [0.2,0.2,0.2,0.2,0.2,0.3,0.4,0.4,0.4,0.4,0.4,0.4, \
                0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.4,0.3,0.3,0.2,0.2]

    @property
    def isTrafficPar(self):
        """Return True for isTrafficPar."""
        return True

    def get_uwg_matrix(self):
        """Return a python matrix of the traffic schedule that can be assigned to the uwg."""
        return [self.weekday_schedule, self.saturday_schedule, self.sunday_schedule]

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Represnt Dragonfly traffic parameters."""
        return 'Traffic Parameters: ' + \
               '\n  Max Heat: ' + str(self._sensible_heat) + ' W/m2' + \
               '\n  Weekday Avg Heat: ' + str(round(self._sensible_heat* (sum(self._weekday_schedule)/24),1)) + ' W/m2' + \
               '\n  Saturday Avg Heat: ' + str(round(self._sensible_heat* (sum(self._saturday_schedule)/24),1)) + ' W/m2' + \
               '\n  Sunday Avg Heat: ' + str(round(self._sensible_heat* (sum(self._sunday_schedule)/24),1)) + ' W/m2'

class VegetationPar(DFParameter):
    """Represents the behaviour of vegetation within an urban area.

    Properties:
        vegetation_albedo: A number between 0 and 1 that represents the ratio of reflected radiation
            from vegetated surfaces to incident radiation upon them.
        vegetation_start_month: An integer from 1 to 12 that represents the month at which
            vegetation begins to affect the urban climate.  The default is set to 0, which will
            automatically determine the vegetation start month by analyzing the epw to see which
            months have an average monthly temperature above 10 C.
        vegetation_end_month: An integer from 1 to 12 that represents the last month at which
            vegetation affect the urban climate.  The default is set to 0, which will
            automatically determine the vegetation end month by analyzing the epw to see which
            months have an average monthly temperature above 10 C.
        tree_latent_fraction: A number between 0 and 1 that represents the the fraction of absorbed
            solar energy by trees that is given off as latent heat (evapotranspiration). Currently,
            this does not affect the moisture balance in the uwg but it will affect the temperature.
            If no value is input here, a typical value of 0.7 will be assumed.
        grass_latent_fraction: A number between 0 and 1 that represents the the fraction of absorbed solar
            energy by grass that is given off as latent heat (evapotranspiration). Currently,
            this does not affect the moisture balance in the uwg but it will affect the temperature.
            If no value is input here, a typical value of 0.5 will be assumed.
    """

    def __init__(self, vegetation_albedo=0.25, vegetation_start_month=0, vegetation_end_month=0,
        tree_latent_fraction=0.7, grass_latent_fraction=0.5):
        """Initialize dragonfly vegetation parameters"""
        # get dependencies
        self.genChecks = Utilities()

        self.vegetation_albedo = vegetation_albedo
        self.vegetation_start_month = vegetation_start_month
        self.vegetation_end_month = vegetation_end_month
        self.tree_latent_fraction = tree_latent_fraction
        self.grass_latent_fraction = grass_latent_fraction

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
        """Get or set the vegetation start month."""
        return self._vegetation_start_month

    @vegetation_start_month.setter
    def vegetation_start_month(self, month):
        if month is not None:
            assert isinstance(month, (float, int)), 'vegetation_start_month must be a number got {}'.format(type(month))
            self._vegetation_start_month = self.genChecks.in_range(int(month), 0, 12, 'vegetation_start_month')
        else:
            self._vegetation_start_month = 0

    @property
    def vegetation_end_month(self):
        """Get or set the vegetation end month."""
        return self._vegetation_end_month

    @vegetation_end_month.setter
    def vegetation_end_month(self, month):
        if month is not None:
            assert isinstance(month, (float, int)), 'vegetation_end_month must be a number got {}'.format(type(month))
            self._vegetation_end_month = self.genChecks.in_range(int(month), 0, 12, 'vegetation_end_month')
        else:
            self._vegetation_end_month = 0

    @property
    def vegetation_albedo(self):
        """Get or set the vegetation albedo."""
        return self._vegetation_albedo

    @vegetation_albedo.setter
    def vegetation_albedo(self, a):
        if a is not None:
            assert isinstance(a, (float, int)), 'vegetation_albedo must be a number got {}'.format(type(a))
            self._vegetation_albedo = self.genChecks.in_range(a, 0, 1, 'vegetation_albedo')
        else:
            self._vegetation_albedo = 0.25

    @property
    def tree_latent_fraction(self):
        """Return the tree latent fraction."""
        return self._tree_latent_fraction

    @tree_latent_fraction.setter
    def tree_latent_fraction(self, a):
        if a is not None:
            assert isinstance(a, (float, int)), 'tree_latent_fraction must be a number got {}'.format(type(a))
            self._tree_latent_fraction = self.genChecks.in_range(a, 0, 1, 'tree_latent_fraction')
        else:
            self._tree_latent_fraction = 0.7

    @property
    def grass_latent_fraction(self):
        """Return the grass latent fraction."""
        return self._grass_latent_fraction

    @grass_latent_fraction.setter
    def grass_latent_fraction(self, a):
        if a is not None:
            assert isinstance(a, (float, int)), 'grass_latent_fraction must be a number got {}'.format(type(a))
            self._grass_latent_fraction = self.genChecks.in_range(a, 0, 1, 'grass_latent_fraction')
        else:
            self._grass_latent_fraction = 0.5

    @property
    def isVegetationPar(self):
        """Return True for isVegetationPar."""
        return True

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Represnt Dragonfly vegetation parameters."""
        return 'Vegetation Parameters: ' + \
               '\n  Albedo: ' + str(self._vegetation_albedo) + \
               '\n  Vegetation Time: ' + self.monthsDict[self._vegetation_start_month] + ' - ' + self.monthsDict[self._vegetation_end_month] + \
               '\n  Tree | Grass Latent: ' + str(self._tree_latent_fraction) + ' | ' + str(self._grass_latent_fraction)


class PavementPar(DFParameter):
    """Represents the makeup of pavement within the urban area.

    Properties:
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
        self.genChecks = Utilities()

        self.albedo = albedo
        self.thickness = thickness
        self.conductivity = conductivity
        self.volumetric_heat_capacity = volumetric_heat_capacity

    @property
    def albedo(self):
        """Get or set the road albedo."""
        return self._albedo

    @albedo.setter
    def albedo(self, a):
        if a is not None:
            assert isinstance(a, (float, int)), 'albedo must be a number got {}'.format(type(a))
            self._albedo = self.genChecks.in_range(a, 0, 1, 'albedo')
        else:
            self._albedo = 0.1

    @property
    def thickness(self):
        """Get or set the road thickness."""
        return self._thickness

    @thickness.setter
    def thickness(self, t):
        if t is not None:
            assert isinstance(t, (float, int)), 'thickness must be a number got {}'.format(type(t))
            assert (t >= 0),"thickness must be greater than 0"
            self._thickness = t
        else:
            self._thickness = 0.5

    @property
    def conductivity(self):
        """Get or set the road conductivity."""
        return self._conductivity

    @conductivity.setter
    def conductivity(self, k):
        if k is not None:
            assert isinstance(k, (float, int)), 'conductivity must be a number got {}'.format(type(k))
            assert (k >= 0),"conductivity must be greater than 0"
            self._conductivity = k
        else:
            self._conductivity = 1

    @property
    def volumetric_heat_capacity(self):
        """Get or set the volumetric heat capacity."""
        return self._volumetric_heat_capacity

    @volumetric_heat_capacity.setter
    def volumetric_heat_capacity(self, x):
        if x is not None:
            assert isinstance(x, (float, int)), 'volumetric_heat_capacity must be a number got {}'.format(type(x))
            assert (x >= 0),"volumetric_heat_capacity must be greater than 0"
            self._volumetric_heat_capacity = x
        else:
            self._volumetric_heat_capacity = 1600000

    @property
    def isPavementPar(self):
        """Return True for isPavementPar."""
        return True

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Represnt Dragonfly pavement parameters."""
        return 'Pavement Parameters: ' + \
               '\n  Albedo: ' + str(self._albedo) + \
               '\n  Thickness: ' + str(self._thickness) + \
               '\n  Conductivity: ' + str(self._conductivity) + \
               '\n  Vol Heat Capacity: ' + str(self._volumetric_heat_capacity)

class RefEPWSitePar(DFParameter):
    """Represents the properties of the reference site where the original EPW was recorded.

    Properties:
        average_obstacle_height: A number that represents the height in meters of objects that
            obstruct the view to the sky at the weather station site.  This includes both trees
            and buildings.  The default is set to 0.1 meters.
        vegetation_coverage: A number between 0 and 1 that represents that fraction of the reference
            EPW site that is covered in grass. If nothing is input here, a defailt of 0.9 will be used.
        temp_measure_height: A number that represents the height in meters at which temperature is
            measured on the weather station.  The default is set to 10 meters as this is the standard
            measurement height for US Department of Energy EPW files.
        wind_measure_height: A number that represents the height in meters at which wind speed is
            measured on the weather station.  The default is set to 10 meters as this is the standard
            measurement height for US Department of Energy EPW files.
    """

    def __init__(self, average_obstacle_height=None, vegetation_coverage=None, temp_measure_height=None, wind_measure_height=None):
        """Initialize RefEPWSitePar parameters"""
        # get dependencies
        self.genChecks = Utilities()

        self.average_obstacle_height = average_obstacle_height
        self.vegetation_coverage = vegetation_coverage
        self.temp_measure_height = temp_measure_height
        self.wind_measure_height = wind_measure_height

    @property
    def average_obstacle_height(self):
        """Get or set the average obstacle height."""
        return self._average_obstacle_height

    @average_obstacle_height.setter
    def average_obstacle_height(self, h):
        if h is not None:
            assert isinstance(h, (float, int)), 'average_obstacle_height must be a number got {}'.format(type(h))
            assert (h >= 0),"average_obstacle_height must be greater than 0"
            self._average_obstacle_height = h
        else:
            self._average_obstacle_height = 0.1

    @property
    def vegetation_coverage(self):
        """Get or set the vegetation coverage."""
        return self._vegetation_coverage

    @vegetation_coverage.setter
    def vegetation_coverage(self, a):
        if a is not None:
            assert isinstance(a, (float, int)), 'vegetation_coverage must be a number got {}'.format(type(a))
            self._vegetation_coverage = self.genChecks.in_range(a, 0, 1, 'vegetation_coverage')
        else:
            self._vegetation_coverage = 0.9

    @property
    def temp_measure_height(self):
        """Get or set the temperature measurement height."""
        return self._temp_measure_height

    @temp_measure_height.setter
    def temp_measure_height(self, h):
        if h is not None:
            assert isinstance(h, (float, int)), 'temp_measure_height must be a number got {}'.format(type(h))
            assert (h >= 0),"temp_measure_height must be greater than 0"
            self._temp_measure_height = h
        else:
            self._temp_measure_height = 10

    @property
    def wind_measure_height(self):
        """Get or set the wind measurement height."""
        return self._wind_measure_height

    @wind_measure_height.setter
    def wind_measure_height(self, h):
        if h is not None:
            assert isinstance(h, (float, int)), 'wind_measure_height must be a number got {}'.format(type(h))
            assert (h >= 0),"wind_measure_height must be greater than 0"
            self._wind_measure_height = h
        else:
            self._wind_measure_height = 10

    @property
    def isRefEPWSitePar(self):
        """Return True for isRefEPWSitePar."""
        return True

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Represnt Dragonfly reference EPW site parameters."""
        return 'Reference EPW Site Parameters: ' + \
               '\n  Obstacle Height: ' + str(self._average_obstacle_height) + ' m' + \
               '\n  Vegetation Coverage: ' + str(self._vegetation_coverage) + \
               '\n  Measurement Height (Temp | Wind): ' + str(self._temp_measure_height) + \
                    ' m | ' + str(self._wind_measure_height) + ' m'

class BoundaryLayerPar(DFParameter):
    """Represents the properties of the urban boundary layer.

    Properties:
        day_boundary_layer_height: A number that represents the height in meters of the urban boundary layer
            during the daytime. This is the height to which the urban meterorological conditions are stable
            and representative of the overall urban area. Typically, this boundary layer height increases with
            the height of the buildings.  The default is set to 1000 meters.
        night_boundary_layer_height: A number that represents the height in meters of the urban boundary layer
            during the nighttime. This is the height to which the urban meterorological conditions are stable
            and representative of the overall urban area. Typically, this boundary layer height increases with
            the height of the buildings.  The default is set to 80 meters.
        inversion_height: A number that represents the height at which the vertical profile of potential
            temperature becomes stable. It is the height at which the profile of air temperature becomes
            stable. Can be determined by flying helium balloons equipped with temperature sensors and
            recording the air temperatures at different heights.  The default is set to 150 meters.
        circulation_coefficient: A number that represents the circulation coefficient.  The default
            is 1.2 per Bueno, Bruno (2012).
        exchange_coefficient: A number that represents the exchange coefficient.  The default is
            1.0 per Bueno, Bruno (2014).
    """

    def __init__(self, day_boundary_layer_height=None, night_boundary_layer_height=None,
        inversion_height=None, circulation_coefficient=None, exchange_coefficient=None):
        """Initialize Boundary Layer parameters"""

        self.day_boundary_layer_height = day_boundary_layer_height
        self.night_boundary_layer_height = night_boundary_layer_height
        self.inversion_height = inversion_height
        self.circulation_coefficient = circulation_coefficient
        self.exchange_coefficient = exchange_coefficient

    @property
    def day_boundary_layer_height(self):
        """Get or set the daytime boundary layer height."""
        return self._day_boundary_layer_height

    @day_boundary_layer_height.setter
    def day_boundary_layer_height(self, h):
        if h is not None:
            assert isinstance(h, (float, int)), 'day_boundary_layer_height must be a number got {}'.format(type(h))
            assert (h >= 0),"day_boundary_layer_height must be greater than 0"
            self._day_boundary_layer_height = h
        else:
            self._day_boundary_layer_height = 1000

    @property
    def night_boundary_layer_height(self):
        """Get or set the nighttime boundary layer height."""
        return self._night_boundary_layer_height

    @night_boundary_layer_height.setter
    def night_boundary_layer_height(self, h):
        if h is not None:
            assert isinstance(h, (float, int)), 'night_boundary_layer_height must be a number got {}'.format(type(h))
            assert (h >= 0),"night_boundary_layer_height must be greater than 0"
            self._night_boundary_layer_height = h
        else:
            self._night_boundary_layer_height = 80

    @property
    def inversion_height(self):
        """Get or set the inversion height."""
        return self._inversion_height

    @inversion_height.setter
    def inversion_height(self, h):
        if h is not None:
            assert isinstance(h, (float, int)), 'inversion_height must be a number got {}'.format(type(h))
            assert (h >= 0),"inversion_height must be greater than 0"
            self._inversion_height = h
        else:
            self._inversion_height = 150

    @property
    def circulation_coefficient(self):
        """Get or set the circulation coefficient."""
        return self._circulation_coefficient

    @circulation_coefficient.setter
    def circulation_coefficient(self, h):
        if h is not None:
            assert isinstance(h, (float, int)), 'circulation_coefficient must be a number got {}'.format(type(h))
            self._circulation_coefficient = h
        else:
            self._circulation_coefficient = 1.2

    @property
    def exchange_coefficient(self):
        """Get or set the exchange coefficient."""
        return self._exchange_coefficient

    @exchange_coefficient.setter
    def exchange_coefficient(self, h):
        if h is not None:
            assert isinstance(h, (float, int)), 'exchange_coefficient must be a number got {}'.format(type(h))
            self._exchange_coefficient = h
        else:
            self._exchange_coefficient = 1.0

    @property
    def isBoundaryLayerPar(self):
        """Return True for isBoundaryLayerPar."""
        return True

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Represnt Dragonfly boundary layer parameters."""
        return 'Boundary Layer Parameters: ' + \
               '\n  Boundary Height (Day | Night): ' + str(self.day_boundary_layer_height) + \
                    ' m | ' + str(self.night_boundary_layer_height) + ' m' +\
               '\n  Inversion Height: ' + str(self.inversion_height) + ' m' + \
               '\n  Circulation Coefficient: ' + str(self.circulation_coefficient) + \
               '\n  Exchange Coefficient: ' + str(self.exchange_coefficient)



checkIn = CheckIn(default_folder_)

try:
    checkIn.checkForUpdates(True)
except:
    # no internet connection
    pass

now = datetime.datetime.now()


if checkIn.letItFly:
    sc.sticky["dragonfly_release"] = versionCheck()

    if sc.sticky.has_key("dragonfly_release") and sc.sticky["dragonfly_release"]:
        # Check for the existince of the uwg folder.
        username = os.getenv("USERNAME")
        rhinoScriptsDir = 'C:\\Users\\{}\\AppData\\Roaming\\McNeel\\Rhinoceros\\6.0\\scripts\\'.format(username)
        uwgClassDir = rhinoScriptsDir + 'uwg\\'
        readDOE_file_path = os.path.join(uwgClassDir,"refdata","readDOE.pkl")
        if not os.path.isdir(rhinoScriptsDir):
            msg = "Dragonfly currently only works on Rhino 6."
            print msg
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        notWorkingUWGmsg = "You will not be able to run simulations to account for urban heat island. \n" + \
            "Use the Dragonfly installer component to (re)install the uwg or download \n" + \
            "the most recent version from here: \n" + \
            "https://github.com/chriswmackey/Dragonfly/tree/master/uwg \n" + \
            "and copy the uwg folder to here: \n" + uwgClassDir
        if not os.path.isdir(uwgClassDir):
            msg = "The Urban Weather Generator (uwg) is not currently installed. \n" + notWorkingUWGmsg
            print msg
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
            uwgClassDir = None
        else:
            try:
                from uwg import uwg
            except:
                msg = "The Urban Weather Generator (uwg) failed to load. \n" + notWorkingUWGmsg
                print msg
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
                uwgClassDir = None

        # copy the classes to memory
        if uwgClassDir != None:
            sc.sticky["dragonfly_UWGPath"] = uwgClassDir
            sc.sticky["dragonfly_UWGBldgTypes"] = BuildingTypes(readDOE_file_path)
        sc.sticky["dragonfly_BuildingTypology"] = Typology
        sc.sticky["dragonfly_City"] = City
        sc.sticky["dragonfly_Terrain"] = Terrain
        sc.sticky["dragonfly_Vegetation"] = Vegetation
        sc.sticky["dragonfly_TrafficPar"] = TrafficPar
        sc.sticky["dragonfly_VegetationPar"] = VegetationPar
        sc.sticky["dragonfly_PavementPar"] = PavementPar
        sc.sticky["dragonfly_RefEpwPar"] = RefEPWSitePar
        sc.sticky["dragonfly_BoundaryLayerPar"] = BoundaryLayerPar

        print "Hi " + os.getenv("USERNAME")+ "!\n" + \
              "Dragonfly is Flying! Vviiiiiiizzz...\n\n" + \
              "Default path is set to: " + sc.sticky["Dragonfly_DefaultFolder"] + "\n" + \
              "UWGEngine path is set to: " + str(uwgClassDir)

        # push ladybug component to back
        ghenv.Component.OnPingDocument().SelectAll()
        ghenv.Component.Attributes.Selected = False
        ghenv.Component.OnPingDocument().BringSelectionToTop()
        ghenv.Component.OnPingDocument().DeselectAll()
