#!/usr/bin/env python3

# *************************************************************************************************
# * Calibration Table                                                                             *
# *************************************************************************************************


# Description
# ===========

# Calibration table for gauge of this folder.


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

# 0.1:  Initial Beta


###################################################################################################


def calibration():

    # Define calibration table. Non existing speed values will be interpolated between existing
    # neighbours linearly.
    cal = {
        # m/s : Degree
           -5 : -135.99,
           -4 : -108.55,
           -3 :  -80.54,
           -2 :  -53.20,
           -1 :  -26.41,
            0 :    0.00,
            1 :   26.70,
            2 :   52.74,
            3 :   79.97,
            4 :  106.47,
            5 :  133.23 
    }
    return cal
