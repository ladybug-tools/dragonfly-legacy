# Urban Weather Generator Parameters from Building Typologies
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
Use this component to generate paremeters for an Urban Weather Generator model using urban typologies and the ratios of each typology within the urban area.  These building typologies can generated with either the "Dragonfly_Building Typology from HBZone" or the "Dragonfly_Building Typology from Parameters" component.
_
The ouput of this component can be plugged into the 'Dragonfly_Run Urban Weather Generator' component in order to morph a rural/airport weather file to reflect the urban conditions input to this component.
-
Provided by Dragonfly 0.0.01
    Args:
        _buildingTypologies: One or more building typologies from either the "Dragonfly_Building Typology from HBZone" or the "Dragonfly_Building Typology from Parameters" component.
        typologyRatios_: A list of numbers that sum to 1 and represent the fraction of the buildings in the urban area occupied by each of the connected typologies now.  Note that the length of this list must match the number of typologies connected to the input above and that the order of this list should align with the order that you have connected typologies to the input above.  It is useful to use the "Dragonfly_Typology Ratios" component to caclulate these areas if you have the building geometry organized by typlogy.  If no values are input here, it will be assumed that each of the typologies occupies an equal amount of the built space in the urban area.
        roofAngles_: A list of numbers between 0 and 1 that that represent the dinensionless inclination angle of the roof surfaces of the building typologies:
            _
            0 = Perfectly vertical surface  (like a wall)
            0.5 = Sloped surfacece that is 45 degrees from the horizontal.
            1 = Perfectly horizontal surface (like a flat roof)
            _
            Note that the length of this list must match the number of typologies connected to the input above and that the order of this list should align with the order that you have connected typologies to the input above.  It is useful to use the "Dragonfly_Typology Ratios" component to caclulate these angles if you have the building geometry organized by typlogy.  If no values are input here, it will be assumed that all roofs are flat (with a value of 1).
        wallAngles_: A list of numbers between 0 and 1 that that represent the dinensionless inclination angle of the wall surfaces of the building typologies:
            _
            0 = Perfectly vertical surface  (like a wall)
            0.5 = Sloped surfacece that is 45 degrees from the horizontal.
            1 = Perfectly horizontal surface (like a flat roof)
            _
            Note that the length of this list must match the number of typologies connected to the input above and that the order of this list should align with the order that you have connected typologies to the input above.  It is useful to use the "Dragonfly_Typology Ratios" component to caclulate these angles if you have the building geometry organized by typlogy.  If no values are input here, it will be assumed that all walls are perfectly vertical (with a value of 0).
        --------------------: ...
        _buildingBreps: A list of closed solids that represent the buildings of the UWG City.  Note that each solid should represent one building and buildings should NOT be broken up floor-by-floor as they are for zones in the "Dragonfly_UWG Parameters from HBZones" component.  Ideally, there should be no building brep that is on top of another building brep, although this may be difficult to avoid in some urban environemnts.  Furthermore, the calculation will be more accurate if buildings with varying heights are broken up into several solids, each at a different height.
        _pavementBrep: A list of breps that represent the paved portion of the urban area.  Note that this input brep should just reflect the surface of the terrain and should not be a solid.  Also note that this surface should be coninuous beneath the ground of the HBZones and should only be interrupted in grassy areas where the user intends to connect up such grassy surfaces to the "grassBrep_" input below.  The limits of this surface will be used to determine the density of the urban area so including a surface that extends well beyond the area where the HBZones are will cause the simulation to inacurately model the density.
        treesOrCoverage_: Either a list of breps that represent the trees of the urban area that is being modeled or a number between 0 and 1 that represents that fraction of tree coverage in the urban area.  If breps are input, they will be projected to the ground plane to compute the area of tree coverage as seen from above.  Thus, simpler tree geometry like boxes that represent the tree canopies are preferred.  If nothing is input here, it will be assumed that there are no trees in the urban area.
        grassOrCoverage_: Either a list of breps that represent the grassy ground surfaces of the urban area or a number between 0 and 1 that represents that fraction of the _pavementBrep that is covered in grass. If nothing is input here, it will be assumed that there is no grass in the urban area.
        booleanedBldgs_: An optional list of boolened building solids that will be used to compute the facade area of buildings exposed to the outdoor air.  This should essentially be the same buildings plugged into the _buildingBreps input but passed through a native grasshopper "Solid Union" component.  The booleaning of solids is not done inside this component since this can be a time-intensive operation for large uban areas with a lot of buildings.  If no value is input here, it will be assumed that all building surfaces surfaces that are not a roof or floor are exposed to the outside air.
        --------------------: ...
        vegetationPar_: An optional list of Vegetation Parameters from the "Dragonfly_Vegetation Parameters" component.  If no vegetation parameters are input here, the UWG will attempt to determine the months in which vegetation is active by looking at the average monthly temperatures in the EPW file.
        pavementConstr_: A text string representing the construction of the uban pavement.  This construction can be either from the OpenStudio Library (the "Honeybee_Call from EP Construction Library" component) or it can be a custom construction from the "Honeybee_EnergyPlus Construction" component.  If no construction is input here, a default construction for asphalt will be used for simulating all paved areas of the urban neighborhood.
        nonBldgHeat_: An number that represents the anthropogenic heat generated in the urban canyon in Watts per square meter of pavement (W/m2).  This is specifcally the heat that DOES NOT originate from buildings and mostly includes heat originating from automobiles, street lighting, and human metabolism.  Typical values are:
        _
        10 W/m2 = A commercial area in Singapore
        4 W/m2 = A residential area in Singapore
        8 W/m2 = A typical part of Toulouse, France.
        _
        Values are available for some cities by Sailor: http://onlinelibrary.wiley.com/doi/10.1002/joc.2106/abstract
        nonBldgLatentFract_: A number between 0 and 1 that represents the the fraction of the nonBldgHeat_ plugged into this component that is given off as latent heat.  LAtent heat is heat that goes towards evaporating water as opposed to raising the temperature of the air.  If no value is plugged in here, it will be assumed that all of the non-building antrhopogenic heat is sensible.
        _runIt: Set to 'True' to run the component and generate UWG parameters from the connected inputs.
    Returns:
        readMe!: A report of the key variables extraced from the input geometry.
        ----------------: ...
        UWGCity: A list of city parameters that can be plugged into the "Dragonfly_Run Urban Weather Generator" component.
        ----------------: ...
        joinedBldgs: The boolean union of adjacent buildings.  This is done to ensure that a correct facade-to-site ratio is computed.
        bldgFootprints: The building geometry as projected onto the world XY plane.  This is used to determine the site coverage ratio and to perform a weighted-average of the building heights.
        treeFootprints: If tree breps are connected, this is the tree geometry as projected into the world XY plane.  This is used to determine the tree coverage of the pavement.
        pavementSrf: The pavement terrian as projected into the world XY plane.  The area of this surface along with the grass surface is used to determine all other geometric parameters.
        grassSrf: The grass terrian as projected into the world XY plane.  The area of this surface along with the pavement surface is used to determine all other geometric parameters.
"""

ghenv.Component.Name = "Dragonfly_UWG City from Typologies"
ghenv.Component.NickName = 'UWGCityFromTypology'
ghenv.Component.Message = 'VER 0.0.01\nSEP_13_2017'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "2 | GenerateUrbanClimate"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import scriptcontext as sc
import Rhino as rc
import rhinoscriptsyntax as rs

from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh


def checkTheInputs(df_textGen, df_UWGGeo):
    #Check to be sure that there are not more than 4 building typologies connected.
    checkData1 = True
    if len(_buildingTypologies) > 4:
        checkData1 = False
        warning = "At present, the Urban Weather Generator can only model up to 4 building typologies. \n This feature will hopefully be enhanced in the future. \n For the time being, please make sure that the number of typologies connected to _buildingTypologies does not exceed 4."
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        try:
            for typology in _buildingTypologies:
                if typology.startswith('  <typology'): pass
                else: checkData1 = False
            if checkData1 == False:
                warning = "The input to the _buildingTypologies does not appear to be a valid UWG Building Typology \n generated with either the 'Dragonfly_Building Typology from HBZone' or the 'Dragonfly_Building Typology from Parameters' component."
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        except:
            checkData1 = False
            warning = "Null value connected for _buildingTypologies."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Error, warning)
    
    #Check the typologyRatios_ and be sure that the length of the list matches the length of the _buildingTypologies list.
    checkData2 = False
    typologyRatios = []
    if len(typologyRatios_) != 0:
        if len(typologyRatios_) == len(_buildingTypologies):
            if sum(typologyRatios_) <= 1.01 and sum(typologyRatios_) >= 0.99:
                for count, ratio in enumerate(typologyRatios_):
                    if count != len(_buildingTypologies)-1: typologyRatios.append(int(round(ratio*100)))
                    else: typologyRatios.append(100-sum(typologyRatios))
                checkData2 = True
            else:
                warning = "The ratios connected to typologyRatios_ does not sum to 1. \n Make sure that your ratios sum to 1."
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        else:
            warning = "The number of ratios connected to typologyRatios_ does not match \n the number of typologies connected to the _buildingTypologies input."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        if len(_buildingTypologies) == 1: typologyRatios = [100]
        if len(_buildingTypologies) == 2: typologyRatios = [50, 50]
        if len(_buildingTypologies) == 3: typologyRatios = [34, 33, 33]
        if len(_buildingTypologies) == 4: typologyRatios = [25, 25, 25, 25]
        print "No value has been connected for typologyRatios. \n It will be assumed that each typology occupies an equal part of the urban area."
        checkData2 = True
    
    #Check the roofAngles_ and be sure that the length of the list matches the length of the _buildingTypologies list.
    checkData3 = True
    roofAngles = []
    if len(roofAngles_) != 0:
        if len(roofAngles_) == len(_buildingTypologies):
            for count, val in enumerate(roofAngles_):
                if val <= 1 and val >= 0: roofAngles.append(val)
                else:
                    checkData3 = False
                    warning = "One of the values connected to roofAngles_ is not between 1 and 0. \n Roof angles mut be dimensioless values between 0 and 1."
                    print warning
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        else:
            checkData3 = False
            warning = "The number of values connected to roofAngles_ does not match \n the number of typologies connected to the _buildingTypologies input."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        for val in _buildingTypologies: roofAngles.append(1)
        print "No value has been connected for roofAngles. \n It will be assumed that each typology has perfectly flat roofs."
    
    #Check the wallAngles_ and be sure that the length of the list matches the length of the _buildingTypologies list.
    checkData4 = True
    wallAngles = []
    if len(wallAngles_) != 0:
        if len(wallAngles_) == len(_buildingTypologies):
            for count, val in enumerate(wallAngles_):
                if val <= 1 and val >= 0: wallAngles.append(val)
                else:
                    checkData4 = False
                    warning = "One of the values connected to wallAngles_ is not between 1 and 0. \n Roof angles mut be dimensioless values between 0 and 1."
                    print warning
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        else:
            checkData4 = False
            warning = "The number of values connected to wallAngles_ does not match \n the number of typologies connected to the _buildingTypologies input."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        for val in _buildingTypologies: wallAngles.append(0)
        print "No value has been connected for wallAngles. \n It will be assumed that each typology has perfectly vertical walls."
    
    
    #Check to be sure that the buildingBreps are closed.
    checkData5 = True
    for brep in _buildingBreps:
        if not brep.IsSolid:
            checkData5 = False
            warning = "One of the breps in the connected _buildingBreps is not closed.  The input buildings into this component must be closed."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    
    #Set default vegetation parameters if none are connected.
    if vegetationPar_: vegetationParString = vegetationPar_
    else: vegetationParString = df_textGen.defaultVegStr
    
    #Set default pavement parameters if none are connected.
    checkData8 = True
    if pavementConstr_:
        try: pavementConstrString = df_textGen.createXMLFromEPConstr(pavementConstr_, 'urbanRoad', 'valToReplace', 'setByEPW')
        except:
            checkData8 = False
            warning = "Converting the conctruction name connected to 'pavementConstr_' failed. Note that the component cannot yet handle full EnergyPlus construction definitions."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else: pavementConstrString = df_textGen.defaultPavementStr
    
    #Set default non-Building anthropogenic heat.
    checkData6 = True
    if nonBldgLatentFract_:
        nonBldgLatentFract = nonBldgLatentFract_
        if nonBldgLatentFract < 0 or nonBldgLatentFract > 1:
            checkData6 = False
            warning = "nonBldgLatentFract_ must be between 0 and 1."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        nonBldgLatentFract = 0
        print "No value is connected for nonBldgLatentFract_ and so it will be assumed that this value is 0 and that all heat within the canyon is sensible."
    
    #Check the non-bldg sensible heat.
    checkData7 = True
    if nonBldgHeat_:
        nonBldgSensHeat = nonBldgHeat_*(1-nonBldgLatentFract)
        nonBldgLatentHeat = nonBldgHeat_*(nonBldgLatentFract)
        if nonBldgSensHeat < 0:
            checkData7 = False
            warning = "nonBldgHeat_ cannot be less than 0."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        nonBldgSensHeat = 7*(1-nonBldgLatentFract)
        nonBldgLatentHeat = 7*(nonBldgLatentFract)
        print "No value is connected for nonBldgHeat_ and so a default of 7 W/m2 will be used, which is characteristic of medium density urban areas."
    
    #Check the booleaned buildings.
    if len(booleanedBldgs_) != 0: booleanedBldgs = booleanedBldgs_
    else: booleanedBldgs = _buildingBreps
    
    #Do a final check of everything and, if it's good, project any goemtry that needs to be projected in order to extract relevant parameters.
    checkData = False
    if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True  and checkData5 == True  and checkData6 == True and checkData7 == True and checkData8 == True:
        checkData = True
    
    
    #Set Default Parameters.
    groundProjection = rc.Geometry.Transform.PlanarProjection(rc.Geometry.Plane.WorldXY)
    maxRoofAngle, maxFloorAngle = 45, 60
    
    #Make empty parameters to be filled.
    projectedBldgBreps = []
    projectedTreeBreps = []
    projectedPaveBreps = []
    projectedGrassBreps = []
    
    buildingBrepAreas = []
    buildingHeights = []
    selfIntersectList = []
    srfNormalVecs = []
    totalBuiltArea = 0
    totalPavedArea = 0
    totalGrassArea = 0
    totalTreeArea = 0
    totalTerrainArea = 0
    
    #Define the final variables that we need.
    averageBuildingHeight = 0
    siteCoverageRatio = 0
    totalGrassCoverage = 0
    totalTreeCoverage = 0
    characteristicLength = 500
    
    
    #Project geometry into the XYPlane to extract the 
    if checkData == True:
        # Project the building breps into the XYPlane and extract the horizontal area.
        buildingBreps = []
        for bldg in _buildingBreps:
            buildingBreps.append(bldg.DuplicateBrep())
        bldgVertices = []
        bldgHeights = []
        
        for brep in buildingBreps:
            #Pull out info related to bldg heights and neighborhood boundaries.
            bldgBBox = rc.Geometry.Brep.GetBoundingBox(brep, rc.Geometry.Plane.WorldXY)
            bldgHeights.append(bldgBBox.Diagonal[2])
            bldgVertices.extend(brep.DuplicateVertices())
            
            #Pull out the projected building footprints.
            #Separate out the surfaces of the Brep
            footPrintBreps, upSrfs, sideSrfs, sideNormals, roofNormals, topNormVectors, allCentPts, allNormVectors = df_UWGGeo.separateBrepSrfs(brep, maxRoofAngle, maxFloorAngle)
            
            #Collect the surface normals.
            srfNormalVecs.append(allNormVectors)
            
            #Check to see if there are any building breps that self-intersect once they are projected into the XYPlane.  If so, we have to use an alternative method.
            meshedBrep = rc.Geometry.Mesh.CreateFromBrep(brep, rc.Geometry.MeshingParameters.Coarse)
            selfIntersect = False
            for count, normal in enumerate(topNormVectors):
                srfRay = rc.Geometry.Ray3d(allCentPts[count], normal)
                for mesh in meshedBrep:
                    intersectTest = rc.Geometry.Intersect.Intersection.MeshRay(mesh, srfRay)
                    if intersectTest <= sc.doc.ModelAbsoluteTolerance: pass
                    else: selfIntersect = True
            selfIntersectList.append(selfIntersect)
            
            if selfIntersect == True:
                # Use any downward-facing surfaces that we can identify as part of the building footprint and boolean them together to get the projected area.
                grounBreps = []
                for srf in footPrintBreps:
                    srf.Transform(groundProjection)
                    grounBreps.append(srf)
                booleanSrf = rc.Geometry.Brep.CreateBooleanUnion(grounBreps, sc.doc.ModelAbsoluteTolerance)[0]
                buildingBrepAreas.append(rc.Geometry.AreaMassProperties.Compute(booleanSrf).Area)
                projectedBldgBreps.append(booleanSrf)
            else:
                #Project the whole building brep into the X/Y plane and take half its area.
                brep.Transform(groundProjection)
                buildingBrepAreas.append(rc.Geometry.AreaMassProperties.Compute(brep).Area/2)
                projectedBldgBreps.append(brep)
        
        totalBuiltArea = sum(buildingBrepAreas)
        
        #Use the projected building breps to estimate the neighborhood characteristic length.
        neighborhoodBB = rc.Geometry.BoundingBox(bldgVertices)
        neighborhoodDiagonal = neighborhoodBB.Diagonal
        characteristicLength = neighborhoodDiagonal.Length/2
        
        #Get an area-weighted average building height.
        multipliedBldgHeights = [a*b for a,b in zip(buildingBrepAreas,bldgHeights)]
        averageBuildingHeight = sum(multipliedBldgHeights)/totalBuiltArea
        
        #Project the pavement breps into the XYPlane and extract their area.
        groundAreas = []
        for srf in _pavementBrep:
            if not srf.IsSolid:
                srf.Transform(groundProjection)
                groundAreas.append(rc.Geometry.AreaMassProperties.Compute(srf).Area)
            else:
                srf.Transform(groundProjection)
                groundAreas.append(rc.Geometry.AreaMassProperties.Compute(srf).Area/2)
            projectedPaveBreps.append(srf)
        totalPavedArea = sum(groundAreas) - totalBuiltArea
        
        #Project the grass breps into the XYPlane and extract their area.
        if len(grassOrCoverage_) != 0:
            try:
                #The user has connected a single number to represent the fraction of the ground covered in grass
                totalGrassCoverage = float(grassOrCoverage_[0])
                if totalGrassCoverage >= 0 or totalGrassCoverage <=1: pass
                else:
                    checkData = False
                    warning = "If you are inputting a number for grassOrCoverage_, this number must be between 0 and 1."
                    print warning
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            except:
                grassAreas = []
                for brep in grassOrCoverage_:
                    srf = rs.coercebrep(brep)
                    if not srf.IsSolid:
                        srf.Transform(groundProjection)
                        grassAreas.append(rc.Geometry.AreaMassProperties.Compute(srf).Area)
                    else:
                        srf.Transform(groundProjection)
                        grassAreas.append(rc.Geometry.AreaMassProperties.Compute(srf).Area/2)
                    projectedGrassBreps.append(srf)
                totalGrassArea = sum(grassAreas)
                totalGrassCoverage = totalGrassArea/(totalPavedArea+totalGrassArea)
        
        #Replace the vegetation coverage in the ground construction.
        pavementConstrStringSplit = pavementConstrString.split('valToReplace')
        pavementConstrString = pavementConstrStringSplit[0] + str(totalGrassCoverage) + pavementConstrStringSplit[-1]
        
        #With all of the ground breps accounted for, compute the siteCoverageRatio.
        totalTerrainArea = totalBuiltArea + totalPavedArea + totalGrassCoverage
        siteCoverageRatio = totalBuiltArea / totalTerrainArea
        
        #Project the tree breps into the XYPlane and extract their area.
        if len(treesOrCoverage_) != 0:
            try:
                #The user has connected a single number to represent the fraction of the ground covered in grass
                totalTreeCoverage = float(treesOrCoverage_[0])
                if totalTreeCoverage >= 0 or totalTreeCoverage <=1: pass
                else:
                    checkData = False
                    warning = "If you are inputting a number for treesOrCoverage_, this number must be between 0 and 1."
                    print warning
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            except:
                treeAreas = []
                for brep in treesOrCoverage_:
                    srf = rs.coercebrep(brep)
                    if not srf.IsSolid:
                        srf.Transform(groundProjection)
                        treeAreas.append(rc.Geometry.AreaMassProperties.Compute(srf).Area)
                    else:
                        srf.Transform(groundProjection)
                        treeAreas.append(rc.Geometry.AreaMassProperties.Compute(srf).Area/2)
                    projectedTreeBreps.append(srf)
                totalTreeArea = sum(treeAreas)
                totalTreeCoverage = totalTreeArea/(totalPavedArea + totalGrassArea)
    
    
    return checkData, _buildingTypologies, _buildingBreps, buildingBrepAreas, srfNormalVecs, typologyRatios, roofAngles, wallAngles, averageBuildingHeight, siteCoverageRatio, totalGrassCoverage, totalTreeCoverage, vegetationParString, pavementConstrString, nonBldgSensHeat, nonBldgLatentHeat, characteristicLength, totalTerrainArea, projectedBldgBreps, projectedTreeBreps, projectedPaveBreps, projectedGrassBreps, booleanedBldgs


def createMatStr(name, thermalConduct, heatCapacity, thickness):
    # Write in the material name.
    constrStr = '          <names>\n'
    constrStr = constrStr + '            <item>' + name + '</item>\n'
    constrStr = constrStr + '          </names>\n'
    
    # Next, write in the thermal conductivity.
    constrStr = constrStr + '          <thermalConductivity>\n'
    constrStr = constrStr + '            <item>' + str(thermalConduct) + '</item>\n'
    constrStr = constrStr + '          </thermalConductivity>\n'
    
    # Next, write in the heat capacity.
    constrStr = constrStr + '          <volumetricHeatCapacity>\n'
    constrStr = constrStr + '            <item>' + str(heatCapacity) + '</item>\n'
    constrStr = constrStr + '          </volumetricHeatCapacity>\n'
    
    # Finally, write in the thickness.
    constrStr = constrStr + '          <thickness>' +  str([float(thickness)]) + '</thickness>\n'
    
    
    return constrStr


def main(buildingTypologies, buildingBreps, buildingBrepAreas, srfNormalVecs, typologyRatios, roofAngles, wallAngles, averageBuildingHeight, siteCoverageRatio, totalGrassCoverage, totalTreeCoverage, vegetationParString, pavementConstrString, nonBldgSensHeat, nonBldgLatentHeat, characteristicLength, totalTerrainArea, booleanedBldgs):
    
    #Use the final adjacency list to select out the breps that are adjacent to one another and boolean union them together.
    ### I am bypassing this now until I can put it in its own adjacency-solving component.
    adjacentBrepsList = []
    adjacentBrepAreaList = []
    totalBuildingAreaList = []
    totalGroundAreaList = []
    booleanBuildings = []
    
    #Get the surface areas of booleaned buildings.
    for listCount, brep in enumerate(booleanedBldgs):
        totalBuildingAreaList.append(rc.Geometry.AreaMassProperties.Compute(brep).Area)
    
    #Compute the facade to site ratio by subtracting twice the building footprint from the total shape area.
    facade2SiteRatio = (sum(totalBuildingAreaList)-(2*sum(buildingBrepAreas)))/totalTerrainArea
    
    
    #Create the urban area string.
    urbanString = "  <urbanArea>\n"
    urbanString = urbanString + "    <averageBuildingHeight>" + str(averageBuildingHeight) + "</averageBuildingHeight>\n"
    urbanString = urbanString + "    <siteCoverageRatio>" + str(siteCoverageRatio) + '</siteCoverageRatio>\n'
    urbanString = urbanString + "    <facadeToSiteRatio>" + str(facade2SiteRatio) + '</facadeToSiteRatio>\n'
    urbanString = urbanString + "    <treeCoverage>" + str(totalTreeCoverage) + '</treeCoverage>\n'
    urbanString = urbanString + "    <nonBldgSensibleHeat>" + str(nonBldgSensHeat) + '</nonBldgSensibleHeat>\n'
    urbanString = urbanString + "    <nonBldgLatentAnthropogenicHeat>" + str(nonBldgLatentHeat) + '</nonBldgLatentAnthropogenicHeat>\n'
    urbanString = urbanString + "    <charLength>" + str(characteristicLength) + '</charLength>\n'
    urbanString = urbanString +  vegetationParString
    urbanString = urbanString + "    <daytimeBLHeight>700</daytimeBLHeight>\n"
    urbanString = urbanString + "    <nighttimeBLHeight>80</nighttimeBLHeight>\n"
    urbanString = urbanString + "    <refHeight>150</refHeight>\n"
    urbanString = urbanString +  pavementConstrString
    urbanString = urbanString + "  </urbanArea>\n"
    
    #Swap out the portions of the building typologies that we have caulculated (like fraction of each in the urban area and roof angle).
    #Replace the typology ratio in the typology string.
    newBuildingTypologies = []
    for count, typString in enumerate(buildingTypologies):
        newTypString = typString.replace('TBDPercent', str(typologyRatios[count]))
        newBuildingTypologies.append(newTypString)
    buildingTypologies = newBuildingTypologies
    
    #Replace the roof angle in the typology string.
    newBuildingTypologies = []
    for count, typString in enumerate(buildingTypologies):
        typStringSplit = typString.split('inclination')
        newTypString = typStringSplit[0] + 'inclination' + typStringSplit[1] + 'inclination' + typStringSplit[2] + 'inclination>' + str(round(roofAngles[count],2)) + '</inclination'
        for count, string in enumerate(typStringSplit[4:]):
            if count != len(typStringSplit[4:])-1: newTypString = newTypString + string + 'inclination'
            else: newTypString = newTypString + string
        newBuildingTypologies.append(newTypString)
    buildingTypologies = newBuildingTypologies
    
    #Replace the roof angle in the typology string.
    newBuildingTypologies = []
    for count, typString in enumerate(buildingTypologies):
        typStringSplit = typString.split('inclination')
        newTypString = typStringSplit[0] + 'inclination>' + str(round(wallAngles[count], 2)) + '</inclination'
        for count, string in enumerate(typStringSplit[2:]):
            if count != len(typStringSplit[2:])-1: newTypString = newTypString + string + 'inclination'
            else: newTypString = newTypString + string
        newBuildingTypologies.append(newTypString)
    buildingTypologies = newBuildingTypologies
    
    #Replace the typology number in the typology string.
    newBuildingTypologies = []
    for count, typString in enumerate(buildingTypologies):
        strToReplace1 = '<typology' + str(count+1)
        strToReplace2 = '</typology' + str(count+1)
        newTypString1 = typString.replace('<typology1', strToReplace1)
        newTypString2 = newTypString1.replace('</typology1', strToReplace2)
        newBuildingTypologies.append(newTypString2)
    buildingTypologies = newBuildingTypologies
    
    #Add blank typologies to the UWGString.
    if len(buildingTypologies) < 2: buildingTypologies =  buildingTypologies + [df_textGen.createBlankTypology(2)]
    if len(buildingTypologies) < 3: buildingTypologies =  buildingTypologies + [df_textGen.createBlankTypology(3)]
    if len(buildingTypologies) < 4: buildingTypologies =  buildingTypologies + [df_textGen.createBlankTypology(4)]
    
    #Combine everything into one string.
    UWGPar = '<?xml version="1.0" encoding="utf-8"?>\n<xml_input>\n'
    for typ in buildingTypologies:
        UWGPar = UWGPar + typ
    UWGPar = UWGPar + urbanString
    
    #Print out a report of important information
    print '_'
    print 'Average Building Height = ' + str(round(averageBuildingHeight, 1)) + ' meters'
    print 'Site Coverage Ratio =     ' + str(round(siteCoverageRatio, 2))
    print 'Facade To Site Ratio =    ' + str(round(facade2SiteRatio, 2))
    print 'Total Grass Coverage =    ' + str(round(totalGrassCoverage, 2))
    print 'Total Tree Coverage =     ' + str(round(totalTreeCoverage, 2))
    print 'Characteristic Length =   ' + str(int(characteristicLength)) + ' meters'
    
    
    return UWGPar, buildingBreps



#Check to be sure that Dragonfly is flying.
initCheck = False
if sc.sticky.has_key('honeybee_release') and sc.sticky.has_key("dragonfly_release"):
    df_textGen = sc.sticky["dragonfly_UWGText"]()
    df_UWGGeo = sc.sticky["dragonfly_UWGGeometry"]()
    initCheck = True
else:
    if not sc.sticky.has_key("honeybee_release"):
        warning = "You need to let Honeybee  fly to use this component."
        print warning
    if not sc.sticky.has_key("dragonfly_release"):
        warning = "You need to let Dragonfly fly to use this component."
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)



if initCheck == True and _runIt == True and len(_buildingTypologies) != 0 and len(_buildingBreps) != 0 and len(_pavementBrep) != 0:
    checkData, buildingTypologies, buildingBreps, buildingBrepAreas, srfNormalVecs, typologyRatios, roofAngles, wallAngles, averageBuildingHeight, siteCoverageRatio, totalGrassCoverage, totalTreeCoverage, vegetationParString, pavementConstrString, nonBldgSensHeat, nonBldgLatentHeat, characteristicLength, totalTerrainArea, bldgFootprints, treeFootprints, pavementSrf, grassSrf, booleanedBldgs = checkTheInputs(df_textGen, df_UWGGeo)
    if checkData == True:
        UWGCity, joinedBldgs = main(buildingTypologies, buildingBreps, buildingBrepAreas, srfNormalVecs, typologyRatios, roofAngles, wallAngles, averageBuildingHeight, siteCoverageRatio, totalGrassCoverage, totalTreeCoverage, vegetationParString, pavementConstrString, nonBldgSensHeat, nonBldgLatentHeat, characteristicLength, totalTerrainArea, booleanedBldgs)

