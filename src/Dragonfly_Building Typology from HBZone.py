# UWG Building Typlogy from HBZone
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
Use this component to generate a building typology using a HBZone that represents a single floor of the entire building.  The resulting typology can be plugged into the "Dragonfly_UWG Parameters from Typologies" component.
-
Provided by Dragonfly 0.0.01
    Args:
        _HBZones: A HBZone that represents a single floor of the whole building typology that you hope to create.  While it is important that this zone represent a single typical floor for the building typology, the roof construction of this zone should be representative of the roof of the whole building (not an interior ceilings).  The floor of the zone represents the interior floor construction.
        roofVegFraction_: A number between 0 and 1 that represents the fraction of the building's roof that is covered in vegetation, such as green roof, grassy lawn, etc. If no value is input here, it will be assumed that the roof has no vegetation.
        wallVegFraction_: A number between 0 and 1 that represents the fraction of the building's walls that is covered in vegetation, such as green wall, vine-covered wall, etc. If no value is input here, it will be assumed that the roof has no vegetation.
        coolingCOP_: A number representing the mechanical cooling system coefficient of performance (COP), as defined as the ratio of the heat removed from a building over the electrical energy used by the building cooling system.  If no value is input here, a typical value of 3.7 will be used.
        heatingCOP_: A number representing the effectiveness of the building heating system at transforming the fuel energy (either electricity or burned fuel) into building heat energy. If no value is input here, a typical value of 0.8 will be used, representative of a typical gas furnace.
        coolingSystemType_: Set to 'True' to have the building modeled with an air-based cooling system and set to 'False' to have the building modeled with a water-based system.  The default is set to 'True' to model the building with an air-based system.
        heatFract2Canyon_: A number between 0 an 1 that represents the fraction of the waste heat from the mechanical cooling system that is exhausted into the urban canyon as opposed to being release above your neighborhood boundary layer.  If no value is input here, a default of 0.5 will be used, assuming that half of the cooling system's waste heat is rejected to the canyon in the fashion that window AC units would.  Set to 0 to assume that all waste heat is exhausted through the roof.
    Returns:
        buildingTypology: A building typology that can be plugged into the "Dragonfly_UWG Parameters from Typologies" component.
"""

ghenv.Component.Name = "Dragonfly_Building Typology from HBZone"
ghenv.Component.NickName = 'BldgTypologyFromZone'
ghenv.Component.Message = 'VER 0.0.01\nSEP_13_2017'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "2 | GenerateUrbanClimate"
#compatibleLBVersion = VER 0.0.59\nFEB_01_2015
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


import scriptcontext as sc
import Rhino as rc
import os

from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh


def setDefaultInputs():
    #Set a default roofVegFract.
    checkData1 = True
    if roofVegFraction_:
        if roofVegFraction_ >= 0 and roofVegFraction_ <= 1: roofVegFract = roofVegFraction_
        else:
            checkData1 = False
            warning = "roofVegFraction_ must be a value between 0 and 1."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else: roofVegFract = 0
    
    #Set a default wallVegFract.
    checkData2 = True
    if wallVegFraction_:
        if wallVegFraction_ >= 0 and wallVegFraction_ <= 1: wallVegFract = wallVegFraction_
        else:
            checkData2 = False
            warning = "wallVegFraction_ must be a value between 0 and 1."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else: wallVegFract = 0
    
    #Set a default heatFract2Canyon.
    checkData3 = True
    if heatFract2Canyon_:
        if heatFract2Canyon_ >= 0 and heatFract2Canyon_ <= 1: heatFract2Canyon = heatFract2Canyon_
        else:
            checkData3 = False
            warning = "heatFract2Canyon_ must be a value between 0 and 1."
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else: heatFract2Canyon = 0.5
    
    #Set a default cooling/heating system parameters.
    if coolingCOP_: coolingCOP = coolingCOP_
    else: coolingCOP = 3.7
    if heatingCOP_: heatingCOP = heatingCOP_
    else: heatingCOP = 0.8
    if coolingSystemType_: coolingSystemType = coolingSystemType_
    else: coolingSystemType = True
    
    
    #Do a final check of everything.
    checkData = False
    if checkData1 == True and checkData2 == True and checkData3 == True:
        checkData = True
    
    
    return checkData, roofVegFract, wallVegFract, coolingCOP, heatingCOP, coolingSystemType, heatFract2Canyon


def copyHBZoneData(hb_hive, lb_preparation):
    #Define a dictoinary to hold all of the zone information.
    zoneInfoDict = {
        
    #Overall zone proerties.
    'zoneName': None,
    'flr2FlrHeight' : None,
    'glzRatio' : None,
    'isConditioned' : None,
    'coolingCapacity' : None,
    
    #Internal gains (in W/m2)
    'equipSched' : [],
    'lightSched' : [],
    'pplSched' : [],
    
    #Ventilation and Infiltration (in ACH)
    'infilSched' : [],
    'ventilSched' : [],
    
    #Setpoints
    'heatSetPtSched' : [],
    'coolSetPtSched' : [],
    
    #Building Construction Information.
    'zoneWallsAreas' : [],
    'zoneRoofsAreas' : [],
    'zoneFloorAreas' : [],
    'zoneGlzSrfsAreas' : [],
    'zoneWallCnstr' : [],
    'zoneRoofCnstr' : [],
    'zoneFloorCnstr' : [],
    'zoneGlzSrfCnstr' : []
    }
    
    #Try to pull all of the properties of of the zone and add if to the disctionary.
    try:
        #Call the zone from the hive.
        zone = hb_hive.callFromHoneybeeHive([_HBZone])[0]
        
        #Get some of the basic proerties of the zone that will be used in the other calculations.
        flrArea = zone.getFloorArea()
        zoneVolume = zone.getZoneVolume()
        zoneGeometry = zone.geometry
        zoneGeoBoundBox = rc.Geometry.Brep.GetBoundingBox(zoneGeometry, rc.Geometry.Plane.WorldXY)
        flrHeight = zoneGeoBoundBox.Max.Z - zoneGeoBoundBox.Min.Z
        
        # Add the overall zone proerties to the dictionary.
        zoneInfoDict['zoneName'] = zone.name
        zoneInfoDict['flr2FlrHeight'] = flrHeight
        zoneInfoDict['isConditioned'] = zone.isConditioned
        try:
            zoneInfoDict['coolingCapacity'] = (float(zone.coolingCapacity)*1000)/flrArea
        except: zoneInfoDict['coolingCapacity'] = 205
        
        #Extract the info for the zone's internal gains.
        if not zone.isLoadsAssigned: zone.assignLoadsBasedOnProgram(ghenv.Component)
        zoneInfoDict['equipSched'] = computeHourlySchedVals(zone.equipmentLoadPerArea, zone.equipmentSchedule, lb_preparation)
        zoneInfoDict['lightSched'] = computeHourlySchedVals(zone.lightingDensityPerArea, zone.lightingSchedule, lb_preparation)
        occSched = computeHourlySchedVals(zone.numOfPeoplePerArea, zone.occupancySchedule, lb_preparation)
        activSched = computeHourlySchedVals(1, zone.occupancyActivitySch, lb_preparation)
        for count, occ in enumerate(occSched):
            zoneInfoDict['pplSched'].append(occ*activSched[count])
        
        #Extract the info for the zone's infiltration and ventilation.
        zoneInfoDict['infilSched'] = computeHourlySchedVals((zone.infiltrationRatePerArea*flrArea*3600)/zoneVolume, zone.infiltrationSchedule, lb_preparation)
        ventPerPerson = []
        for occ in occSched: ventPerPerson.append(occ*zone.ventilationPerPerson)
        if zone.outdoorAirReq == "Sum":
            for val in ventPerPerson: zoneInfoDict['ventilSched'].append(((val+zone.ventilationPerArea)*flrArea*3600)/zoneVolume)
        elif zone.outdoorAirReq == "Maximum":
            for val in ventPerPerson:
                if val > zone.ventilationPerArea: zoneInfoDict['ventilSched'].append((val*flrArea*3600)/zoneVolume)
                else: zoneInfoDict['ventilSched'].append((zone.ventilationPerArea*flrArea*3600)/zoneVolume)
        else:
            for val in ventPerPerson: zoneInfoDict['ventilSched'].append(0)
        
        #Extract the info for the zone's setpoints.
        if zone.isConditioned:
            zoneInfoDict['heatSetPtSched'] = computeHourlySchedVals(1, zone.heatingSetPtSchedule, lb_preparation)
            zoneInfoDict['coolSetPtSched'] = computeHourlySchedVals(1, zone.coolingSetPtSchedule, lb_preparation)
        else:
            for val in occSched: zoneInfoDict['heatSetPtSched'].append(-50)
            for val in occSched: zoneInfoDict['coolSetPtSched'].append(50)
        
        
        #Write a function to automate the creation of lists for zone surfaces.
        def abstractSrfToDict(srf, constrList, areaList, surfCnstr):
            srfArea = rc.Geometry.AreaMassProperties.Compute(srf.geometry).Area
            if surfCnstr in zoneInfoDict[constrList]:
                for count, constr in enumerate(zoneInfoDict[constrList]):
                    if constr == surfCnstr: zoneInfoDict[areaList][count] += srfArea
            else:
                zoneInfoDict[constrList].append(surfCnstr)
                zoneInfoDict[areaList].append(srfArea)
        
        
        #Extract all of the info in the zone's surfaces.
        for srf in zone.surfaces:
            srfCnstr = srf.EPConstruction
            if str(srf.type) == '0':
                abstractSrfToDict(srf, 'zoneWallCnstr', 'zoneWallsAreas', srfCnstr)
                if srf.hasChild:
                    for childSrf in srf.childSrfs: abstractSrfToDict(childSrf, 'zoneGlzSrfCnstr', 'zoneGlzSrfsAreas', childSrf.EPConstruction)
            if str(srf.type) == '1':
                abstractSrfToDict(srf, 'zoneRoofCnstr', 'zoneRoofsAreas', srfCnstr)
                if srf.hasChild:
                    for childSrf in srf.childSrfs: abstractSrfToDict(childSrf, 'zoneGlzSrfCnstr', 'zoneGlzSrfsAreas', childSrf.EPConstruction)
            if str(srf.type).startswith('2'):
                abstractSrfToDict(srf, 'zoneFloorCnstr', 'zoneFloorAreas', srfCnstr)
        
        #Make sure that we have gotten at least one construction for each of the critical surface types.
        missingWarnings = []
        if len(zoneInfoDict['zoneWallCnstr']) == 0: missingWarnings.append('Your connected _HBZone does not have any above-ground wall surfaces. \n The zone must have at least one wall surface to be represented in the UWG.')
        if len(zoneInfoDict['zoneRoofCnstr']) == 0: missingWarnings.append('Your connected _HBZone does not have any above-ground roof surfaces. \n The zone must have at least one roof surface to be represented in the UWG.')
        if len(zoneInfoDict['zoneFloorCnstr']) == 0: missingWarnings.append('Your connected _HBZone does not have any floor surfaces. \n The zone must have at least one floor surface to be represented in the UWG.')
        if len(missingWarnings) != 0:
            for warning in missingWarnings:
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            return -1
        if len(zoneInfoDict['zoneGlzSrfsAreas']) == 0:
            zoneInfoDict['zoneGlzSrfCnstr'].append(None)
            zoneInfoDict['zoneGlzSrfsAreas'].append(0)
        
        #Compute the galzing window-to-wall ratio of the zone from the areas that have been collected.
        zoneInfoDict['glzRatio'] = sum(zoneInfoDict['zoneGlzSrfsAreas'])/sum(zoneInfoDict['zoneWallsAreas'])
        if zoneInfoDict['glzRatio'] > 1: zoneInfoDict['glzRatio'] = 1
        
        return zoneInfoDict
    except:
        warning = "The geometry that you have connected to _HBZone is not a valid Honeybee Zone created with Honeybee components."
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        return -1


def computeHourlySchedVals(load, schName, lb_preparation):
    #Make a list to be filled and call the class.
    hourlyVals = []
    readSchedules = sc.sticky["honeybee_ReadSchedules"](schName, None)
    
    #Get the schedule fractional values.
    values = []
    if schName.lower().endswith(".csv"):
        # check if csv file exists
        if not os.path.isfile(schName):
            msg = "Cannot find the shchedule file: " + schName
            print msg
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        else:
            result = open(schName, 'r')
            for lineCount, line in enumerate(result):
                readSchedules.schType = 'schedule:year'
                readSchedules.startHOY = 1
                readSchedules.endHOY = 8760
                if lineCount == 0: readSchedules.unit = line.split(',')[-2].split(' ')[-1].upper()
                elif lineCount == 1: readSchedules.schName = line.split('; ')[-1].split(':')[0]
                elif lineCount < 4: pass
                else:
                    for columnCount, column in enumerate(line.split(',')):
                        if columnCount == 4:
                            values.append(float(column))
    else:
        HBScheduleList = sc.sticky["honeybee_ScheduleLib"].keys()
        if schName.upper() not in HBScheduleList:
            msg = "Cannot find " + schName + " in Honeybee schedule library."
            print msg
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        else:
            values  = readSchedules.getScheduleValues()
    
    #Flatten the list if it needs to be flattened.
    try: values = lb_preparation.flattenList(values)
    except: pass
    
    #Multiply the schedule values by the load.
    for val in values:
        hourlyVals.append(val*load)
    
    return hourlyVals



def main(HBZoneDict, roofVegFract, wallVegFract, coolingCOP, heatingCOP, coolingSystemType, heatFract2Canyon, df_textGen):
    #Define the building typolgy string.
    typologyString = '  <typology1 dist="TBDPercent" name="' + HBZoneDict['zoneName'] + '">\n'
    typologyString = typologyString + '    <dist>TBDPercent</dist>\n'
    
    #Have a function to deal with the case where there are multiple constructions assigned to a given surface type.  In this case, we should just take the construction with the most surface area to define the typology.
    def giveConstructionWarning(constructionList, areaList, surfaceType):
        areaListSort, constructionListSort = zip(*sorted(zip(areaList, constructionList)))
        msg = "You have more than one type of construction assigned to your HBZone's " + surfaceType + ". \n At the moment, the UWG only supports one material per surface type. \n The construction that takes up the most surface area of the " + surfaceType + " has been selected: \n" + constructionListSort[-1]
        print msg
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
        return constructionListSort[-1]
    
    #Pull the starting temperature from the setpoint schedule.
    if HBZoneDict['heatSetPtSched'][0] > -20: startTemp = HBZoneDict['heatSetPtSched'][0]
    else: startTemp = 'setByEPW'
    
    
    #Generate the text strings for the building constructions
    typologyString = typologyString + '    <construction>\n'
    
    if len(HBZoneDict['zoneWallCnstr']) != 1: wallConstr = giveConstructionWarning(HBZoneDict['zoneWallCnstr'], HBZoneDict['zoneWallsAreas'], 'walls')
    else: wallConstr = HBZoneDict['zoneWallCnstr'][0]
    wallCnstrString = df_textGen.createXMLFromEPConstr(wallConstr, 'wall', wallVegFract, startTemp)
    typologyString = typologyString + wallCnstrString
    
    if len(HBZoneDict['zoneRoofCnstr']) != 1: roofConstr = giveConstructionWarning(HBZoneDict['zoneRoofCnstr'], HBZoneDict['zoneFloorAreas'], 'walls')
    else: roofConstr = HBZoneDict['zoneRoofCnstr'][0]
    roofCnstrString = df_textGen.createXMLFromEPConstr(roofConstr, 'roof', roofVegFract, startTemp)
    typologyString = typologyString + roofCnstrString
    
    if len(HBZoneDict['zoneFloorCnstr']) != 1: massConstr = giveConstructionWarning(HBZoneDict['zoneFloorCnstr'], HBZoneDict['zoneFloorAreas'], 'walls')
    else: massConstr = HBZoneDict['zoneFloorCnstr'][0]
    massCnstrString = df_textGen.createXMLFromEPConstr(massConstr, 'mass', 0, startTemp)
    typologyString = typologyString + massCnstrString
    
    glzCnstrString = df_textGen.createXMLFromEPWindow(HBZoneDict['glzRatio'], HBZoneDict['zoneGlzSrfCnstr'], HBZoneDict['zoneGlzSrfsAreas'])
    typologyString = typologyString + glzCnstrString
    
    typologyString = typologyString + '    </construction>\n'
    
    
    #Start generateing the text strings for the building.
    buildingString = '    <building name="' + HBZoneDict['zoneName'] + 'Building">\n'
    buildingString = buildingString + '      <floorHeight>' + str(HBZoneDict['flr2FlrHeight']) + '</floorHeight>\n'
    
    #From the internal loads and schedules, compute total daytime / nighttime internal gains, as well as a radiant/latent fraction.
    intGainString = df_textGen.constructIntGainString(HBZoneDict['equipSched'], HBZoneDict['lightSched'], HBZoneDict['pplSched'])
    buildingString = buildingString + intGainString
    
    #From the ventilation and infiltration lods/schedules, compute the values to plug into the XML.
    buildingString = buildingString + '      <infiltration>' + str(sum(HBZoneDict['infilSched'])/len(HBZoneDict['infilSched'])) + '</infiltration>\n'
    buildingString = buildingString + '      <ventilation>' + str(sum(HBZoneDict['ventilSched'])/len(HBZoneDict['ventilSched'])) + '</ventilation>\n'
    
    #Write in the building heating/cooling system parameters.
    if coolingSystemType == True: buildingString = buildingString + '      <coolingSystemType>air</coolingSystemType>\n'
    else: buildingString = buildingString + '      <coolingSystemType>water</coolingSystemType>\n'
    buildingString = buildingString + '      <coolingCOP>' + str(coolingCOP) + '</coolingCOP>\n'
    setPtString = df_textGen.constructSetPtString(HBZoneDict['coolSetPtSched'], HBZoneDict['heatSetPtSched'])
    buildingString = buildingString + setPtString
    buildingString = buildingString + '      <coolingCapacity>' + str(HBZoneDict['coolingCapacity']) + '</coolingCapacity>\n'
    buildingString = buildingString + '      <heatingEfficiency>' + str(heatingCOP) + '</heatingEfficiency>\n'
    buildingString = buildingString + '      <nightSetStart>20</nightSetStart>\n'
    buildingString = buildingString + '      <nightSetEnd>8</nightSetEnd>\n'
    buildingString = buildingString + '      <heatReleasedToCanyon>' + str(heatFract2Canyon) + '</heatReleasedToCanyon>\n'
    buildingString = buildingString + '      <initialT>' + str(startTemp) + '</initialT>\n'
    buildingString = buildingString + '    </building>\n'
    
    #Add in the building text to the whole typology string.
    typologyString = typologyString + buildingString 
    
    
    #Conclude the building typology.
    typologyString = typologyString + '  </typology1>\n'
    
    
    return typologyString




#Check to be sure that Honeybee, Ladybug and Dragonfly are flying.
initCheck = False
hb_hive = None
if sc.sticky.has_key('honeybee_release') and sc.sticky.has_key("ladybug_release") and sc.sticky.has_key("dragonfly_release"):
    hb_hive = sc.sticky["honeybee_Hive"]()
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    df_textGen = sc.sticky["dragonfly_UWGText"]()
    initCheck = True
else:
    if not sc.sticky.has_key("honeybee_release"):
        warning = "You need to let Honeybee  fly to use this component."
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    if not sc.sticky.has_key("ladybug_release"):
        warning = "You need to let Ladybug fly to use this component."
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    if not sc.sticky.has_key("dragonfly_release"):
        warning = "You need to let Dragonfly fly to use this component."
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)


#Get the properties of the HBZone and write them into a format for the UWG XML.
if _HBZone and initCheck == True:
    checkData, roofVegFract, wallVegFract, coolingCOP, heatingCOP, coolingSystemType, heatFract2Canyon = setDefaultInputs()
    if checkData == True:
        HBZoneDict = copyHBZoneData(hb_hive, lb_preparation)
        if HBZoneDict != -1:
            buildingTypology = main(HBZoneDict, roofVegFract, wallVegFract, coolingCOP, heatingCOP, coolingSystemType, heatFract2Canyon, df_textGen)

