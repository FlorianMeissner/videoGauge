#!/usr/bin/env python3

# *************************************************************************************************
# * My Misc Functions                                                                             *
# *************************************************************************************************


# Description
# ===========

# This file contains several functions often needed for differend applications. Usually they can be
# called directly.


# TODO
# ====

# -


# ABOUT
# =====

# Creator:  Florian Meissner
#           n1990b@gmx.de
# Version:  0.1
# Date:     2017/03/09


# VERSION HISTORY
# ===============

# 0.1:  - Initial Beta (containing 'basePath()')
# 0.2:  - Added lookahead()


###################################################################################################


from math                   import floor
import os


# Returns an absolute path. Expects __file__ object of calling module as parent. If parent is empty
# path of this module will be returned.
def basePath(parent=None):

    # If parent is not set, use __file__object of this module. Otherwise use given one.
    if parent is None:
        parent = __file__

    # Get absolute path to parent module.
    fullpath = os.path.realpath(parent)

    # Crop filename from path.
    bp =  os.path.dirname(fullpath)

    # Add trailing slash if missing.
    if bp[-1] != "/":
        bp += "/"

    return bp


def lookahead(iterable):
    """
    Pass through all values from a given iterable, augmented by the information if there are more
    values to come after the current one (True) or if it is the last value (False).
    https://stackoverflow.com/a/1630350
    """

    # Get interator and pull first value.
    it = iter(iterable)
    last = next(it)

    # Run iterator to exhaustion (starting from second value).
    for val in it:

        # report previous value.
        yield last, val
        last = val

    # Report last value.
    yield last


def splitPower(number):
    """
    Splits a given number into powers of 10.
    """

    FACEPLATE_MAX = 10

    number = float(number)
    tenthousend = number / 10000
    thousend = (number - floor(tenthousend) * 10000) / 1000
    hundret = (number - floor(tenthousend) * 10000 - \
        floor(thousend) * 1000) / 100

    print tenthousend, thousend, hundret

    rot10000 = floor(tenthousend / FACEPLATE_MAX)
    rot1000 = floor(tenthousend)
    rot100 = floor(thousend) + rot1000 * 10

    print rot10000, rot1000, rot100

    return (tenthousend, thousend, hundret, rot10000, rot1000, rot100)


# EOF
