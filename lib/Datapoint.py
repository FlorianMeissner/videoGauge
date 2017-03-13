#!/usr/bin/env python3

# *************************************************************************************************
# * Data Point Storage Class                                                                     *
# *************************************************************************************************


# Description
# ===========

# Class to store Waypoints to be processed by VideoGaugeCreator.


# TODO
# ====

# See TODO.txt


# ABOUT
# =====

# Creator:  Florian Meissner
#           n1990b@gmx.de
# Version:  0.1
# Date:     2017/03/12


# VERSION HISTORY
# ===============

# 0.1:  - Initial Beta


###################################################################################################


class WP(object):

    WPlist = []

    # Units
    U_MPH   = "statute miles per hour"
    U_MS    = "meters per second"
    U_KT    = "knots (nautical miles per hour)"
    U_KMH   = "kilometers per second"
    U_FTMIN = "feet per minute"
    U_FT    = "feet"
    U_M     = "meters"
    U_SEC   = "seconds"
    U_MIN   = "minutes"
    U_HR    = "hours"
    U_DEG   = "degrees"
    U_INHG  = "inch mercury"
    U_HPA   = "hecopascal"


    def __init__(self):
        pass


    def addWP(self, altitude=None, duration=None, g=None, heading=None, lat=None, lon=None, \
        pitch=None, qnh=None, roll=None, speed=None, time=None, vsi=None, windDir=None, \
        windSpd=None):

        """
        Add waypoint to list. For a waypoint at least one parameter should be given.
        """

        self.WPlist.append(
            {
                "altitude"  :   altitude,
                "duration"  :   duration,
                "g"         :   g,
                "heading"   :   heading,
                "lat"       :   lat,
                "lon"       :   lon,
                "pitch"     :   pitch,
                "qnh"       :   qnh,
                "roll"      :   roll,
                "speed"     :   speed,
                "time"      :   time,
                "vsi"       :   vsi,
                "windDir"   :   windDir,
                "windSpd"   :   windSpd
            }
        )


    def changeWP(self, ident, altitude=None, duration=None, g=None, heading=None, lat=None, lon=None, pitch=None, qnh=None, roll=None, speed=None, time=None, vsi=None, windDir=None, windSpd=None):

        changedSomething = False

        if altitude is not None:
            self.WPlist[ident]['altitude'] = altitude
            changedSomething = True

        if duration is not None:
            self.WPlist[ident]['duration'] = duration
            changedSomething = True

        if g is not None:
            self.WPlist[ident]['g'] = g
            changedSomething = True

        if heading is not None:
            self.WPlist[ident]['heading'] = heading
            changedSomething = True

        if lat is not None:
            self.WPlist[ident]['lat'] = lat
            changedSomething = True

        if lon is not None:
            self.WPlist[ident]['lon'] = lon
            changedSomething = True

        if pitch is not None:
            self.WPlist[ident]['pitch'] = pitch
            changedSomething = True

        if qnh is not None:
            self.WPlist[ident]['qnh'] = qnh
            changedSomething = True

        if roll is not None:
            self.WPlist[ident]['roll'] = roll
            changedSomething = True

        if speed is not None:
            self.WPlist[ident]['speed'] = speed
            changedSomething = True

        if time is not None:
            self.WPlist[ident]['time'] = time
            changedSomething = True

        if vsi is not None:
            self.WPlist[ident]['vsi'] = vsi
            changedSomething = True

        if windDir is not None:
            self.WPlist[ident]['windDir'] = windDir
            changedSomething = True

        if windSpd is not None:
            self.WPlist[ident]['windSpd'] = windSpd
            changedSomething = True

        if not changedSomething:
            raise ValueError("At least one parameter must be specified!")


    def getListLength(self):
        """
        Returns the number of current list entries.
        """

        pass


    def getWP(self, ident, mode="nearest"):
        """
        Return a Waypoint by a given identifier and identification mode.
        ident_type can be "index" or "time".

        "index" returns a given list index and "time" the first list item matching the timestamp
        given in "ident" in "absolute"-mode or the closed match in "nearest"-mode.
        """

        pass


    def showWPtable(self):
        """
        Show a table like pattern containing all waypoints stored at the time this method is called.
        """

        # Prepare table head
        print("")
        print(" Latitude | Longitude | Altitude | Speed | Time ")
        print("----------+-----------+----------+-------+------")
        print("          |           |          |       |      ")
        #           9       9           8           5       4

        for wp in self.WPlist:
            # Print table with trackpoints.
            string = " "

            if wp['lat'] < 10:
                string += " %7.5f | " % wp['lat']
            else:
                string += "%7.5f | " % wp['lat']

            if wp['lon'] < 10:
                string += "  %7.5f | " % wp['lon']
            elif wp['lon'] < 100:
                string += " %7.5f | " % wp['lon']
            else:
                string += "%7.5f | " % wp['lon']

            if wp['altitude'] < 10:
                string += "  %7.4f | " % wp['altitude']
            elif wp['altitude'] < 100:
                string += " %7.4f | " % wp['altitude']
            else:
                string += "%7.4f | " % wp['altitude']

            if wp['speed'] < 10:
                string += " %4.1f | " % wp['speed']
            elif wp['speed'] < 100:
                string += " %4.1f | " % wp['speed']
            else:
                string += "%4.1f | " % wp['speed']

            string += str(wp['time'])
            print(string)
        print("")


#EOF
