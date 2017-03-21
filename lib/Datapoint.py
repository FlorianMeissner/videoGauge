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


# own libraries
import lib.calculations.av_conv

# foreign libraries
from datetime import datetime
from operator import itemgetter
from terminaltables import AsciiTable as Table
import logging


class WP(object):

    WPlist = []

    # Units
    U_DEG   = "deg"
    U_FT    = "ft"
    U_FTMIN = "ftmin"
    U_HPA   = "hpa"
    U_HR    = "h"
    U_INHG  = "inhg"
    U_MPH   = "mph"
    U_KMH   = "kmh"
    U_KT    = "kt"
    U_M     = "m"
    U_MIN   = "min"
    U_MS    = "ms"
    U_SEC   = "sec"

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

    # Possible units
    U_ALTITUDE = (U_FT, U_M)
    U_DURATION = (U_SEC, U_MIN, U_HR)
    #~ U_G = ()
    U_HEADING = (U_DEG)
    U_LAT = (U_DEG)
    U_LON = (U_DEG)
    U_PITCH = (U_DEG)
    U_QNH = (U_INHG, U_HPA)
    U_ROLL = (U_DEG)
    U_SPEED = (U_KT, U_MPH, U_KMH, U_MS)
    #~ U_TIME = ()
    U_TIMESTAMP = (U_SEC)
    U_VSI = (U_FTMIN, U_MS)
    U_WINDDIR = (U_DEG)
    U_WINDSPD = (U_KT, U_MPH, U_KMH, U_FTMIN, U_MS)


    # Control variables
    __listCalculated = False
    __listOrdered = False
    __refTimestamp = None


    def __init__(self):
        pass


    # ---------------------------------------------------------------------------------------------
    # - Interface methods                                                                         -
    # ---------------------------------------------------------------------------------------------


    def addWP(self, \
        altitude    =   None,   altitude_unit   =   DEFAULT_U_ALTITUDE, \
        duration    =   None,   duration_unit   =   DEFAULT_U_DURATION, \
        g           =   None, \
        heading     =   None,   heading_unit    =   DEFAULT_U_HEADING, \
        lat         =   None,   lat_unit        =   DEFAULT_U_LAT, \
        lon         =   None,   lon_unit        =   DEFAULT_U_LON, \
        pitch       =   None,   pitch_unit      =   DEFAULT_U_PITCH, \
        qnh         =   None,   qnh_unit        =   DEFAULT_U_QNH, \
        roll        =   None,   roll_unit       =   DEFAULT_U_ROLL, \
        speed       =   None,   speed_unit      =   DEFAULT_U_SPEED, \
        time        =   None, \
        timestamp   =   None,   timestamp_unit  =   DEFAULT_U_TIMESTAMP, \
        vsi         =   None,   vsi_unit        =   DEFAULT_U_VSI, \
        windDir     =   None,   windDir_unit    =   DEFAULT_U_WINDDIR, \
        windSpd     =   None,   windSpd_unit    =   DEFAULT_U_WINDSPD):

        """
        Add waypoint to list. For a waypoint at least one parameter should be given.
        """

        # Check if at least one parameters has been set.
        params = (altitude, duration, g, heading, lat, lon, pitch, qnh, roll, speed, time, \
            timestamp, vsi, windDir, windSpd)

        if all(v is None for v in params):
            raise ValueError("Specify at least one parameter to add a new waypoint.")

        # Parse units and convert values if neccessary.
        altitude = self.__setParam(
            altitude,
            altitude_unit,
            self.DEFAULT_U_ALTITUDE,
            self.U_ALTITUDE
        )
        duration = self.__setParam(
            duration,
            duration_unit,
            self.DEFAULT_U_DURATION,
            self.U_DURATION
        )
        """
        g = self.__setParam(
            g,
            g_unit,
            self.DEFAULT_U_G,
            self.U_G
        )
        """
        heading = self.__setParam(
            heading,
            heading_unit,
            self.DEFAULT_U_HEADING,
            self.U_HEADING
        )
        lat = self.__setParam(
            lat,
            lat_unit,
            self.DEFAULT_U_LAT,
            self.U_LAT
        )
        lon = self.__setParam(
            lon,
            lon_unit,
            self.DEFAULT_U_LON,
            self.U_LON
        )
        pitch = self.__setParam(
            pitch,
            pitch_unit,
            self.DEFAULT_U_PITCH,
            self.U_PITCH
        )
        qnh = self.__setParam(
            qnh,
            qnh_unit,
            self.DEFAULT_U_QNH,
            self.U_QNH
        )
        roll = self.__setParam(
            roll,
            roll_unit,
            self.DEFAULT_U_ROLL,
            self.U_ROLL
        )
        speed = self.__setParam(
            speed,
            speed_unit,
            self.DEFAULT_U_SPEED,
            self.U_SPEED
        )
        """
        time = self.__setParam(
            time,
            time_unit,
            self.DEFAULT_U_TIME,
            self.U_TIME
        )
        """
        timestamp = self.__setParam(
            timestamp,
            timestamp_unit,
            self.DEFAULT_U_TIMESTAMP,
            self.U_TIMESTAMP
        )
        vsi = self.__setParam(
            vsi,
            vsi_unit,
            self.DEFAULT_U_VSI,
            self.U_VSI
        )
        windDir = self.__setParam(
            windDir,
            windDir_unit,
            self.DEFAULT_U_WINDDIR,
            self.U_WINDDIR
        )
        windSpd = self.__setParam(
            windSpd,
            windSpd_unit,
            self.DEFAULT_U_WINDSPD,
            self.U_WINDSPD
        )

        self.WPlist.append(
            {
                # Actual data fields
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

                # Support fields
                "higherNeighbour"   :   None,
                "lowerNeighbour"    :   None
            }
        )

        # Perfom gap filling calculations.
        self.__listOrdered = False
        self.__listCalculated = False
        self.__calculate()


    def changeWP(self, ident, \
        altitude        =   None,   altitude_unit   =   DEFAULT_U_ALTITUDE, \
        duration        =   None,   duration_unit   =   DEFAULT_U_DURATION, \
        g               =   None, \
        heading         =   None,   heading_unit    =   DEFAULT_U_HEADING, \
        lat             =   None,   lat_unit        =   DEFAULT_U_LAT, \
        lon             =   None,   lon_unit        =   DEFAULT_U_LON, \
        pitch           =   None,   pitch_unit      =   DEFAULT_U_PITCH, \
        qnh             =   None,   qnh_unit        =   DEFAULT_U_QNH, \
        roll            =   None,   roll_unit       =   DEFAULT_U_ROLL, \
        speed           =   None,   speed_unit      =   DEFAULT_U_SPEED, \
        time            =   None, \
        timestamp       =   None,   timestamp_unit  =   DEFAULT_U_TIMESTAMP, \
        vsi             =   None,   vsi_unit        =   DEFAULT_U_VSI, \
        windDir         =   None,   windDir_unit    =   DEFAULT_U_WINDDIR, \
        windSpd         =   None,   windSpd_unit    =   DEFAULT_U_WINDSPD, \
        lowerNeighbour  =   None, \
        higherNeighbour =   None):

        """
        Change the given parameters of a waypoint identified by its list index in ident.
        """

        # Check if at least one parameters has been set.
        params = (altitude, duration, g, heading, lat, lon, pitch, qnh, roll, speed, time, \
            timestamp, vsi, windDir, windSpd, lowerNeighbour, higherNeighbour)

        if all(v is None for v in params):
            raise ValueError("Specify at least one parameter to add a new waypoint.")

        altitude = self.__setParam(
            altitude,
            altitude_unit,
            self.DEFAULT_U_ALTITUDE,
            self.U_ALTITUDE
        )
        if altitude is not None:
            self.WPlist[ident]['altitude'] = altitude

        duration = self.__setParam(
            duration,
            duration_unit,
            self.DEFAULT_U_DURATION,
            self.U_DURATION
        )
        if duration is not None:
            self.WPlist[ident]['duration'] = duration

        """
        g = self.__setParam(
            g,
            g_unit,
            self.DEFAULT_U_G,
            self.U_G
        )
        """
        if g is not None:
            self.WPlist[ident]['g'] = g

        heading = self.__setParam(
            heading,
            heading_unit,
            self.DEFAULT_U_HEADING,
            self.U_HEADING
        )
        if heading is not None:
            self.WPlist[ident]['heading'] = heading

        lat = self.__setParam(
            lat,
            lat_unit,
            self.DEFAULT_U_LAT,
            self.U_LAT
        )
        if lat is not None:
            self.WPlist[ident]['lat'] = lat

        lon = self.__setParam(
            lon,
            lon_unit,
            self.DEFAULT_U_LON,
            self.U_LON
        )
        if lon is not None:
            self.WPlist[ident]['lon'] = lon

        pitch = self.__setParam(
            pitch,
            pitch_unit,
            self.DEFAULT_U_PITCH,
            self.U_PITCH
        )
        if pitch is not None:
            self.WPlist[ident]['pitch'] = pitch

        qnh = self.__setParam(
            qnh,
            qnh_unit,
            self.DEFAULT_U_QNH,
            self.U_QNH
        )
        if qnh is not None:
            self.WPlist[ident]['qnh'] = qnh

        roll = self.__setParam(
            roll,
            roll_unit,
            self.DEFAULT_U_ROLL,
            self.U_ROLL
        )
        if roll is not None:
            self.WPlist[ident]['roll'] = roll

        speed = self.__setParam(
            speed,
            speed_unit,
            self.DEFAULT_U_SPEED,
            self.U_SPEED
        )
        if speed is not None:
            self.WPlist[ident]['speed'] = speed

        """
        time = self.__setParam(
            time,
            time_unit,
            self.DEFAULT_U_TIME,
            self.U_TIME
        )
        """
        if time is not None:
            self.WPlist[ident]['time'] = time

        timestamp = self.__setParam(
            timestamp,
            timestamp_unit,
            self.DEFAULT_U_TIMESTAMP,
            self.U_TIMESTAMP
        )
        if timestamp is not None:
            self.WPlist[ident]['timestamp'] = timestamp

        vsi = self.__setParam(
            vsi,
            vsi_unit,
            self.DEFAULT_U_VSI,
            self.U_VSI
        )
        if vsi is not None:
            self.WPlist[ident]['vsi'] = vsi

        windDir = self.__setParam(
            windDir,
            windDir_unit,
            self.DEFAULT_U_WINDDIR,
            self.U_WINDDIR
        )
        if windDir is not None:
            self.WPlist[ident]['windDir'] = windDir

        windSpd = self.__setParam(
            windSpd,
            windSpd_unit,
            self.DEFAULT_U_WINDSPD,
            self.U_WINDSPD
        )
        if windSpd is not None:
            self.WPlist[ident]['windSpd'] = windSpd

        if lowerNeighbour is not None:
            self.WPlist[ident]['lowerNeighbour'] = lowerNeighbour

        if higherNeighbour is not None:
            self.WPlist[ident]['higherNeighbour'] = higherNeighbour

        # Perfom gap filling calculations.
        self.__listOrdered = False
        self.__listCalculated = False
        self.__calculate()


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
            line = []

            line.append("%7.5f" % wp['lat'])
            line.append("%7.5f" % wp['lon'])
            line.append("%7.4f" % wp['altitude'])
            line.append("%4.1f" % wp['speed'])
            line.append(str(wp['time']))
            line.append("%s" % wp['timestamp'])

            if isinstance(wp['lowerNeighbour'], str):
                lNb = wp['lowerNeighbour'][0]
            else:
                lNb = wp['lowerNeighbour']

            if isinstance(wp['higherNeighbour'], str):
                hNb = wp['higherNeighbour'][0]
            else:
                hNb = wp['higherNeighbour']

            line.append("%s, %s" % (lNb, hNb))
            line.append("%s" % wp['duration'])
            return line

        # Prepare table head
        rows = []
        rows.append(['Lat', 'Lon', 'Alt', 'Spd', 'Time', 'Ts', 'Nb', 'Dur'])

        # Parse returned lines. If thereis more then one line, the returned list containes
        # additional listes and needs to be itterated threw.
        ret = self.__iterWPlist(subfunc, ret=True)
        if isinstance(ret[0], list):
            for line in ret:
                rows.append(line)
        else:
            rows.append(ret)

        # Construct table
        tbl = Table(rows)

        # Align columns containing numerical data right.
        for col in (0, 1, 2, 3, 5, 7):
            tbl.justify_columns[col] = 'right'

        # Show table
        print tbl.table + '\n'


    # ---------------------------------------------------------------------------------------------
    # - Waypoint Parameter Handling                                                               -
    # ---------------------------------------------------------------------------------------------


    def __setParam(self, param, unit, default, allowed):

        """
        Check a given parameter for the associated unit and excecute unit conversion if neccessary.
        """

        # Check if parameter is set.
        if param is not None:

            # Check if unit is allowed.
            if unit not in allowed:
                raise ValueError("Unknown unit '%s'!" % unit)

            else:

                # If unit equals default unit return parameter unchanged.
                if unit == default:
                    return param

                else:

                    # Iterate threw allowed units to find matching.
                    for u in allowed:
                        if unit == u:
                            funcName = "%s2%s" % (unit, default)
                            func = getattr(lib.calculations.av_conv, funcName)
                            return func(param)

        # Return None for unset parameter. Just to return something as the params already holds None.
        else:
            return None


    # ---------------------------------------------------------------------------------------------
    # - Calculation methods                                                                       -
    # ---------------------------------------------------------------------------------------------


    def __calculate(self):
        """
        Perform a series of calculatios to fill gaps in the waypoint list. These can be either
        artificial values needed for gauge animations or flight data not provides by GPS.
        """

        self.showWPtable()

        if not self.__listCalculated:
            self.__convertTimestamp()
            self.__orderByParam('timestamp')
            self.__videoTimestamp()
            self.__getNeighbour()
            self.__getDuration()
            self.__listCalculated = True


    def __convertTimestamp(self, epoch=datetime(1970,1,1)):
        """
        Convert datetime.datetime timestamps from GPX into video squence timestamps. Video sequence
        starts at 0 sec.
        """

        def subfunc(wp, epoch):
            t = wp['time']
            ts = wp['timestamp']

            if ts is None:
                td = t - epoch
                ts = td.total_seconds()
                return ('timestamp', ts)

        ret = self.__iterWPlist(subfunc, {'epoch':epoch}, writeChange=True)


    def __getDuration(self):
        """
        Get length of frame. Determine time to next frame.
        This function also adds the length of each GPX frame to the list of track points.
        """

        #~ print "GetDuration"

        def subfunc(wp):
            if wp['higherNeighbour'] == "LAST":
                if wp['duration'] is None:
                    return ('duration', 0.0)
            else:
                myTs = wp['timestamp']
                nextTs = self.getWP(wp['higherNeighbour'], 'index')['timestamp']
                length = nextTs - myTs
                if wp['duration'] != length:
                    return ('duration', length)

        self.__iterWPlist(subfunc, writeChange=True)


    def __getNeighbour(self):
        """
        Iteratre through list of waypoints and get index of both neighbouring waypoints. If it is
        the first waypoint, set lower neighbour to FIRST and if it is last waypoint set higher
        neighbour to LAST.
        """

        #~ print("GetNeighbour")

        def subfunc(wp, i, direction):
            """
            direction expects L or H for lower and higher neighbour.
            """

            if direction == "L":
                if wp['lowerNeighbour'] is None:
                    if i == 0:
                        ret = "FIRST"
                    else:
                        ret = i -1
                    return ('lowerNeighbour', ret)

            elif direction == "H":
                if i == self.getWPListLength() - 1:
                    if wp['higherNeighbour'] != "LAST":
                        return ('higherNeighbour', 'LAST')
                else:
                    ret = i + 1
                    if ret != wp['higherNeighbour']:
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
                #~ print("args: None")
                if passIndex:
                    retVal = func(wp, i)
                else:
                    retVal = func(wp)

            elif isinstance(args, dict):
                #~ print("args: Dict")
                if passIndex:
                    args['i'] = i
                retVal = func(wp, **args)

            elif args is tuple or args is list:
                #~ print("args: Tuple, List")
                if passIndex:
                    args.append(i)
                retVal = func(wp, *args)

            else:
                #~ print("args: else")
                if passIndex:
                    retVal = func(wp, i, args)
                else:
                    retVal = func(wp, args)

            if retVal == "BREAK":
                writeChange = False
                break
            elif retVal == "CONTINUE":
                continue

            if writeChange and retVal is not None:
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

        def calculator(wp, ref):
            ts = wp['timestamp']
            if ts >= ref:
                ts = ts - ref
                return ('timestamp', ts)

        # Check if waypoints are in order. Don't check by which parameter they were ordered.
        # If unordered, order by timestamp.
        if not self.__listOrdered:
            self.__orderByParam('timestamp')

        # Get unix timestamp of first waypoint as reference. This is done only once.
        if self.__refTimestamp is None:
            self.__refTimestamp = self.getWP(0, 'index')['timestamp']

        self.__iterWPlist(calculator, self.__refTimestamp, writeChange=True)


#EOF
