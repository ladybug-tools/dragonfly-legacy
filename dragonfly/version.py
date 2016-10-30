# coding=utf-8
"""Versions and header."""
from copy import deepcopy
from datetime import datetime


class Version(object):
    """Version class."""

    DFVer = "0.0.1"
    UWGVer = "4.1"
    lastUpdated = datetime(year=2016, month=10, day=29, hour=18, minute=35)

    def duplicate(self):
        """Return a copy of this object."""
        return deepcopy(self)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Version."""
        return 'Version::Butterfly{}::OpenFOAM{}'.format(self.BFVer, self.OFVer)
