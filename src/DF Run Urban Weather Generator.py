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
Provided by Dragonfly 0.0.03
    Args:
        _epw_file: An .epw file path on your system.  This is the rural or airport file that will be morphed to reflect the climate conditions within an urban canyon.
        _city: A Dragonfly City object. This object can be generated with the "DF City" component.
        epw_site_par_: Optional Reference EPW Site Parameters from the "DF Reference EPW Site Par" component.
        bnd_layer_par_: Optional Boundary Layer Parameters from the "DF Boundary Layer Par" component.
        _analysis_period_: An optional analysis period from the 'Ladybug_Analysis Period' component.  If no Analysis period is given, the Urban Weather Generator will be run for the enitre year.
        _sim_timestep_: A number representing the timestep at which the simulation is run in seconds.  The default is set to 300 seconds (5 minutes).
        _folder_: An optional working directory to a folder on your system, into which the morphed EPW files will be written.  The default will write these files in the folder that contains the connected _epw_file.
        _name_: An optional text string which will be used to name of your morphed EPW files.  Change this to aviod over-writing results of previous runs of the Urban Weather Generator.
        _write: Set to "True" to have the component generate a UWG object from the connected DFCity and parameters. This object can be edited and smulated using a python component.
        run_: Set to "True" to simulate the uwg_object and morph the EPW using the Urban Weather Generator (UWG).
    Returns:
        readMe!: ...
        ---------------: ...
        urban_epw: The file path of the morphed EPW file that has been generated on your machine.
        ---------------: ...
        uwg_object: The python UWG object that can be edited and simulated using the methods on the UWG.
"""

ghenv.Component.Name = "DF Run Urban Weather Generator"
ghenv.Component.NickName = 'RunUWG'
ghenv.Component.Message = 'VER 0.0.03\nMAR_25_2020'
ghenv.Component.Category = "DF-Legacy"
ghenv.Component.SubCategory = "1 | Urban Weather"
#compatibleDFVersion = VER 0.0.02\nMAY_25_2018
ghenv.Component.AdditionalHelpFromDocStrings = "1"


import scriptcontext as sc
import Grasshopper.Kernel as gh
import os
import itertools

try:
    from uwg import uwg
except ImportError as e:
    raise ImportError('\nFailed to import the uwg:\n\t{}'.format(e))

def create_uwg(epw_file, end_folder, name):
    start_folder, epw_name = os.path.split(epw_file)
    epw_name = epw_name.replace('.epw', '')
    if end_folder is None:
        end_folder = start_folder + '\\URBAN\\'
    if name is None:
        name = epw_name + '_URBAN.epw'
    if not os.path.isdir(end_folder):
        os.mkdir(end_folder)
    return uwg(epw_name, None, start_folder, None, end_folder, name), end_folder + '\\' + name

def parse_ladybug_analysis_period(analysis_period):
    if analysis_period is not None:
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        st_month, st_day, st_hour, end_month, end_day, end_hour = lb_preparation.readRunPeriod(analysis_period)
        start_doy = int(lb_preparation.getJD(st_month, st_day))
        end_doy = int(lb_preparation.getJD(end_month, end_day))
        simDuration = end_doy - start_doy + 1
        return st_month, st_day, simDuration
    else:
        return 1, 1, 365

def autocalcStartEndVegetation(epw_file):
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    locationData = lb_preparation.epwLocation(epw_file)
    temperatureData = lb_preparation.epwDataReader(epw_file, locationData[0])[0][7:]
    
    monthDays = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    monthTemps = []
    for month in range(1, 13):
        stJD = lb_preparation.getJD(month, 1)
        endJD = lb_preparation.getJD(month, monthDays[month])
        monthlyData = temperatureData[lb_preparation.getHour(stJD, 1)-1 : lb_preparation.getHour(endJD , 24)]
        monthTemps.append(sum(monthlyData)/len(monthlyData))
    
    thresholdTemp = 10
    vegEnd = 12
    vegStart = 1
    vegStartSet = False
    for i, t in enumerate(monthTemps):
        if t > thresholdTemp and vegStartSet == False:
            vegStart = i+1
            vegStartSet = True
        elif t < thresholdTemp and vegStartSet == True:
            vegEnd = i+1
            vegStartSet = False
    
    return vegStart, vegEnd

def set_uwg_input(uwg, DFCity, epw_site_par, bnd_layer_par, analysis_period, simTimestep):
        """Assign all inputs to the uwg """
        
        # Define Simulation and Weather parameters
        month, day, nDay = parse_ladybug_analysis_period(analysis_period)
        uwg.Month = month
        uwg.Day = day
        uwg.nDay = nDay
        if simTimestep is not None:
            uwg.dtSim = simTimestep
        else:
            uwg.dtSim = 300.
        uwg.dtWeather = 3600.
        
        # HVAC system and internal laod
        uwg.autosize = 0
        uwg.sensOcc = 100.
        uwg.LatFOcc = 0.3
        uwg.RadFOcc = 0.2
        uwg.RadFEquip = 0.5
        uwg.RadFLight = 0.7
        
        # Define Urban microclimate parameters
        uwg.h_ubl1 = float(bnd_layer_par.day_boundary_layer_height)
        uwg.h_ubl2 = float(bnd_layer_par.night_boundary_layer_height)
        uwg.h_ref = float(bnd_layer_par.inversion_height)
        uwg.c_circ = bnd_layer_par.circulation_coefficient
        uwg.c_exch = bnd_layer_par.exchange_coefficient
        uwg.h_temp = float(epw_site_par.temp_measure_height)
        uwg.h_wind = float(epw_site_par.wind_measure_height)
        uwg.maxDay = 150.
        uwg.maxNight = 20.
        uwg.windMin = 1.
        uwg.h_obs = float(epw_site_par.average_obstacle_height)
        
        # Urban characteristics
        uwg.bldHeight = float(DFCity.average_bldg_height)
        uwg.h_mix = float(DFCity.fract_heat_to_canyon)
        uwg.bldDensity = float(DFCity.site_coverage_ratio)
        uwg.verToHor = float(DFCity.facade_to_site_ratio)
        uwg.charLength = float(DFCity.characteristic_length)
        uwg.sensAnth = float(DFCity.traffic_parameters.sensible_heat)
        uwg.SchTraffic = DFCity.traffic_parameters.get_uwg_matrix()
        
        # Define optional Building characteristics
        uwg.bld = DFCity.get_uwg_matrix()
        
        # climate Zone
        uwg.zone = DFCity._climate_zone
        
        # Vegetation parameters
        uwg.vegCover = float(DFCity.grass_coverage_ratio)
        uwg.treeCoverage = float(DFCity.tree_coverage_ratio)
        uwg.albVeg = float(DFCity.vegetation_parameters.vegetation_albedo)
        uwg.latTree = float(DFCity.vegetation_parameters.tree_latent_fraction)
        uwg.latGrss = float(DFCity.vegetation_parameters.grass_latent_fraction)
        uwg.rurVegCover = float(epw_site_par.vegetation_coverage)
        
        if DFCity.vegetation_parameters.vegetation_start_month == 0 or DFCity.vegetation_parameters.vegetation_end_month == 0:
            vegStart, vegEnd = autocalcStartEndVegetation(_epw_file)
        if DFCity.vegetation_parameters.vegetation_start_month == 0:
            uwg.vegStart = vegStart
        else:
            uwg.vegStart = DFCity.vegetation_parameters.vegetation_start_month
        if DFCity.vegetation_parameters.vegetation_end_month == 0:
            uwg.vegEnd = vegEnd
        else:
            uwg.vegEnd = DFCity.vegetation_parameters.vegetation_end_month
        
        # Define road
        uwg.alb_road = float(DFCity.pavement_parameters.albedo)
        uwg.d_road = float(DFCity.pavement_parameters.thickness)
        uwg.kRoad = float(DFCity.pavement_parameters.conductivity)
        uwg.cRoad = float(DFCity.pavement_parameters.volumetric_heat_capacity)
        
        return uwg

def set_individual_typologies(uwg, city):
    bldg_conversion = sc.sticky["dragonfly_UWGBldgTypes"]
    
    # create a dictonary to convert between the df_city and uwg typologies
    city_typologies = city.building_typologies
    city_typNames = [','.join([typ.bldg_program, typ.bldg_age]) for typ in city_typologies]
    typology_dict = dict(itertools.izip(city_typNames, city_typologies))
    
    # update each typology
    for uwg_typology in uwg.BEM:
        df_typology = typology_dict[','.join([bldg_conversion.uwg_bldg_type[uwg_typology.building.Type], bldg_conversion.uwg_built_era[uwg_typology.building.Era]])]
        uwg_typology.building.floorHeight = df_typology.floor_to_floor
        uwg_typology.building.canyon_fraction = df_typology.fract_heat_to_canyon
        uwg_typology.building.glazingRatio = df_typology.glz_ratio
        uwg_typology.building.shgc = df_typology.shgc
        uwg_typology.wall.albedo = df_typology.wall_albedo
        uwg_typology.roof.albedo = df_typology.roof_albedo
        uwg_typology.roof.vegCoverage = df_typology.roof_veg_fraction
    
    return uwg

def set_global_facade_props(uwg, DFCity):
    # parameters for the UCMdef that must be overwritten
    uwg.r_glaze_total = DFCity.glz_ratio
    uwg.SHGC_total = DFCity.shgc
    uwg.alb_wall_total = DFCity.wall_albedo
    
    # parameters that are already corrected on the set_individual_typologies that I am overwriting for visual reasons
    uwg.albRoof = DFCity.roof_albedo
    uwg.vegRoof = DFCity.roof_veg_fraction
    uwg.flr_h = DFCity.floor_height
    
    return uwg


# dragonfly check.
init_check = True
if not sc.sticky.has_key('dragonfly_release') == True:
    init_check = False
    print "You should first let Drafgonfly fly..."
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, "You should first let Drafgonfly fly...")
else:
    if not sc.sticky['dragonfly_release'].isCompatible(ghenv.Component): init_check = False
    if sc.sticky['dragonfly_release'].isInputMissing(ghenv.Component): init_check = False
    df_RefEPWSitePar = sc.sticky["dragonfly_RefEpwPar"]
    df_BndLayerPar = sc.sticky["dragonfly_BoundaryLayerPar"]
    uwg_path = sc.sticky["dragonfly_UWGPath"]

# ladybug check
if not sc.sticky.has_key("ladybug_release") == True:
    init_check = False
    warning = "You need to let Ladybug fly to use this component."
    print warning
    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)


if init_check == True and _write == True:
    # check the epw_site_par and assign default if None.
    if epw_site_par_ is not None:
        assert (hasattr(epw_site_par_, 'isRefEPWSitePar')), 'epw_site_par_ must be a Dragonfly RefEPWSitePar object. Got {}'.format(type(epw_site_par_))
        epw_site_par = epw_site_par_
    else:
        epw_site_par = df_RefEPWSitePar()
    
    # check the bnd_layer_par and assign default if None.
    if bnd_layer_par_ is not None:
        assert (hasattr(bnd_layer_par_, 'isBoundaryLayerPar')), 'bnd_layer_par_ must be a Dragonfly BoundaryLayerPar object. Got {}'.format(type(bnd_layer_par_))
        bnd_layer_par = bnd_layer_par_
    else:
        bnd_layer_par = df_BndLayerPar()
    
    # check the DFcity object.
    assert (hasattr(_city, 'isCity')), '_city must be a Dragonfly City object. Got {}'.format(type(_city))
    
    # create a uwg_object from the dragonfly objects.
    uwg_object, new_epw_path = create_uwg(_epw_file, _folder_, _name_)
    uwg_object = set_uwg_input(uwg_object, _city, epw_site_par, bnd_layer_par, _analysis_period_, _sim_timestep_)
    uwg_object.check_required_inputs()
    uwg_object.init_BEM_obj()
    uwg_object = set_individual_typologies(uwg_object, _city)
    uwg_object = set_global_facade_props(uwg_object, _city)
    
    # get the object ready to simulate
    uwg_object.read_epw()
    uwg_object.init_input_obj()
    uwg_object.hvac_autosize()
    
    # run the UWG object if run is set to True.
    if run_ == True:
        uwg_object.simulate()
        uwg_object.write_epw()
        urban_epw = new_epw_path
