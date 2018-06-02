# Dragonfly: A Plugin for Climate Modeling (GPL) started by Chris Mackey <chris@ladybug.tools> 
# This file is part of Dragonfly.
#
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Use this component to morph a rural or airport EPW to reflect the conditions within an urban street canyon.  The properties of this urban street canyon are specified in the connected _UWGCity.
_
For definitions of the inputs of the Urban Weather Generator, please see this page of the MIT Urban Microclimate Group:
http://urbanmicroclimate.scripts.mit.edu/uwg_parameters.php#ref
_
For a full list of publications on the Urban Weather Generator, please see this page of the MIT Urban Microclimate Group:
http://urbanmicroclimate.scripts.mit.edu/publications.php
-
Provided by Dragonfly 0.0.02
    Args:
        _epwFile: An .epw file path on your system.  This is the rural or airport file that will be morphed to reflect the climate conditions within an urban canyon.
        _DFCity: A Dragonfly City object. This object can be generated with the "Dragonfly_City" component.
        epwSitePar_: Optional Reference EPW Site Parameters from the "Dragonfly_Reference EPW Site Par" component.
        bndLayerPar_: Optional Boundary Layer Parameters from the "Dragonfly_Boundary Layer Par" component.
        _analysisPeriod_: An optional analysis period from the 'Ladybug_Analysis Period' component.  If no Analysis period is given, the Urban Weather Generator will be run for the enitre year.
        _simTimestep_: A number representing the timestep at which the simulation is run in seconds.  The default is set to 300 seconds (5 minutes).  Note that all restuls are still reported on an hour-by-hour basis in the otuput EPW and this input only changes how the calculation is run in the UWG.
        _folder_: An optional working directory to a folder on your system, into which the morphed EPW files will be written.  The default will write these files in the folder that contains the connected _epwFile.
        _name_: An optional text string which will be used to name of your morphed EPW files.  Change this to aviod over-writing results of previous runs of the Urban Weather Generator.
        _write: Set to "True" to have the component generate a UWG object from the connected DFCity and parameters. This object can be edited and smulated using a python component.
        run_: Set to "True" to simulate the uwgObject and morph the EPW using the Urban Weather Generator (UWG).
    Returns:
        readMe!: ...
        ---------------: ...
        urbanEpw: The file path of the morphed EPW file that has been generated on your machine.
        ---------------: ...
        uwgObject: The python UWG object that can be edited and simulated using the methods on the UWG.
"""

ghenv.Component.Name = "Dragonfly_Run Urban Weather Generator"
ghenv.Component.NickName = 'RunUWG'
ghenv.Component.Message = 'VER 0.0.02\nJUN_03_2018'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "00::UWG"
#compatibleDFVersion = VER 0.0.02\nMAY_25_2018
ghenv.Component.AdditionalHelpFromDocStrings = "1"


import scriptcontext as sc
import Grasshopper.Kernel as gh
import os

try:
    from UWG import UWG
except ImportError as e:
    raise ImportError('\nFailed to import the UWG:\n\t{}'.format(e))

def create_uwg(epwFile, endFolder, name):
    startFolder, epwName = os.path.split(epwFile)
    epwName = epwName.replace('.epw', '')
    if endFolder is None:
        endFolder = startFolder
    if name is None:
        name = epwName + '_URBAN.epw'
    return UWG(epwName, None, startFolder, None, endFolder, name), endFolder + '\\' + name

def parse_ladybug_analysis_period(analysisPeriod):
    if analysisPeriod is not None:
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        stMonth, stDay, stHour, endMonth, endDay, endHour = lb_preparation.readRunPeriod(analysisPeriod)
        startDOY = int(lb_preparation.getJD(stMonth, stDay))
        endDOY = int(lb_preparation.getJD(endMonth, endDay))
        simDuration = endDOY - startDOY + 1
        return stMonth, stDay, simDuration
    else:
        return 1, 1, 365

def autocalcStartEndVegetation(epwFile):
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    locationData = lb_preparation.epwLocation(epwFile)
    temperatureData = lb_preparation.epwDataReader(epwFile, locationData[0])[0][7:]
    
    monthDays = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    monthTemps = []
    for month in range(1, 13):
        stJD = lb_preparation.getJD(month, 1)
        endJD = lb_preparation.getJD(month, monthDays[month])
        monthlyData = temperatureData[lb_preparation.getHour(stJD, 1)-1 : lb_preparation.getHour(endJD , 24)]
        monthTemps.append(sum(monthlyData)/len(monthlyData))
    
    thresholdTemp = 10
    vegEnd = 12
    vegStartSet = False
    for i, t in enumerate(monthTemps):
        if t > thresholdTemp and vegStartSet == False:
            vegStart = i+1
            vegStartSet = True
        elif t < thresholdTemp and vegStartSet == True:
            vegEnd = i+1
            vegStartSet = False
    
    return vegStart, vegEnd

def set_uwg_input(uwg, DFCity, epwSitePar, bndLayerPar, analysisPeriod, simTimestep):
        """Assign all inputs to the UWG """
        
        # Define Simulation and Weather parameters
        month, day, nDay = parse_ladybug_analysis_period(analysisPeriod)
        uwg.Month = month
        uwg.Day = day
        uwg.nDay = nDay
        if simTimestep is not None:
            uwg.dtSim = simTimestep
        else:
            uwg.dtSim = 300
        uwg.dtWeather = 3600
        
        # HVAC system and internal laod
        uwg.autosize = 0
        uwg.sensOcc = 100
        uwg.LatFOcc = 0.3
        uwg.RadFOcc = 0.2
        uwg.RadFEquip = 0.5
        uwg.RadFLight = 0.7
        
        # Define Urban microclimate parameters
        uwg.h_ubl1 = bndLayerPar.day_boundary_layer_height
        uwg.h_ubl2 = bndLayerPar.night_boundary_layer_height
        uwg.h_ref = bndLayerPar.inversion_height
        uwg.c_circ = bndLayerPar.circulation_coefficient
        uwg.c_exch = bndLayerPar.exchange_coefficient
        uwg.h_temp = epwSitePar.temp_measure_height
        uwg.h_wind = epwSitePar.wind_measure_height
        uwg.maxDay = 150
        uwg.maxNight = 20
        uwg.windMin = 1
        uwg.h_obs = epwSitePar.average_obstacle_height
        
        # Urban characteristics
        uwg.bldHeight = DFCity.average_bldg_height
        uwg.h_mix = DFCity.fract_heat_to_canyon
        uwg.bldDensity = DFCity.site_coverage_ratio
        uwg.verToHor = DFCity.facade_to_site_ratio
        uwg.charLength = DFCity.characteristic_length
        uwg.sensAnth = DFCity.traffic_parameters.sensible_heat
        uwg.SchTraffic = DFCity.traffic_parameters.get_uwg_matrix()
        
        # Define optional Building characteristics
        uwg.bld = DFCity.get_uwg_matrix()
        
        # climate Zone
        uwg.zone = DFCity._climate_zone
        
        # Vegetation parameters
        uwg.vegCover = DFCity.grass_coverage_ratio
        uwg.treeCoverage = DFCity.tree_coverage_ratio
        uwg.albVeg = DFCity.vegetation_parameters.vegetation_albedo
        uwg.rurVegCover = epwSitePar.vegetation_coverage
        
        if DFCity.vegetation_parameters.vegetation_start_month == 0 or DFCity.vegetation_parameters.vegetation_end_month == 0:
            vegStart, vegEnd = autocalcStartEndVegetation(_epwFile)
        if DFCity.vegetation_parameters.vegetation_start_month == 0:
            uwg.vegStart = vegStart
        else:
            uwg.vegStart = DFCity.vegetation_parameters.vegetation_start_month
        if DFCity.vegetation_parameters.vegetation_start_month == 0:
            uwg.vegEnd = vegEnd
        else:
            uwg.vegEnd = DFCity.vegetation_parameters.vegetation_end_month
        
        # Define road
        uwg.alb_road = DFCity.pavement_parameters.albedo
        uwg.d_road = DFCity.pavement_parameters.thickness
        uwg.kRoad = DFCity.pavement_parameters.conductivity
        uwg.cRoad = DFCity.pavement_parameters.volumetric_heat_capacity
        
        # parameters that will be added in
        uwg.r_glaze = DFCity.glz_ratio
        uwg.SHGC = DFCity.shgc
        uwg.alb_wall = DFCity.wall_albedo
        uwg.h_floor = DFCity.floor_height
        
        # parameters that are not being used that are going away
        uwg.latAnth = 0
        uwg.latGrss = 0
        uwg.latTree = 0
        
        return uwg


# dragonfly check.
initCheck = True
if not sc.sticky.has_key('dragonfly_release') == True:
    initCheck = False
    print "You should first let Drafgonfly fly..."
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "You should first let Drafgonfly fly...")
else:
    if not sc.sticky['dragonfly_release'].isCompatible(ghenv.Component): initCheck = False
    if sc.sticky['dragonfly_release'].isInputMissing(ghenv.Component): initCheck = False
    df_RefEPWSitePar = sc.sticky["dragonfly_RefEpwPar"]
    df_BndLayerPar = sc.sticky["dragonfly_BoundaryLayerPar"]
    uwg_path = sc.sticky["dragonfly_UWGPath"]

# ladybug check
if not sc.sticky.has_key("ladybug_release") == True:
    initCheck = False
    warning = "You need to let Ladybug fly to use this component."
    print warning
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)


if initCheck == True and _write == True:
    # check the epwSitePar and assign default if None.
    if epwSitePar_ is not None:
        assert (hasattr(epwSitePar_, 'isRefEPWSitePar')), 'epwSitePar_ must be a Dragonfly RefEPWSitePar object. Got {}'.format(type(epwSitePar_))
        epwSitePar = epwSitePar_
    else:
        epwSitePar = df_RefEPWSitePar()
    
    # check the bndLayerPar and assign default if None.
    if bndLayerPar_ is not None:
        assert (hasattr(bndLayerPar_, 'isBoundaryLayerPar')), 'bndLayerPar_ must be a Dragonfly BoundaryLayerPar object. Got {}'.format(type(bndLayerPar_))
        bndLayerPar = bndLayerPar_
    else:
        bndLayerPar = df_BndLayerPar()
    
    # check the DFcity object.
    assert (hasattr(_DFCity, 'isDFCity')), '_DFCity must be a Dragonfly City object. Got {}'.format(type(_DFCity))
    
    # create a uwgObject from the dragonfly objects.
    uwgObject, newEpwPath = create_uwg(_epwFile, _folder_, _name_)
    uwgObject.RESOURCE_PATH = uwg_path
    uwgObject = set_uwg_input(uwgObject, _DFCity, epwSitePar, bndLayerPar, _analysisPeriod_, _simTimestep_)
    uwgObject.read_epw()
    uwgObject.instantiate_input()
    uwgObject.hvac_autosize()
    
    # run the UWG object if run is set to True.
    if run_ == True:
        uwgObject.simulate()
        uwgObject.write_epw()
        urbanEpw = newEpwPath
