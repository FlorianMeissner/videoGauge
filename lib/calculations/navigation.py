#!/usr/bin/env python3

# *****************************************************************************
# * Collection of navigational calculations                                   *
# *****************************************************************************


# Description
# ===========

# Collection of calculations used for aeronautical navigational purposes.


# TODO
# ====

# -


# ABOUT
# =====

# Creator:  Florian Meissner
#           n1990b@gmx.de
# Version:  0.1
# Date:     2017/03/21


# VERSION HISTORY
# ===============

# 0.1:  Initial Beta


###############################################################################


from math import sin, cos, asin, atan2, sqrt, radians, degrees


def getBearing(wp1, wp2):
    """
    Calculate bearing between two points specified by latitude and longitude.
    Formula from http://www.movable-type.co.uk/scripts/latlong.html#bearing
    """

    # lat, lon in degrees
    # phi, lambda in radians

    lat1, lon1 = wp1
    lat2, lon2 = wp2

    # Convert to radians.
    phi1 = radians(lat1)
    lambda1 = radians(lon1)
    phi2 = radians(lat2)
    lambda2 = radians(lon2)

    y = sin(lambda2 - lambda1) * cos(phi2)
    x = cos(phi1) * sin(phi2) - sin(phi1) * cos(phi2) * cos(lambda2 - lambda1)

    bearing = atan2(y, x)
    bearing = degrees(bearing)

    # atan2 gives values between -180 deg and 180 deg.
    return (bearing + 360) % 360


def getDistance(wp1, wp2):
    """
    Calculate the distance between two points specified by latitude and longitude.
    Formular from http://www.movable-type.co.uk/scripts/latlong.html#distance
    """

    # lat, lon in degrees
    # phi, lambda in radians

    lat1, lon1 = wp1
    lat2, lon2 = wp2

    # Convert to radians.
    phi1 = radians(lat1)
    lambda1 = radians(lon1)
    phi2 = radians(lat2)
    lambda2 = radians(lon2)

    earth_radius = 6371000 # meters

    delta_phi = phi2 - phi1
    delta_lambda = lambda2 - lambda1

    a = sin(delta_phi/2)**2 + cos(phi1) * cos(phi2) * sin(delta_lambda/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    dist = earth_radius * c

    return dist


def findFix(startWP, bearing, distance):
    """
    Calculate a fix defined by a waypoint, bearing and distance..
    Formular from http://www.movable-type.co.uk/scripts/latlong.html#destPoint
    """

    earth_radius = 6371000 # meters

    # lat, lon in degrees
    # phi, lambda in radians

    lat1, lon1 = startWP

    # Convert to radians.
    phi1 = radians(lat1)
    lambda1 = radians(lon1)

    dr = distance / earth_radius

    phi2 = asin(sin(phi1) * cos(dr) + cos(phi1) * sin(dr) * cos(bearing))
    lambda2 = lambda1 + atan2(sin(bearing) * sin(dr) * cos(phi1), cos(dr) - sin(phi1) * sin(phi2))

    lat2 = degrees(phi2)
    lon2 = degrees(lambda2)

    lon2 = (lon2 + 540)%360 - 180

    return (lat2, lon2)


# EOF
