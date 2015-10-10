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
        _runIt: Set to 'True' to run the component and calculate the ratios of typologies in the urban area.
    Returns:
        typologyRatios: A list of typology ratios that can be plugged into the "Dragonfly_UWG Parameters from Typologies" component.
        projectedBreps: The typology geometry as projected onto the worrldXY plane, which is used to determine the appropriate ratios.
"""

ghenv.Component.Name = "Dragonfly_Typology Ratios"
ghenv.Component.NickName = 'TypologyRatios'
ghenv.Component.Message = 'VER 0.0.57\nOCT_10_2015'
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
    typologies = [_typology1Breps_, _typology2Breps_, _typology3Breps_, _typology4Breps_]
    typologyProjectedBreps = []
    typologyAreas = []
    typologyRatio = []
    
    #Define a maximum floor angle and a transformation for projection.
    maximumFloorAngle = 60
    groundProjection = rc.Geometry.Transform.PlanarProjection(rc.Geometry.Plane.WorldXY)
    
    # Make a function that attempts to extrac the building footprint surfaces.
    def getBrepDownSrfs(brep):
        downSrfs = []
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
            
            if  180 - maximumFloorAngle < angle2Z < 180 + maximumFloorAngle:
                downSrfs.append(surface)
        
        return downSrfs
    
    # Use any downward-facing surfaces that we can identify as part of the building footprint to get the projected area.
    for typology in typologies:
        typAreas = []
        typeProjBreps = []
        for brep in typology:
            footPrintBreps = getBrepDownSrfs(brep)
            for srf in footPrintBreps:
                #Project the surface into the X/Y plane.
                srf.Transform(groundProjection)
                typAreas.append(rc.Geometry.AreaMassProperties.Compute(srf).Area)
                typeProjBreps.append(srf)
        
        typologyProjectedBreps.append(typeProjBreps)
        typologyAreas.append(sum(typAreas))
    
    #Calculate the ratios.
    totalArea = sum(typologyAreas)
    for area in typologyAreas: typologyRatio.append(area/totalArea)
    
    
    return typologyRatio, typologyProjectedBreps


if sc.sticky.has_key('dragonfly_release') == True:
    df_UWGGeo = sc.sticky["dragonfly_UWGGeometry"]()
else:
    print "You should first let Dragonfly  fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Dragonfly fly...")


if len(_typology1Breps_) != 0 or len(_typology2Breps_) != 0 or len(_typology1Breps_) != 0 or len(_typology1Breps_) != 0:
    if _runIt:
        checkData = checkInputs()
        if checkData == True:
             result = main(df_UWGGeo)
             if result != -1:
                 typologyRatios, projectedBrepsInit = result
                 
                 projectedBreps = DataTree[Object]()
                 for dataCount, dataList in enumerate(projectedBrepsInit):
                    for item in dataList: projectedBreps.Add(item, GH_Path(dataCount))