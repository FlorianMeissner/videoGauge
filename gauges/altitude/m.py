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
# Date:     2017/03/09


# VERSION HISTORY
# ===============

# 0.1:  Initial Beta


###################################################################################################


def calibration():

    # Define calibration table. Non existing speed values will be interpolated between existing
    # neighbours linearly.
    cal = {
        # MPH : Degree
            0 :   0.0,
           30 :  13.9,
           35 :  18.5,
           40 :  24.3,
           45 :  30.8,
           50 :  37.1,
           55 :  46.6,
           60 :  49.1,
           70 :  68.2,
           80 :  85.7,
           90 : 109.5,
          100 : 133.4,
          110 : 155.5,
          120 : 180.0,
          130 : 205.2,
          140 : 230.2,
          150 : 258.9,
          160 : 287.4,
          170 : 311.9,
          180 : 337.0
    }
    return cal
