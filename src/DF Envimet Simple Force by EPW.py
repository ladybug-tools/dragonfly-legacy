# Dragonfly: A Plugin for Climate Modeling (GPL) started by Chris Mackey <chris@ladybug.tools>, Antonello Di Nunzio <antonellodinunzio@gmail.com> 
# This file is part of Dragonfly.
#
# You should have received a copy of the GNU General Public License
# along with Dragonfly; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
This component let you force climate condition of the simulation. Data of this component comes from EPW file.
Basically, it extract 24 values of temperature and relative humidity by using DOY.
-
It is a good element to find a relation between calculation with EnergyPlus and calculation with ENVI_MET.
-
Connect "simpleForce" to ...
-
Provided by Dragonfly 0.0.03
    
    Args:
        _epwFile:  An .epw file path on your system as a string.
        _DOY: The day of the year. Connect the output from "Ladybug_DOY_HOY".
        _HOY: The hour of the year. Connect the output from "Ladybug_DOY_HOY".
    Returns:
        readMe!: ...
        dryBulbTemperature: The dry bulb temperature values [K] from selected day.
        relativeHumidity: The relative humidity values [%] from selected day.
        startDate: Start date for simulation settings.
        startTime: Start time for simulation settings.
"""

ghenv.Component.Name = "DF Envimet Simple Force by EPW"
ghenv.Component.NickName = 'DFenvimetSimpleForceByEPW'
ghenv.Component.Message = 'VER 0.0.03\nNOV_26_2018'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "6 | Utility Envimet"
#compatibleLBVersion = VER 0.0.59\nNOV_26_2018
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass


import Grasshopper.Kernel as gh
import scriptcontext as sc
import datetime
import sys
import os

def extractNumbers(listName, DOY):
    chunks = [listName[n:n+24] for n in range(0, len(listName), 24)]
    return chunks[DOY]

def main():
    
    if _DOY:
        DOY = _DOY -1
    else:
        DOY = 172
    if _HOY:
        hoy = _HOY
    else:
        hoy = 4105
    
    weatherData = lb_preparation.epwDataReader(_epwFile)
    modelYear = int(weatherData[14][7:][0])
    temperatureData = weatherData[0][7:]
    RHdata = weatherData[2][7:]
    
    dryBulbTemperature = map(lambda x : x + 273.15 , extractNumbers(temperatureData, DOY))
    relativeHumidity = extractNumbers(RHdata, DOY)
    
    # start date and start time
    d, m, t = map(int, lb_preparation.hour2Date(hoy, True))
    ladybugDate = datetime.datetime(modelYear, m+1, d, t)
    startDate = ladybugDate.strftime("%d.%m.%Y")
    startTime = ladybugDate.strftime("%H:%M:%S")
    
    return dryBulbTemperature, relativeHumidity, startDate, startTime


# import the classes
initCheck = False
w = gh.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key('ladybug_release'):
    initCheck = True
    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): initCheck = True
    except:
        initCheck = False
        warning = "You need a newer version of Ladybug to use this compoent." + \
        "Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        ghenv.Component.AddRuntimeMessage(w, warning)
    lb_preparation = sc.sticky["ladybug_Preparation"]()
else:
    initCheck = False
    print "You should first let the Ladybug fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")


#Check the data
if _epwFile and _DOY and _HOY:
    
    if initCheck == True:
        result = main()
        if result != -1:
            dryBulbTemperature, relativeHumidity, startDate, startTime = result
else:
    ghenv.Component.AddRuntimeMessage(w, "Connect all inputs.")