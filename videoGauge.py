#!/usr/bin/env python3

# *************************************************************************************************
# * Video Gauge Creator                                                                           *
# *************************************************************************************************


# Description
# ===========

# Video Gauge Creator is build to enhance aviation videos by overlaying them with mock up gauges
# showing several airplane parameters. Therefore the software expects a GPX file containing GPS data
# to the flight. It outputs an MP4 video stream of the hole duration of the GPX track containing
# the configured gauges on a transparent background show the data of the GPX file. More gauges will
# be added in the future.


# TODO
# ====

# - Add PA28 airspeed indicator
# - Add G-Meter
# - Add altimeter


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


import os
import shutil
import sys
import getopt
from lib import gpxpy
from gauges.airspeed_luscombe_mph import AirspeedLuscombeMPH
from lib.calculations.conversions import colorHex2RGB, splitXY


class VideoGauge(object):

    def __init__(self):

        # Constants
        self.VIDEOSETTINGS = {
                                "codec"             :   "mpeg4",
                                "filetype"          :   ".mp4",
                                "framerate"         :   24,
                                "audio"             :   False,
                                "ffmpeg_preset"     :   "ultrafast",
                                "ffmpeg_threads"    :   8,
                                "format"            :   "1280x720"
                             }
        self.TMP_FOLDER = "videoGauge_tmp/"

        # Start calling methods
        self.__basepath()
        self._getCmdParams()

        self.__print("***********************")
        self.__print("* Video Gauge Creator *")
        self.__print("***********************")
        self.__print("")

        self._displayHelp()
        self.__tmp_folder("add")
        self.__output_folder()
        self._chkMissingParams()
        self._readGPX()
        self._convertTimestamp()
        self._getFrameLength()
        self._printTrkPts()
        self._runGauges()

        self.__tmp_folder("delete")
        self.__print("Done! Exiting...")


    # ---------------------------------------------------------------------------------------------
    # - Parameter handling                                                                        -
    # ---------------------------------------------------------------------------------------------


    # Get all commandline parameters. Function holds a list of default values for each parameter
    # which will be overridden by command line. Required parameters hold default value "None".
    def _getCmdParams(self):

        # Set Default parameters.
        displayHelp = False

        gpxfile = None
        outputfolder = "Gauges/"
        force = False

        quiet = False
        verbose = False

        airspeed = {
                        "display"   :   False,
                        "size"      :   "200x200",
                        "position"  :   "0x520",
                        "unit"      :   None,
                        "bg"        :   "#0000FF"
                    }

        altitude =  {
                        "display"   :   False,
                        "size"      :   "200x200",
                        "position"  :   "200x520",
                        "unit"      :   None,
                        "bg"        :   "#0000FF"
                    }


        attitude =  {
                        "display"   :   False,
                        "size"      :   "200x200",
                        "position"  :   "400x520",
                        "bg"        :   "#0000FF"
                    }


        compass =   {
                        "display"   :   False,
                        "size"      :   "200x200",
                        "position"  :   "600x520",
                        "bg"        :   "#0000FF"
                    }


        g_meter =   {
                        "display"   :   False,
                        "size"      :   "200x200",
                        "position"  :   "800x520",
                        "bg"        :   "#0000FF"
                    }


        vsi =       {
                        "display"   :   False,
                        "size"      :   "200x200",
                        "position"  :   "1000x520",
                        "unit"      :   None,
                        "bg"        :   "#0000FF"
                    }



        # Define string with short options. Colon used when parameter is expected.
        options  = ""
        options += "h"  # Display help
        options += "g:" # Input GPX file
        options += "o:" # Output video folder
        options += "f"  # Force to overwrite existing files
        options += "v"  # Verbose
        options += "q"  # Quiet

        # Define list with long options.
        long_options = [
                        "help",
                        "gpxfile=",
                        "outputfolder=",

                        "airspeed=",
                        "airspeed-size=",
                        "airspeed-position=",
                        "airspeed-background=",
                        "airspeed-outputfile=",

                        "altitude=",
                        "altitude-size=",
                        "altitude-position=",
                        "altitude-background=",
                        "altitude-outputfile=",

                        "attitude",
                        "attitude-size=",
                        "attitude-position=",
                        "attitude-background=",
                        "attitude-outputfile=",

                        "compass",
                        "compass-size=",
                        "compass-position=",
                        "compass-background=",
                        "compass-outputfile=",

                        "gmeter",
                        "gmeter-size=",
                        "gmeter-position=",
                        "gmeter-background=",
                        "gmeter-outputfile=",

                        "vsi=",
                        "vsi-size=",
                        "vsi-position=",
                        "vsi-background=",
                        "vsi-outputfile="
                       ]

        # Parse arguemnts. "opts" contains recognised parameters. "args" contains unrecognized ones.
        try:
            opts, args = getopt.getopt(sys.argv[1:], options, long_options)
        except getopt.GetoptError as err:
            self.__print(str(err))
            sys.exit(2)
        else:

            # Parse recognized arguments and overwrite default parameters
            for opt, arg in opts:

                # display help
                if opt == "-h":
                    displayHelp = True

                # GPX input file
                elif opt in ("-g", "--gpxfile"):
                    gpxfile = arg

                # Video outputfile
                elif opt in ("-o", "--outputfolder"):
                    if arg[:-1] != "/":
                        arg += "/"
                    outputfolder = arg

                # Force overwrite
                elif opt == "-f":
                    force = True

                # Airspeed indicator settings
                elif opt == "--airspeed":
                    airspeed['display'] = True
                    airspeed['unit'] = arg
                elif opt == "--airspeed-size":
                    airspeed['size'] = arg
                elif opt == "--airspeed-position":
                    airspeed['position'] = arg
                elif opt == "--airspeed-background":
                    airspeed['bg'] = arg
                elif opt == "--airspeed-outputfile":
                    airspeed['output'] = arg

                # Altitude indicator settings
                elif opt == "--altitude":
                    altitude['display'] = True
                    altitude['unit'] = arg
                elif opt == "--altitude-size":
                    altitude['size'] = arg
                elif opt == "--altitude-position":
                    altitude['position'] = arg
                elif opt == "--altitude-background":
                    altitude['bg'] = arg
                elif opt == "--altitude-outputfile":
                    altitude['output'] = arg

                # Attitude indicator settings
                elif opt == "--attitude":
                    attitude['display'] = True
                elif opt == "--attitude-size":
                    attitude['size'] = arg
                elif opt == "--attitude-position":
                    attitude['position'] = arg
                elif opt == "--attitude-background":
                    attitude['bg'] = arg
                elif opt == "--attitude-outputfile":
                    attitude['output'] = arg

                # Compass settings
                elif opt == "--compass":
                    compass['display'] = True
                elif opt == "--compass-size":
                    compass['size'] = arg
                elif opt == "--compass-position":
                    compass['position'] = arg
                elif opt == "--compass-background":
                    compass['bg'] = arg
                elif opt == "--compass-outputfile":
                    compass['output'] = arg

                # G-Meter settings
                elif opt == "--gmeter":
                    g_meter['display'] = True
                elif opt == "--g_meter-size":
                    g_meter['size'] = arg
                elif opt == "--g_meter-position":
                    g_meter['position'] = arg
                elif opt == "--g_meter-background":
                    g_meter['bg'] = arg
                elif opt == "--g_meter-outputfile":
                    g_meter['output'] = arg

                # Vertical speed indicator settings
                elif opt == "--vsi":
                    vsi['display'] = True
                    vsi['unit'] = arg
                elif opt == "--vsi-size":
                    vsi['size'] = arg
                elif opt == "--vsi-position":
                    vsi['position'] = arg
                elif opt == "--vsi-background":
                    vsi['bg'] = arg
                elif opt == "--vsi-outputfile":
                    vsi['output'] = arg

                # Verbose mode
                elif opt == "-v":
                    verbose = True
                    quiet = False

                # Quiet mode
                elif opt == "-q":
                    quiet = True
                    verbose = False
                    force = True

            # Transfor parameters into public dictionary.
            self.params = { "gpxfile"       :   gpxfile,
                            "outputfolder"  :   outputfolder,
                            "force"         :   force,
                            "displayHelp"   :   displayHelp,
                            "airspeed"      :   airspeed,
                            "altitude"      :   altitude,
                            "attitude"      :   attitude,
                            "compass"       :   compass,
                            "g_meter"       :   g_meter,
                            "vsi"           :   vsi,
                            "verbose"       :   verbose,
                            "quiet"         :   quiet
                          }


    # Check for missing but required parameters from the command line.  A missing parameter is
    # expected to hold default value "None".
    def _chkMissingParams(self):
        count = 0
        for opt, arg in self.params.items():
            if arg is None:
                self.__print("ERROR: Required parameter \"%s\" is missing!" % opt)
                count+=1
        if count > 0:
            self.__print("Check \"%s --help\" for further information." % sys.argv[0])
            sys.exit(2)


    # Run class handler method for wated gauges.
    def _runGauges(self):

        # Control variable
        run_something = False

        # Airspeed indicator
        if self.params['airspeed']['display']:
            if self.params['airspeed']['unit'] in ("mph", "kt", "kmh"):
                self._airspeed()
                run_something = True
            else:
                self.__print("WARNING. Unknown unit \"%s\" for 'airspeed'!" % self.params['airspeed']['unit'])

        # Altitude indicator
        if self.params['altitude']['display']:
            if self.params['altitude']['unit'] in ("ft", "m"):
                self._altitude()
                run_something = True
            else:
                self.__print("WARNING. Unknown unit \"%s\" for 'altitude'!" % self.params['altitude']['unit'])

        # Attitude indicator
        if self.params['attitude']['display']:
            self._attitude()
            run_something = True

        # Compass
        if self.params['compass']['display']:
            self._compass()
            run_something = True

        # G-Meter
        if self.params['g_meter']['display']:
            self._g_meter()
            run_something = True

        # Vertical speed indicator
        if self.params['vsi']['display']:
            if self.params['vsi']['unit'] in ("ftmin", "ms"):
                self._vsi()
                run_something = True
            else:
                self.__print("WARNING. Unknown unit \"%s\" for 'vsi'!" % self.params['vsi']['unit'])

        # Check if at least one gauge was selected.
        if not run_something:
            self.__print("WARNING: No gauge selected and no output produced!")


    # ---------------------------------------------------------------------------------------------
    # - Help text                                                                                 -
    # ---------------------------------------------------------------------------------------------


    # Display Help-text and terminate program.
    def _displayHelp(self):
        if self.params["displayHelp"]:
            self.__print("Help!!")
            sys.exit(0)


    # ---------------------------------------------------------------------------------------------
    # - GPX                                                                                       -
    # ---------------------------------------------------------------------------------------------


    # Read given GPX file and extract trackpoints.
    def _readGPX(self):
        gpxfile = open(self.params['gpxfile'], 'r')
        gpx = gpxpy.parse(gpxfile, version='1.0')
        self.trkPts = []

        # Parse tracks.
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    trkPt = {'lat'   : point.latitude,
                             'lon'   : point.longitude,
                             'alt'   : point.elevation,
                             'speed' : point.speed,
                             'time'  : point.time}
                    self.trkPts.append(trkPt)


    # Print table with trackpoints.
    def _printTrkPts(self):

        # Prepare table head
        self.__print(" Latitude | Longitude | Altitude | Speed | Time ", v=True)
        self.__print("----------+-----------+----------+-------+------", v=True)
        self.__print("          |           |          |       |      ", v=True)
        #           9       9           8           5       4

        for trkPt in self.trkPts:
            # Print table with trackpoints.
            string = " "

            if trkPt['lat'] < 10:
                string += " %7.5f | " % trkPt['lat']
            else:
                string += "%7.5f | " % trkPt['lat']

            if trkPt['lon'] < 10:
                string += "  %7.5f | " % trkPt['lon']
            elif trkPt['lon'] < 100:
                string += " %7.5f | " % trkPt['lon']
            else:
                string += "%7.5f | " % trkPt['lon']

            if trkPt['alt'] < 10:
                string += "  %7.4f | " % trkPt['alt']
            elif trkPt['alt'] < 100:
                string += " %7.4f | " % trkPt['alt']
            else:
                string += "%7.4f | " % trkPt['alt']

            if trkPt['speed'] < 10:
                string += " %4.1f | " % trkPt['speed']
            elif trkPt['speed'] < 100:
                string += " %4.1f | " % trkPt['speed']
            else:
                string += "%4.1f | " % trkPt['speed']

            string += str(trkPt['time'])
            self.__print(string, v=True)


    # Convert datetime.datetime timestamps from GPX into video squence timestamps. Video sququence
    # starts at 0 sec.
    def _convertTimestamp(self):
        beginning = 0
        for trkPt in self.trkPts:

            # Get key of track point.
            key = self.trkPts.index(trkPt)

            # Calculate timestamp. First second of video will be 0.
            year   = trkPt['time'].year
            month  = trkPt['time'].month
            day    = trkPt['time'].day
            hour   = trkPt['time'].hour
            minute = trkPt['time'].minute
            second = trkPt['time'].second

            timestamp  = second
            timestamp += minute * 60
            timestamp += hour * 3600
            timestamp += day * 86400

            # If it is the first track point, save time as reference.
            if beginning == 0:
                beginning = timestamp

            # Subtract track points timestamp from reference to get elapsed seconds since track
            # started.
            timestamp = timestamp - beginning

            # Write timestamp to track points list.
            self.trkPts[key]['timestamp'] = timestamp


    # Get length of frame. Determine time to next frame.
    # This function also adds the length of each GPX frame to the list of track points.
    def _getFrameLength(self):
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


    # ---------------------------------------------------------------------------------------------
    # - Airspeed indicator                                                                        -
    # ---------------------------------------------------------------------------------------------


    # Handle class operation for airspeed indicator.
    def _airspeed(self):
        params = self.params['airspeed']
        gauge = AirspeedLuscombeMPH(self, autorun=False)

        # Background color
        r, g, b = colorHex2RGB(params['bg'])
        gauge.setBackground(r, g, b)

        # Position
        gauge.setPosition(splitXY(params['position']))

        # Size
        w, h = splitXY(params['size'])
        gauge.setSize(w, h)

        gauge.make()


    # ---------------------------------------------------------------------------------------------
    # - Altitude indicator                                                                        -
    # ---------------------------------------------------------------------------------------------


    # Handle class operation for altitude indicator.
    def _altitude(self):
        self.__print("Warning: Altitude indicator will be added later!")


    # ---------------------------------------------------------------------------------------------
    # - Attitude indicator                                                                        -
    # ---------------------------------------------------------------------------------------------


    # Handle class operation for attitude indicator.
    def _attitude(self):
        self.__print("Warning: Attitude indicator will be added later!")


    # ---------------------------------------------------------------------------------------------
    # - Compass                                                                                   -
    # ---------------------------------------------------------------------------------------------


    # Handle class operation for compass.
    def _compass(self):
        self.__print("Warning: Compass will be added later!")


    # ---------------------------------------------------------------------------------------------
    # - G-Meter                                                                                   -
    # ---------------------------------------------------------------------------------------------


    # Handle class operation for G-Meter.
    def _g_meter(self):
        self.__print("Warning: G-Meter will be added later!")


    # ---------------------------------------------------------------------------------------------
    # - Vertical speed indicator                                                                  -
    # ---------------------------------------------------------------------------------------------


    # Handle class operation for vertical speed indicator.
    def _vsi(self):
        self.__print("Warning: Vertical speed indicator will be added later!")


    # ---------------------------------------------------------------------------------------------
    # - Other stuff                                                                               -
    # ---------------------------------------------------------------------------------------------


    # Helper method to print messages. 'v' triggers messages only to be displayed in verbose mode.
    def __print(self, msg, v=False):
        if self.params['verbose'] and v:
            print(msg, "verbose")
        elif not self.params['quiet'] and not v:
            print(msg)


    # Determine original path of the script.
    def __basepath(self):
        self.basePath = os.path.dirname(os.path.realpath(__file__))
        if self.basePath[:-1] != "/":
            self.basePath += "/"
        print self.basePath


    # Handle output folder for video files.
    def __output_folder(self):
        if os.path.isdir(self.params['outputfolder']):

            a = "no"

            # In quiet mode force to overwrite.
            if not self.params['force']:
                # If folder exists ask user to overwrite.
                q  = "The outputfolder '%s' already exists. "
                q += "All gauge animations in there will be overridden. "
                q += "Continue? (Y/n): "
                a = raw_input(q % self.params['outputfolder'])

            if a.lower() in ("", "y", "yes") or self.params['force']:
                shutil.rmtree(self.params['outputfolder'])
            else:
                self.__print("Aborted by user...")
                sys.exit(0)

        # Create new folder.
        os.mkdir(self.params['outputfolder'])

    # Handle folder for temporary files.
    def __tmp_folder(self, action):
        if action == "add":
            if os.path.isdir(self.TMP_FOLDER):
                shutil.rmtree(self.TMP_FOLDER)
            os.mkdir(self.TMP_FOLDER)
        elif action == "delete":
            shutil.rmtree(self.TMP_FOLDER)
        else:
            raise ValueError("Unknown action '%s'." % action)



# *************************************************************************************************
# * Run app                                                                                       *
# *************************************************************************************************

if __name__ == "__main__":
    app = VideoGauge()


# EOF
