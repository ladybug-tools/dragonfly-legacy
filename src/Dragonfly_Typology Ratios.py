#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2015, Mostapha Sadeghipour Roudsari <Sadeghipour@gmail.com> 
# Honeybee is free software; you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published 
# by the Free Software Foundation; either version 3 of the License, 
# or (at your option) any later version. 
# 
# Honeybee is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Use this component to take building brep geometries that represent certain typologies and produce a list of typologyRatios that can be plugged into the "Dragonfly_UWG Parameters from Typologies" component.  Note that the UWG cannot currently take more than 4 typologies.
-
Provided by Dragonfly 0.0.01
    Args:
        _typology1Breps_: The breps representing the buildings of the first typology connected to the _buildingTypologies input above.
        _typology2Breps_: The breps representing the buildings of the second typology connected to the _buildingTypologies input above.
        _typology3Breps_: The breps representing the buildings of the third typology connected to the _buildingTypologies input above.
        _typology4Breps_: The breps representing the buildings of the fourth typology connected to the _buildingTypologies input above.
        maxRoofAngle_: An optional number in degrees that represents the maximum angle from the horizontal from which a given surface is considered a roof (as opposed to a wall).  This number should not exceed 90 degrees.  The default is set to 45.
        maxFloorAngle_: An optional number in degrees that represents the maximum angle from the horizontal from which a given surface is considered a floor (as opposed to a wall).  This number should not exceed 90 degrees.  The default is set to 60.
    Returns:
        typologyRatios: A list of typology ratios that can be plugged into the "Dragonfly_UWG Parameters from Typologies" component.
        wallAngles: A list of dimensionless inclination angles for the walls of each typology, which can be plugged into the "Dragonfly_UWG Parameters from Typologies" component.
        roofAngless: A list of dimensionless inclination angles for the roofs of each typology, which can be plugged into the "Dragonfly_UWG Parameters from Typologies" component.
        ----------------: ...
        roofBreps: The typology roof geometry.  This is used to determine the roof inclination angles.
        wllBreps: The typology wall geometry.  This is used to determine the wall inclination angles.
        footpringBreps: The typology building footprint geometry as projected onto the worrldXY plane.  This is used to determine the ratios of each typology in the uarban area.
"""

ghenv.Component.Name = "Dragonfly_Typology Ratios"
ghenv.Component.NickName = 'TypologyRatios'
ghenv.Component.Message = 'VER 0.0.57\nOCT_11_2015'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "2 | GenerateUrbanClimate"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "5"
except: pass


import Rhino as rc
import scriptcontext as sc
import math

from System import Object
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path

from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh


def checkInputs():
    checkData = True
    
    #Define a function that checks each typology.
    def ckeckTypology(breps, typeName):
        typeOK = True
        try:
            if breps[0] == None:
                checkData = False
                typeOK = False
                warning = "Null value connected for " + typeName + "."
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        except: pass
        
        if typeOK == True:
            for brep in breps:
                if not brep.IsSolid:
                    checkData = False
                    warning = "One of the breps in " + typeName + " is not closed.  The input buildings into this component must be closed."
                    print warning
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    
    ckeckTypology(_typology1Breps_, 'Typology 1')
    ckeckTypology(_typology2Breps_, 'Typology 2')
    ckeckTypology(_typology3Breps_, 'Typology 3')
    ckeckTypology(_typology4Breps_, 'Typology 4')
    
    return checkData


def main(df_UWGGeo):
    #Put all of the typologies into one list and set up lists to be filled
    typologies = []
    if len(_typology1Breps_): typologies.append(_typology1Breps_)
    if len(_typology2Breps_): typologies.append(_typology2Breps_)
    if len(_typology3Breps_): typologies.append(_typology3Breps_)
    if len(_typology4Breps_): typologies.append(_typology4Breps_)
    
    #Make empty lists of the outputs to be filled.
    typologyProjectedBreps = []
    typologyRoofBreps = []
    typologyWallBreps = []
    typologyRoofNormals = []
    typologyWallNormals = []
    typologyAreas = []
    typologyRatio = []
    
    #Define a default minimum and maximum floor angle if none is connected.
    if maxFloorAngle_ != None: maxFloorAngle = maxFloorAngle_
    else: maxFloorAngle = 45
    if maxRoofAngle_ != None: maxRoofAngle = maxRoofAngle_
    else: maxRoofAngle = 60
    groundProjection = rc.Geometry.Transform.PlanarProjection(rc.Geometry.Plane.WorldXY)
    
    # Make a function that attempts to extrac the building footprint surfaces.
    def separateBrepSrfs(brep):
        up = []
        down = []
        side = []
        roofNormals = []
        sideNormals = []
        for i in range(brep.Faces.Count):
            surface = brep.Faces[i].DuplicateFace(False)
            # find the normal
            findNormal = df_UWGGeo.getSrfCenPtandNormal(surface)
            
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
            else:
                side.append(surface)
                sideNormals.append((90 - angle2Z)/90)
        
        return down, sideNormals, roofNormals, up, side
    
    # Use any downward-facing surfaces that we can identify as part of the building footprint to get the projected area.
    for typology in typologies:
        typAreas = []
        typeProjBreps = []
        typeRoofBreps = []
        typeWallBreps = []
        typeRoofNormals = []
        typeWallNormals = []
        
        for brep in typology:
            footPrintBreps, sideNormals, roofNormals, upSrfs, sideSrfs = separateBrepSrfs(brep)
            
            #Project the ground surface into the X/Y plane and take its area.
            groundAreas = []
            for srf in footPrintBreps:
                srf.Transform(groundProjection)
                groundAreas.append(rc.Geometry.AreaMassProperties.Compute(srf).Area)
                typeProjBreps.append(srf)
            typAreas.append(sum(groundAreas))
            
            #Use the area of the roof surfaces to get a weighted average roof angle.
            roofSrfAreas = []
            for srfCount, srf in enumerate(upSrfs):
                roofSrfAreas.append(rc.Geometry.AreaMassProperties.Compute(srf).Area)
                typeRoofBreps.append(srf)
            totalRoofArea = sum(roofSrfAreas)
            multipliedRoofNormals = [a*b for a,b in zip(roofSrfAreas,roofNormals)]
            weightedAvgRoofAngle = sum(multipliedRoofNormals)/totalRoofArea
            typeRoofNormals.append(weightedAvgRoofAngle)
            
            #Use the area of the wall surfaces to get a weighted average wall angle.
            wallSrfAreas = []
            for srfCount, srf in enumerate(sideSrfs):
                wallSrfAreas.append(rc.Geometry.AreaMassProperties.Compute(srf).Area)
                typeWallBreps.append(srf)
            totalWallArea = sum(wallSrfAreas)
            multipliedWallNormals = [a*b for a,b in zip(wallSrfAreas,sideNormals)]
            weightedAvgWallAngle = sum(multipliedWallNormals)/totalWallArea
            if weightedAvgWallAngle < 0: typeWallNormals.append(0)
            else: typeWallNormals.append(weightedAvgWallAngle)
        
        
        #Append the ground surfaces to their respective list.
        totalTypArea = sum(typAreas)
        typologyProjectedBreps.append(typeProjBreps)
        typologyAreas.append(totalTypArea)
        
        #Append the wall and roof surfaces to their lists.
        typologyRoofBreps.append(typeRoofBreps)
        typologyWallBreps.append(typeWallBreps)
        
        #Perform a weighted average of the roof and wall normals for the typology.
        multipliedWallAngles = [a*b for a,b in zip(typAreas,typeWallNormals)]
        weightedAvgWallAngle = sum(multipliedWallAngles)/totalTypArea
        typologyWallNormals.append(weightedAvgWallAngle)
        multipliedRoofAngles = [a*b for a,b in zip(typAreas,typeRoofNormals)]
        weightedAvgRoofAngle = sum(multipliedRoofAngles)/totalTypArea
        typologyRoofNormals.append(weightedAvgRoofAngle)
    
    #Calculate the ratio of each typology in the urban area.
    totalArea = sum(typologyAreas)
    for area in typologyAreas: typologyRatio.append(area/totalArea)
    
    
    return typologyRatio, typologyRoofNormals, typologyWallNormals, typologyRoofBreps, typologyWallBreps, typologyProjectedBreps


if sc.sticky.has_key('dragonfly_release') == True:
    df_UWGGeo = sc.sticky["dragonfly_UWGGeometry"]()
else:
    print "You should first let Dragonfly  fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Dragonfly fly...")


if len(_typology1Breps_) != 0 or len(_typology2Breps_) != 0 or len(_typology1Breps_) != 0 or len(_typology1Breps_) != 0:
    checkData = checkInputs()
    if checkData == True:
        result = main(df_UWGGeo)
        if result != -1:
            typologyRatios, roofAngles, wallAngles, roofBrepsInit, wallBrepsInit, footprintBrepsInit = result
            
            roofBreps = DataTree[Object]()
            wallBreps = DataTree[Object]()
            footprintBreps = DataTree[Object]()
            for dataCount, dataList in enumerate(footprintBrepsInit):
                for item in dataList: footprintBreps.Add(item, GH_Path(dataCount))
            for dataCount, dataList in enumerate(roofBrepsInit):
                for item in dataList: roofBreps.Add(item, GH_Path(dataCount))
            for dataCount, dataList in enumerate(wallBrepsInit):
                for item in dataList: wallBreps.Add(item, GH_Path(dataCount))
            
            #Hide unwanted outputs
            ghenv.Component.Params.Output[4].Hidden = True
            ghenv.Component.Params.Output[5].Hidden = True