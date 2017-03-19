#!/usr/bin/env python3

# *************************************************************************************************
# * Data Point Storage Class                                                                     *
# *************************************************************************************************


# Description
# ===========

# Class to store Waypoints to be processed by VideoGaugeCreator.


# TODO
# ====

# - Create method to get neighbouring waypoints
# - Add unit handling


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


from datetime import datetime
from operator import itemgetter
import logging


class WP(object):

    WPlist = []

    # Units
    U_DEG   = "degrees"
    U_FT    = "feet"
    U_FTMIN = "feet per minute"
    U_HPA   = "hectopascal"
    U_HR    = "hours"
    U_INHG  = "inch mercury"
    U_MPH   = "statute miles per hour"
    U_KMH   = "kilometers per second"
    U_KT    = "knots (nautical miles per hour)"
    U_M     = "meters"
    U_MIN   = "minutes"
    U_MS    = "meters per second"
    U_SEC   = "seconds"

    # Defaults
    DEFAULT_U_ALTITUDE  =   U_FT
    DEFAULT_U_DURATION  =   U_SEC
    #~ DEFAULT_U_G         =
    DEFAULT_U_HEADING   =   U_DEG
    DEFAULT_U_LAT       =   U_DEG
    DEFAULT_U_LON       =   U_DEG
    DEFAULT_U_PITCH     =   U_DEG
    DEFAULT_U_QNH       =   U_HPA
    DEFAULT_U_ROLL      =   U_DEG
    DEFAULT_U_SPEED     =   U_KT
    #~ DEFAULT_U_TIME      =
    DEFAULT_U_TIMESTAMP =   U_SEC
    DEFAULT_U_VSI       =   U_FTMIN
    DEFAULT_U_WINDDIR   =   U_DEG
    DEFAULT_U_WINDSPD   =   U_KT

    # Control variables
    __listOrdered = False


    def __init__(self):
        pass


    # ---------------------------------------------------------------------------------------------
    # - Interface methods                                                                         -
    # ---------------------------------------------------------------------------------------------


    def addWP(self, altitude=None, duration=None, g=None, heading=None, lat=None, lon=None, \
        pitch=None, qnh=None, roll=None, speed=None, time=None, timestamp=None, vsi=None, \
        windDir=None, windSpd=None):

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
                "timestamp" :   timestamp,
                "vsi"       :   vsi,
                "windDir"   :   windDir,
                "windSpd"   :   windSpd,

                "lowerNeighbour"    :   None,
                "higherNeighbour"   :   None
            }
        )

        self.__listOrdered = False


    def changeWP(self, ident, altitude=None, duration=None, g=None, heading=None, lat=None, \
        lon=None, pitch=None, qnh=None, roll=None, speed=None, time=None, timestamp=None, \
        vsi=None, windDir=None, windSpd=None, lowerNeighbour=None, higherNeighbour=None):

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

        if timestamp is not None:
            self.WPlist[ident]['timestamp'] = timestamp
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

        if lowerNeighbour is not None:
            self.WPlist[ident]['lowerNeighbour'] = lowerNeighbour
            changedSomething = True

        if higherNeighbour is not None:
            self.WPlist[ident]['higherNeighbour'] = higherNeighbour
            changedSomething = True

        if not changedSomething:
            raise ValueError("At least one parameter must be specified!")

        self.__listOrdered = False


    def calculate(self):
        self.showWPtable()
        self.__convertTimestamp()
        self.__orderByParam('timestamp')
        self.__videoTimestamp()
        self.__getNeighbour()
        self.showWPtable()


    def getWPListLength(self):
        """
        Returns the number of current list entries.
        """

        return len(self.WPlist)


    def getWP(self, identifier, ident_type, ident_mode="nearest"):
        """
        Return a Waypoint by a given identifier and identification mode.
        ident_type can be "index" or "time".

        "index" returns a given list index and "time" the first list item matching the timestamp
        given in "identifier" in "absolute"-mode or the closed match in "nearest"-mode.
        """

        ident_type = ident_type.lower()
        ident_mode = ident_mode.lower()

        if ident_type == "index":
            return self.WPlist[identifier]

        elif ident_type == "time":
            if ident_mode == "absolute":
                pass
            elif ident_mode == "nearest":
                pass
            else:
                raise ValueError("Unknown ident_mode %s" % ident_mode)

        else:
            raise ValueError("Unknown ident_type %s" % ident_type)


    def showWPtable(self):
        """
        Show a table like pattern containing all waypoints stored at the time this method is called.
        """

        def subfunc(wp):

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
            string += ", %s sec" % wp['timestamp']
            string += ", %s, %s" % (wp['lowerNeighbour'], wp['higherNeighbour'])
            return string

        # Prepare table head
        print("")
        print(" Latitude | Longitude | Altitude | Speed | Time ")
        print("----------+-----------+----------+-------+------")
        print("          |           |          |       |      ")
        #           9       9           8           5       4

        for line in self.__iterWPlist(subfunc, ret=True):
            print line

        print("")


    # ---------------------------------------------------------------------------------------------
    # - Calculation methods                                                                       -
    # ---------------------------------------------------------------------------------------------


    def __convertTimestamp(self, epoch=datetime(1970,1,1)):
        """
        Convert datetime.datetime timestamps from GPX into video squence timestamps. Video sequence
        starts at 0 sec.
        """

        def subfunc(wp, epoch):
            t = wp['time']
            ts = wp['timestamp']

            if ts is None:
                #~ print type(t), type(epoch)
                td = t - epoch
                ts = td.total_seconds()
                return ('timestamp', ts)

        ret = self.__iterWPlist(subfunc, {'epoch':epoch}, writeChange=True)


    def __getTimeLength(self):
        """
        Get length of frame. Determine time to next frame.
        This function also adds the length of each GPX frame to the list of track points.
        """

        trkPtsCount = len(self.trkPts)

        for trkPt in self.trkPts:

            # get key of track point.
            key = self.trkPts.index(trkPt)

            # If last track point, set length to 0.
            if key == trkPtsCount - 1:
                length = 0

            # Process all other track points.
            else:
                ownTs = trkPt['timestamp']
                nextTs = self.trkPts[key+1]['timestamp']
                length = nextTs - ownTs

            self.trkPts[key]['length'] = length


    def __getNeighbour(self):
        """
        Iteratre through list of waypoints and get index of both neighbouring waypoints. If it is
        the first waypoint, set lower neighbour to FIRST and if it is last waypoint set higher
        neighbour to LAST.
        """

        print("GetNeighbour")
        def subfunc(wp, i, direction):
            """
            direction expects L or H for lower and higher neighbour.
            """

            if direction == "L":
                if i == 0:
                    ret = "FIRST"
                else:
                    ret = i -1
                return ('lowerNeighbour', ret)

            elif direction == "H":
                if i == self.getWPListLength() - 1:
                    ret = "LAST"
                else:
                    ret = i + 1
                return ('higherNeighbour', ret)

            else:
                raise ValueError("Unknown parameter %s for direction." % direction)

        self.__iterWPlist(subfunc, args="L", passIndex=True, writeChange=True)
        self.__iterWPlist(subfunc, args="H", passIndex=True, writeChange=True)


    def __iterWPlist(self, func, args=None, passIndex=False, writeChange=False, ret=False):
        """
        Iterate through all waypoints an apply func to each one.
        func expects a function with first parameter to be the given waypoint. Further parameters
        can be passed as tuple or dict in args.
        If 'writeChange' is True func is expected to return a tuple (key, value) for the parameter
        to be written
        """

        retL = []   # List for return values

        for i in range(self.getWPListLength()):
            wp = self.getWP(i, "index")

            if args is None:
                print("args: None")
                if passIndex:
                    retVal = func(wp, i)
                else:
                    retVal = func(wp)

            elif isinstance(args, dict):
                print("args: Dict")
                if passIndex:
                    args['i'] = i
                retVal = func(wp, **args)

            elif args is tuple or args is list:
                print("args: Tuple, List")
                if passIndex:
                    args.append(i)
                retVal = func(wp, *args)

            else:
                print("args: else")
                if passIndex:
                    retVal = func(wp, i, args)
                else:
                    retVal = func(wp, args)

            if retVal == "BREAK":
                writeChange = False
                break
            elif retVal == "CONTINUE":
                continue

            if writeChange:
                self.changeWP(i, **{retVal[0]:retVal[1]})

            if ret:
                retL.append(retVal)

        if ret:
            if len(retL) == 1:
                return retL[0]
            else:
                return retL


    def __orderByParam(self, param):
        """
        Order list of waypoints by a given dict key. The waypoint dicts themself remain untouched
        but their order within the list will be altered.
        """

        self.WPlist = sorted(self.WPlist, key=itemgetter(param))
        self.__listOrdered = True


    def __videoTimestamp(self):
        """
        Convert timestamps to video position. First waypoint will be 0 seconds.
        """

        def firstTs(wp, i):
            if i == 0:
                return wp['timestamp']
            else:
                return "BREAK"


        def calculator(wp, ref):
            ts = wp['timestamp'] - ref
            return ('timestamp', ts)


        # Check if waypoints are in order. Don't check by which parameter they were ordered.
        # If unordered, order by timestamp.
        if not self.__listOrdered:
            self.__orderByParam('timestamp')

        ref = self.__iterWPlist(firstTs, passIndex=True, ret=True)
        self.__iterWPlist(calculator, ref, writeChange=True)



#EOF
