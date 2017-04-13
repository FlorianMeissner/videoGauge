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
# Date:     2017/04/07


# VERSION HISTORY
# ===============

# 0.1:  Initial Beta


###################################################################################################


from math                   import floor


def calibration():

    # Define calibration table. Non existing speed values will be interpolated between existing
    # neighbours linearly.
    cal = {
        #FT : Degree
        0.0 :   0.28,
        0.2 :   6.34,
        0.4 :  13.42,
        0.6 :  20.79,
        0.8 :  28.21,
        1.0 :  35.47,
        1.2 :  42.65,
        1.4 :  49.88,
        1.6 :  56.93,
        1.8 :  63.94,
        2.0 :  71.39,
        2.2 :  78.30,
        2.4 :  85.12,
        2.6 :  92.82,
        2.8 :  99.93,
        3.0 : 107.63,
        3.2 : 114.49,
        3.4 : 121.89,
        3.6 : 128.83,
        3.8 : 136.14,
        4.0 : 143.46,
        4.2 : 151.16,
        4.4 : 158.62,
        4.6 : 165.96,
        4.8 : 173.32,
        5.0 : 179.73,
        5.2 : 187.09,
        5.4 : 194.36,
        5.6 : 202.00,
        5.8 : 209.31,
        6.0 : 216.71,
        6.2 : 224.01,
        6.4 : 231.34,
        6.6 : 238.64,
        6.8 : 245.60,
        7.0 : 252.94,
        7.2 : 260.13,
        7.4 : 266.47,
        7.6 : 274.09,
        7.8 : 281.36,
        8.0 : 288.85,
        8.2 : 295.63,
        8.4 : 302.83,
        8.6 : 309.74,
        8.8 : 316.85,
        9.0 : 324.03,
        9.2 : 331.37,
        9.4 : 338.78,
        9.6 : 345.89,
        9.8 : 352.84,
       10.0 : 360.28
    }
    return cal


def splitPower(number):
    """
    Splits a given number into powers of 10.

    rot* holds the amount of revolutions needed to display its part of number
    correctly. Used for accurate animation beyond one return of needle.
    """

    FACEPLATE_MAX = 10

    number = float(number)
    tenthousend = number / 10000
    thousend = (number - floor(tenthousend) * 10000) / 1000
    hundret = (number - floor(tenthousend) * 10000 - \
        floor(thousend) * 1000) / 100

    rot10000 = floor(tenthousend / FACEPLATE_MAX)
    rot1000 = floor(tenthousend)
    rot100 = floor(thousend) + rot1000 * 10

    return (tenthousend, thousend, hundret, rot10000, rot1000, rot100)


# EOF
