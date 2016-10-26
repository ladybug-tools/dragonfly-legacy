"""Dragonfly configurations.

Import this module in every module that you need to access Dragonfly configurations.

Usage:

    import config
    print config.uwgPath
    print config.platform
    config.uwgPath = "c:/UWG"
"""

from collections import namedtuple
import os
import sys

class Platform(object):
    """Identify how the script is currently executing.

    0: Running as standard python script
    1: Running inside grasshopper component
    2: Running inside dynamo node
    3: Running inside dynamo node from Revit

    Usage:

        platform = Platform(mute=True)
        p = platform.platform
        pId = platform.platformId
        print "Platform is {} > {}.".format(p, pId)

        >> Dragonfly is running from gh. platform id: 1.
    """

    def __init__(self, mute=False):
        """Find currect platform and platformId."""
        self.__mute = mute

        self.platform = None
        """Current platform that imports the libraries as a string.

        Values:
            None: Running as standard python script
            'gh': Grasshopper
            'ds': Dynamo
            'rvt': Dynamo from inside Revit
        """
        self.platformId = 0
        """Current platformId that imports the libraries as a string.

        Values:
            0: Running as standard python script
            1: Grasshopper
            2: Dynamo
            3: Dynamo from inside Revit
        """
        # created a named tuple for libraries
        self._Libs = namedtuple("Libs", "Rhino Grasshopper Dynamo DesignScript")
        self.libs = None
        """Collection of libraries for this platform.

        Usage:

            from Dragonflyx import config
            gh = config.libs.Grasshopper
            rc = config.libs.Rhino

        """

        __cwd = os.getcwdu().lower()

        if __cwd.find("rhino") > -1:
            # It's running from inside grasshopper component
            self.platform = "gh"
            self.platformId = 1
        elif __cwd.find("dynamo") > -1:
            # It's running from inside dynamo script
            self.platform = "ds"
            self.platformId = 2
        elif __cwd.find("revit") > -1:
            # It's running from inside Revit from a Dynamo node
            self.platform = "rvt"
            self.platformId = 3
        elif __cwd.find("python") == -1:
            # Revit changes the directory to where the file is, if user change
            # the revit file but doesn't close the Dynamo window! :|
            self.platform = "rvt"
            self.platformId = 3

        if not mute:
            print "Dragonfly is running from {}. platform id: {}." \
                .format(self.platform, self.platformId)

        self.importGeometryLibraries()

    @property
    def isRevit(self):
        """Return True if platform is Revit."""
        return self.platform == "rvt"

    @property
    def isDynamo(self):
        """Return True if platform is Dynamo Studio."""
        return self.platform == "ds"

    @property
    def isGrasshopper(self):
        """Return True if platform is Grasshopper."""
        return self.platform == "gh"

    @property
    def isRevitOrDynamo(self):
        """Return True if platform is Revit or Dynamo Studio."""
        return self.isRevit or self.isDynamo

    def importGeometryLibraries(self):
        """
        Import geometry libraries based on platform.

        This approach will avoid importing libraries for several times.
        """
        # import libraries once in config and share it between all the geometry libraries
        if not self.__mute:
            print "Importing geometry libraries..."

        if self.platformId == 1:
            # Import Rhino and Grasshopper
            try:
                gh = __import__('Grasshopper')
                if not self.__mute:
                    print "Grasshopper imported under config.libs.Grasshopper"

                rc = __import__('Rhino')
                if not self.__mute:
                    print "Rhino imported under config.libs.Rhino"

            except ImportError as e:
                print "Failed to import geometry libraries {}".format(e)

            else:
                # Assign Rhino and Grasshopper to the libraries
                self.libs = self._Libs(rc, gh, None, None)

        if self.platformId == 2 or self.platformId == 3:
            try:
                import clr
                clr.AddReference('DynamoCore')
                clr.AddReference('ProtoGeometry')
                clr.AddReference('ProtoInterface')
                import Autodesk.DesignScript as ds
                if not self.__mute:
                    print "DesignScript imported under config.libs.DesignScript"

                __dynamoPath = "\\".join((clr.References[2].Location).split("\\")[:-1])
                sys.path.append(__dynamoPath)
                import Dynamo as dyn
            except ImportError as e:
                print "Failed to import geometry libraries {}".format(e)

            else:
                # Assign Rhino and Grasshopper to the libraries
                self.libs = self._Libs(None, None, dyn, ds)

    def __repr__(self):
        """Return platform."""
        return "{}".format(self.platform)


# expose platform and libraries as global variables
platform = Platform(mute=False)
platformId = platform.platformId
libs = platform.libs
