# HoneybeePlus: A Plugin for CFD Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of HoneybeePlus.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
This component installs the uwg libraries to:
C:\Users\%USERNAME%\AppData\Roaming\McNeel\Rhinoceros\6.0\scripts\UEG

The grasshopper file should be in the same folder as the uwg libraries and dragonfly userobjects folder to work correctly.
You can download the package from the Dragonfly github.

-

    Args:
        _install: Set to True to install dragonfly.
"""

ghenv.Component.Name = "DF Update"
ghenv.Component.NickName = "DFUpdate"
ghenv.Component.Message = 'VER 0.0.03\nNOV_25_2018'
ghenv.Component.Category = "Dragonfly"
ghenv.Component.SubCategory = "4 | Developers"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

import os
import System
import sys
import zipfile
import shutil
from Grasshopper.Folders import UserObjectFolders
System.Net.ServicePointManager.SecurityProtocol = System.Net.SecurityProtocolType.Tls12


def updateDragonfly():
    
    """
    This code will download the uwg library from github to:
        C:\Users\%USERNAME%\AppData\Roaming\McNeel\Rhinoceros\6.0\scripts\honeybee
    """
    folders = ['uwg']
    repos = ['Dragonfly']

    targetDirectory = [p for p in sys.path if p.find('scripts')!= -1][0]
    try:
        targetDirectory = [p for p in sys.path if p.find('scripts')!= -1][0]
    except IndexError:
        # there is no scripts in path try to find plugins folder
        try:
            targetDirectory = [p for p in sys.path if p.find(r'settings\lib')!= -1][0]
        except IndexError:
            raise IOError('Failed to find a shared path in sys.path to install honeybee.\n' \
                          'Make sure Grasshopper is installed correctly!')

    # delete current folders 
    for f in folders:
        libFolder = os.path.join(targetDirectory, f)
        if os.path.isdir(libFolder):
            try:
                print 'removing {}'.format(libFolder)
                shutil.rmtree(libFolder)
            except:
                print 'Failed to remove {}.'.format(libFolder)
    
    # download files
    for repo in repos:
        url = "https://github.com/chriswmackey/%s/archive/master.zip" % repo
        # download the zip file
        print "Downloading {} the github repository to {}".format(repo, targetDirectory)
        zipFile = os.path.join(targetDirectory, '%s.zip' % repo)
        
        try:
            client = System.Net.WebClient()
            client.DownloadFile(url, zipFile)
        except Exception, e:
            msg = `e` + "\nDownload failed! Try to download and unzip the file manually form:\n" + url
            raise Exception(msg)
        
        #unzip the file
        with zipfile.ZipFile(zipFile) as zf:
            for f in zf.namelist():
                if f.endswith('/'):
                    try:
                        os.makedirs(f)
                    except:
                        pass
                else:
                    zf.extract(f, targetDirectory)
        zf.close()
        try:
            os.remove(zipFile)
        except:
            pass
    
    # copy files to folder.
    for f in folders:
        sourceFolder = os.path.join(targetDirectory, "Dragonfly-master", 'uwg')
        libFolder = os.path.join(targetDirectory, 'uwg')
        print 'Copying {} source code to {}'.format(f, libFolder)
        try:
            shutil.copytree(sourceFolder, libFolder)
        except Exception as e:
            if f.endswith('grasshopper'):
                # copy [+] files over and overwrite the original files.
                for ff in os.listdir(sourceFolder):
                    sf = os.path.join(sourceFolder, ff)
                    shutil.copy(sf, libFolder)
            else:
                raise Exception('Failed to copy:\n{}'.format(e))
    
    # copy user-objects
    uofolder = UserObjectFolders[0]

    pl = 'Dragonfly'
    userObjectsFolder = os.path.join(
        targetDirectory,
        r"{}-master\userObjects".format(pl))

    plus_uofolder = os.path.join(uofolder, pl)
    if not os.path.isdir(plus_uofolder):
        os.mkdir(plus_uofolder)

    print 'Removing {} userobjects.'.format(pl, uofolder)

    # remove older userobjects
    for f in os.listdir(uofolder):
        if os.path.isdir(os.path.join(uofolder, f)):
            continue
        if f == pl:
            try:
                os.remove(os.path.join(uofolder, f))
            except:
                print('Failed to remove {}'.format(os.path.join(uofolder, f)))
    for f in os.listdir(plus_uofolder):
        if f == pl:
            try:
                os.remove(os.path.join(plus_uofolder, f))
            except:
                print('Failed to remove {}'.format(os.path.join(plus_uofolder, f)))
                
    print 'Copying {} userobjects to {}.'.format(pl, uofolder)

    for f in os.listdir(userObjectsFolder):
        shutil.copyfile(os.path.join(userObjectsFolder, f),
                        os.path.join(plus_uofolder, f))

    # try to clean up
    for r in repos:
        try:
            shutil.rmtree(os.path.join(targetDirectory, '{}-master'.format(r)))
        except:
            pass

if _update:
    try:
        updateDragonfly()
    except ImportError as e:
        raise Exception("Failed to update Dragonfly:\n{}".format(e))
    else:
        try:
            import uwg
        except ImportError as e:
            raise ImportError('Failed to import the uwg:\n{}'.format(e))
        else:
            print "\n\nImported uwg! \nVviiiizzzz..."
            print "Restart Grasshopper and Rhino to load the new library."
else:
    print 'Set update to True to update Dragonfly and the uwg!'
