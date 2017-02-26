#!/usr/bin/env python3

# *************************************************************************************************
# * Collection of interpolation methods                                                           *
# *************************************************************************************************


# Description
# ===========

# Collection of interpolation method functions.


# TODO
# ====

# - Add nonlinear functions


# ABOUT
# =====

# Creator:  Florian Meissner
#           n1990b@gmx.de
# Version:  0.1
# Date:     2017/02/21


# VERSION HISTORY
# ===============

# 0.1:  Initial Beta


###################################################################################################


# Linear Equation 2 point method
# Get Y coordinate from a known X on a straight line.
# Straight line is defined by (x1|y1) and (x2|y2).
def linEqu2pt(x1, y1, x2, y2, x):
    y = ( ( y2 - y1 ) / ( x2 - x1 ) ) * ( x - x1 ) + y1
    return y


# EOF
