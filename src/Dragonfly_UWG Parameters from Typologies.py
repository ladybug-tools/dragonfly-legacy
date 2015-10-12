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
        _buildingBreps: A list of closed solids that represent the buildings of the urban area for which UWGParamters are being created.  Note that each solid should represent one building and buildings should NOT be broken up floor-by-floor as they are for zones in the "Dragonfly_UWG Parameters from HBZones" component.  Ideally, there should be no building brep that is on top of another building brep, although this may be difficult to avoid in some urban environemnts.  Furthermore, the calculation will be more accurate if buildings with varying heights are broken up into several solids, each at a different height.
        _pavementBrep: A list of breps that represent the paved portion of the urban area.  Note that this input brep should just reflect the surface of the terrain and should not be a solid.  Also note that this surface should be coninuous beneath the ground of the HBZones and should only be interrupted in grassy areas where the user intends to connect up such grassy surfaces to the "grassBrep_" input below.  The limits of this surface will be used to determine the density of the urban area so including a surface that extends well beyond the area where the HBZones are will cause the simulation to inacurately model the density.
        treeBrepsOrCoverage_: Either a list of breps that represent the trees of the urban area that is being modeled or a number between 0 and 1 that represents that fraction of tree coverage in the urban area.  If breps are input, they will be projected to the ground plane to compute the area of tree coverage as seen from above.  Thus, simpler tree geometry like boxes that represent the tree canopies are preferred.  If nothing is input here, it will be assumed that there are no trees in the urban area.
        grassBrepOrCoverage_: Either a list of breps that represent the grassy ground surfaces of the urban area or a number between 0 and 1 that represents that fraction of the _pavementBrep that is covered in grass. If nothing is input here, it will be assumed that there is no grass in the urban area.
        --------------------: ...
        vegetationPar_: An optional list of Vegetation Parameters from the "Dragonfly_Vegetation Parameters" component.  If no vegetation parameters are input here, the UWG will attempt to determine the months in which vegetation is active by looking at the average monthly temperatures in the EPW file.
        pavementConstr_: A text string representing the construction of the uban pavement.  This construction can be either from the OpenStudio Library (the "Honeybee_Call from EP Construction Library" component) or it can be a custom construction from the "Honeybee_EnergyPlus Construction" component.  If no construction is input here, a default construction for asphalt will be used for simulating all paved areas of the urban neighborhood.
        nonBldgAnthroHeat_: An number that represents the anthropogenic heat generated in the urban canyon in Watts per square meter of pavement (W/m2).  This is specifcally the heat that DOES NOT originate from buildings and mostly includes heat originating from automobiles, street lighting, and human metabolism.  Typical values are:
        _
        10 W/m2 = A commercial area in Singapore
        4 W/m2 = A residential area in Singapore
        8 W/m2 = A typical part of Toulouse, France.
        _
        Values are available for some cities by Sailor: http://onlinelibrary.wiley.com/doi/10.1002/joc.2106/abstract
        nonBldgLatentFract_: A number between 0 and 1 that represents the the fraction of the nonBldgAnthroHeat_ plugged into the 'Dragonfly_UWG Parameters' component that is given off as latent heat.  LAtent heat is heat that goes towards evaporating water as opposed to raising the temperature of the air.  If no value is plugged in here, it will be assumed that all of the non-building antrhopogenic heat is sensible.
        --------------------: ...
        _runIt: Set to 'True' to run the component and generate UWG parameters from the connected inputs.
    Returns:
        UWGParameters: A list of parameters that can be plugged into the "Dragonfly_Run Urban Weather Generator" component.
"""

ghenv.Component.Name = "Dragonfly_UWG Parameters from Typologies"
ghenv.Component.NickName = 'UWGParFromTypology'
ghenv.Component.Message = 'VER 0.0.01\nOCT_11_2015'
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
        for typology in _buildingTypologies:
            if typology.startswith('  <typology'): pass
            else: checkData1 = False
        if checkData1 == False:
            warning = "The input to the _buildingTypologies does not appear to be a valid UWG Building Typology \n generated with either the 'Dragonfly_Building Typology from HBZone' or the 'Dragonfly_Building Typology from Parameters' component."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    
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
        if len(_buildingTypologies) == 3: typologyRatios = [33, 33, 34]
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
        try: pavementConstrString = df_textGen.createXMLFromEPConstr(pavementConstr_, 'pavement', 'valToReplace', 'setByEPW')
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
    
    checkData7 = True
    if nonBldgAnthroHeat_:
        nonBldgAnthroHeat = nonBldgAnthroHeat_*(1-nonBldgLatentFract)
        if nonBldgAnthroHeat < 0:
            checkData7 = False
            warning = "nonBldgAnthroHeat_ cannot be less than 0."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        nonBldgAnthroHeat = 7*(1-nonBldgLatentFract)
        print "No value is connected for nonBldgAnthroHeat_ and so a default of 7 W/m2 will be used, which is characteristic of medium density urban areas."
    
    
    #Do a final check of everything and, if it's good, project any goemtry that needs to be projected in order to extract relevant parameters.
    checkData = False
    if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True  and checkData5 == True  and checkData6 == True and checkData7 == True and checkData8 == True:
        checkData = True
    
    
    #Make empty parameters to be filled.
    groundProjection = rc.Geometry.Transform.PlanarProjection(rc.Geometry.Plane.WorldXY)
    buildingBrepAreas = []
    buildingHeights = []
    totalBuiltArea = 0
    totalPavedArea = 0
    totalGrassArea = 0
    totalTreeArea = 0
    
    #Define the final variables that we need.
    averageBuildingHeight = 0
    siteCoverageRatio = 0
    totalGrassCoverage = 0
    totalTreeCoverage = 0
    characteristicLength = 500
    
    
    #Project geometry into the XYPlane to extract the 
    if checkData == True:
        # Project the building breps into the XYPlane and extract the horizontal area.
        buildingBreps = _buildingBreps[:]
        bldgVertices = []
        bldgHeights = []
        for brep in buildingBreps:
            bldgBBox = rc.Geometry.Brep.GetBoundingBox(brep, rc.Geometry.Plane.WorldXY)
            bldgHeights.append(bldgBBox.Diagonal[2])
            brep.Transform(groundProjection)
            buildingBrepAreas.append(rc.Geometry.AreaMassProperties.Compute(brep).Area/2)
            bldgVertices.extend(brep.DuplicateVertices())
        totalBuiltArea = sum(buildingBrepAreas)
        
        #Use the projected building breps to estimate the neightborhood characteristic length.
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
        totalPavedArea = sum(groundAreas) - totalBuiltArea
        
        #Project the grass breps into the XYPlane and extract their area.
        if len(grassBrepOrCoverage_) != 0:
            try:
                #The user has connected a single number to represent the fraction of the ground covered in grass
                totalGrassCoverage = float(grassBrepOrCoverage_[0])
                if totalGrassCoverage >= 0 or totalGrassCoverage <=1: pass
                else:
                    checkData = False
                    warning = "If you are inputting a number for grassBrepOrCoverage_, this number must be between 0 and 1."
                    print warning
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            except:
                grassAreas = []
                for brep in grassBrepOrCoverage_:
                    srf = rs.coercebrep(brep)
                    if not srf.IsSolid:
                        srf.Transform(groundProjection)
                        grassAreas.append(rc.Geometry.AreaMassProperties.Compute(srf).Area)
                    else:
                        srf.Transform(groundProjection)
                        grassAreas.append(rc.Geometry.AreaMassProperties.Compute(srf).Area/2)
                totalGrassArea = sum(grassAreas)
                totalGrassCoverage = totalGrassArea/(totalPavedArea+totalGrassArea)
        
        #Replace the vegetation coverage in the ground construction.
        pavementConstrStringSplit = pavementConstrString.split('valToReplace')
        pavementConstrString = pavementConstrStringSplit[0] + str(totalGrassCoverage) + pavementConstrStringSplit[-1]
        
        #With all of the ground breps accounted for, compute the siteCoverageRatio.
        siteCoverageRatio = totalBuiltArea / (totalBuiltArea + totalPavedArea + totalGrassCoverage)
        
        #Project the tree breps into the XYPlane and extract their area.
        if len(treeBrepsOrCoverage_) != 0:
            try:
                #The user has connected a single number to represent the fraction of the ground covered in grass
                totalTreeCoverage = float(treeBrepsOrCoverage_[0])
                if totalTreeCoverage >= 0 or totalTreeCoverage <=1: pass
                else:
                    checkData = False
                    warning = "If you are inputting a number for treeBrepsOrCoverage_, this number must be between 0 and 1."
                    print warning
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            except:
                treeAreas = []
                for brep in treeBrepsOrCoverage_:
                    srf = rs.coercebrep(brep)
                    if not srf.IsSolid:
                        srf.Transform(groundProjection)
                        treeAreas.append(rc.Geometry.AreaMassProperties.Compute(srf).Area)
                    else:
                        srf.Transform(groundProjection)
                        treeAreas.append(rc.Geometry.AreaMassProperties.Compute(srf).Area/2)
                totalTreeArea = sum(treeAreas)
                totalTreeCoverage = totalTreeArea/(totalPavedArea + totalGrassArea)
    
    #Print out a report of important information
    print '_'
    print 'averageBuildingHeight = ' + str(averageBuildingHeight) + ' meters'
    print 'siteCoverageRatio = ' + str(siteCoverageRatio)
    print 'totalGrassCoverage = ' + str(totalGrassCoverage)
    print 'totalTreeCoverage = ' + str(totalTreeCoverage)
    print 'characteristicLength = ' + str(characteristicLength) + ' meters'
    
    
    return checkData, _buildingTypologies, _buildingBreps, typologyRatios, roofAngles, wallAngles, averageBuildingHeight, siteCoverageRatio, totalGrassCoverage, totalTreeCoverage, vegetationParString, pavementConstrString, nonBldgAnthroHeat, nonBldgLatentFract, characteristicLength


def main(buildingTypologies, buildingBreps, typologyRatios, roofAngles, wallAngles, averageBuildingHeight, siteCoverageRatio, totalGrassCoverage, totalTreeCoverage, vegetationParString, pavementConstrString, nonBldgAnthroHeat, nonBldgLatentFract, characteristicLength):
    #Solve adjacencies between the building breps so that we don't have redundant facade surfaces.
    
    
    #Compute the facade to site ratio.
    
    
    #Create the urban area string
    
    
    #Swap out the portions of the building typologies that we have caulculated (like fraction of each in the urban area and roof angle).
    
    
    #Combine everything into one string.
    
    
    return None



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
    checkData, buildingTypologies, buildingBreps, typologyRatios, roofAngles, wallAngles, averageBuildingHeight, siteCoverageRatio, totalGrassCoverage, totalTreeCoverage, vegetationParString, pavementConstrString, nonBldgAnthroHeat, nonBldgLatentFract, characteristicLength = checkTheInputs(df_textGen, df_UWGGeo)
    if checkData == True:
        UWGParameters = main(buildingTypologies, buildingBreps, typologyRatios, roofAngles, wallAngles, averageBuildingHeight, siteCoverageRatio, totalGrassCoverage, totalTreeCoverage, vegetationParString, pavementConstrString, nonBldgAnthroHeat, nonBldgLatentFract, characteristicLength)

