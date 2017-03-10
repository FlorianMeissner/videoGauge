#!/usr/bin/env python3

# *************************************************************************************************
# * Exceptions                                                                                    *
# *************************************************************************************************


# Description
# ===========

# Definition of own Exceptions used in Video Gauge Creator.


# TODO
# ====

# -


# ABOUT
# =====

# Creator:  Florian Meissner
#           n1990b@gmx.de
# Version:  0.1
# Date:     2017/03/10


# VERSION HISTORY
# ===============

# 0.1:  - Initial Beta


###################################################################################################


class AbstractImplementationRequired(Exception):
    """
    Implementation of given object in child class is required.
    """

    def __init__(self, obj=""):

        msg = "The object '%s' needs to be implemented in child class!" % obj
        super(AbstractImplementationRequired, self).__init__(msg)
