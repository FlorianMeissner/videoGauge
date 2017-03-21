#!/usr/bin/env python3

# *****************************************************************************
# * Collection of conversions                                                 *
# *****************************************************************************


# Description
# ===========

# Collection of conversion functions often used in aviation.


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
# 1.0:  Restructured, added new conversions.


###############################################################################


# -----------------------------------------------------------------------------
# - Speed                                                                     -
# -----------------------------------------------------------------------------


# Meter per second

def ms2kmh(ms):
    ms = float(ms)
    kms = ms / 1000
    kmh = kms * 3600
    return kmh


def ms2mph(ms):
    ms = float(ms)
    mh = ms * 3600
    mph = mh / 1609.344
    return mph


def ms2kt(ms):
    ms = float(ms)
    mh = ms * 3600
    kt = mh / 1852
    return kt


def ms2ftmin(ms):
    ms = float(ms)
    mmin = ms * 60
    ftmin = mmin / 0.3048
    return ftmin


# Kilometer per hour

def kmh2ms(kmh):
    kmh = float(kmh)
    mh = kmh * 1000
    ms = mh / 3600
    return ms


def kmh2mph(kmh):
    kmh = float(kmh)
    mph = kmh / 1.609344
    return mph


def kmh2kt(kmh):
    kmh = float(kmh)
    kt = kmh / 1.852
    return kt


def kmh2ftmin(kmh):
    kmh = float(kmh)
    ftmin = kmh * 54.680666664
    return ftmin


# Miles per hour

def mph2ms(mph):
    mph = float(mph)
    mh = mph * 1609.344
    ms = mh / 3600
    return ms


def mph2kmh(mph):
    mph = float(mph)
    kmh = mph * 1.609344
    return kmh


def mph2kt(mph):
    mph = float(mph)
    kt = mph * 0.8689762419
    return kt


def mph2ftmin(mph):
    mph = float(mph)
    ftmin = mph * 88.000014306
    return ftmin


# Knots

def kt2ms(kt):
    kt = float(kt)
    sms = kt / 3600
    ms = sms * 1852
    return ms


def kt2kmh(kt):
    kt = float(kt)
    kmh = kt * 1.852
    return kmh


def kt2mph(kt):
    kt = float(kt)
    mph = kt * 1.150779448
    return mph


def kt2ftmin(kt):
    kt = float(kt)
    ftmin = 101.268568224
    return ftmin


# Feet per minute

def ftmin2ms(ftmin):
    ftmin = float(ftmin)
    mmin = ftmin * 0.3048
    ms = mmin / 60
    return ms


def ftmin2kmh(ftmin):
    ftmin = float(ftmin)
    kmh = ftmin * 0.018288
    return kmh


def ftmin2mph(ftmin):
    ftmin = float(ftmin)
    mph = ftmin * 0.0113636
    return mph


def ftmin2kt(ftmin):
    ftmin = float(ftmin)
    kt = ftmin * 0.00987473
    return kt


# -----------------------------------------------------------------------------
# - Altitude                                                                  -
# -----------------------------------------------------------------------------

def ft2m(ft):
    ft = float(ft)
    m = ft * 0.3048
    return m


def m2ft(m):
    m = float(m)
    ft = m / 0.3048
    return ft


# -----------------------------------------------------------------------------
# - Air Pressure                                                              -
# -----------------------------------------------------------------------------

def inhg2hpa(inhg):
    inhg = float(inhg)
    hpa = inhg * 33.8638866667
    return hpa


def hpa2inhg(hpa):
    hpa = float(hpa)
    inhg = hpa / 33.8638866667
    return inhg


# EOF
