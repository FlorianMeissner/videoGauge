#!/usr/bin/env python3

# *****************************************************************************
# * Collection of conversions                                                 *
# *****************************************************************************


# Description
# ===========

# Collection of conversion functions often used for visual displays.


# TODO
# ====

# -


# ABOUT
# =====

# Creator:  Florian Meissner
#           n1990b@gmx.de
# Version:  1.0
# Date:     2017/03/21


# VERSION HISTORY
# ===============

# 0.1:  Initial Beta
# 1.0:  Restructured, Split from av_conv.py


###############################################################################


# Color
# =====

def colorHex2RGB(hexstr):
    hexstr = hexstr.strip("#")
    lv = len(hexstr)
    return tuple(int(hexstr[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def colorRGB2Hex(r, g, b):
    return '#%02x%02x%02x' % (r, g, b)



# Coordinates
# ===========

# Spilt coordinate string by 'x' inthe middle into tuple.
# E.g. '1280x720' -> '(1280, 720)'
def splitXY(string):
    x, y = string.split('x')
    return (int(x), int(y))


# EOF
