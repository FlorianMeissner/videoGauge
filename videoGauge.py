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

# See TODO.txt


# ABOUT
# =====

# Creator:  Florian Meissner
#           n1990b@gmx.de
# Version:  0.2
# Date:     2017/03/10


# VERSION HISTORY
# ===============

# 0.1:  - Initial Beta
# 0.2:  - Added title centered in console window
#       - Adjusted gauge class calls to new gauge structure
#       - Switched gpxpy from local lib to pypi.


###################################################################################################


# Gauge modules
import gauges

# Own libraries
from lib.calculations.conversions   import colorHex2RGB, splitXY
from lib.Datapoint                  import WP
from lib.myMisc                     import basePath
from lib.terminalSize               import getTerminalSize

# Foreign libraries
import getopt
import gpxpy
import logging                      as log
import os
import shutil
import sys



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
        self.LOG_FORMAT = "%(levelname)s: %(message)s"
        self.LOG_LEVEL = "WARNING"
        self.BASEPATH = basePath(__file__)

        # Start calling methods
        self.__eventlogger()
        self._getCmdParams()
        self.__title()
        self._displayHelp()
        self.__output_folder()
        self._chkMissingParams()
        self._readGPX()
        self._wp.changeWP(1, altitude=1000)
        #~ self._wp.calculate()
        self._runGauges()

        #~ self._wp.showWPtable()

        #~ self.__tmp_folder("delete")
        self.__exit()


    def __exit(self, msg=None, force=False):
        """
        Exiter method
        """

        if msg is None:
            msg = "Done! Exiting..."

        if force:
            log.warning(msg)
            sys.exit(2)
        else:
            log.info(msg)
            sys.exit(0)


    def __eventlogger(self):
        """
        Create eventlogger for application.
        """

        self.logger = log.getLogger()
        self.logHandler = log.StreamHandler(sys.stdout)
        #self.logHandler = log.FileHandler()
        self.logger.addHandler(self.logHandler)
        self._setLogLevel()
        self._setLogFormat()


    def _setLogFormat(self, fmt="DEFAULT"):
        """
        Set fomat of logtext as specified.
        """

        if fmt == "DEFAULT":
            fmt = self.LOG_FORMAT
        self.logHandler.setFormatter(log.Formatter(fmt=fmt))


    def _setLogLevel(self, level="DEFAULT"):
        """
        DESCRIPTION_MISSING
        """

        if level == "DEFAULT":
            level = self.LOG_LEVEL
        self.logger.setLevel(level.upper())


    def __title(self):
        """
        Show title
        """

        self._setLogFormat("%(message)s")

        x, y = getTerminalSize()
        name = "Video Gauge Creator"
        spaces = (x - len(name) - 2) / 2
        x2 = spaces * 2 + len(name) + 2
        log.critical("*" * x2)
        log.critical("*" + " " * (x2-2) + "*")
        log.critical("*" + " " * spaces + name + spaces * " " + "*")
        log.critical("*" + " " * (x2-2) + "*")
        log.critical("*" * x2)
        log.critical("\n")

        self._setLogFormat()


    # ---------------------------------------------------------------------------------------------
    # - Parameter handling                                                                        -
    # ---------------------------------------------------------------------------------------------


    def _getCmdParams(self):
        """
        Get all commandline parameters. Function holds a list of default values for each parameter
        which will be overridden by command line. Required parameters hold default value "None".
        """

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
            self.__exit(str(err), True)
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
                    self._setLogLevel('INFO')

                # Quiet mode
                elif opt == "-q":
                    quiet = True
                    verbose = False
                    force = True
                    self._setLogLevel('CRITICAL')

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


    def _chkMissingParams(self):
        """
        Check for missing but required parameters from the command line.  A missing parameter is
        expected to hold default value "None".
        """

        count = 0
        for opt, arg in self.params.items():
            if arg is None:
                log.error("Required parameter \"%s\" is missing!" % opt)
                count+=1
        if count > 0:
            self.__exit("Check \"%s --help\" for further information." % sys.argv[0], True)


    def _runGauges(self):
        """
        Run class handler method for wated gauges.
        """

        # Control variable
        run_something = False

        # Airspeed indicator
        if self.params['airspeed']['display']:
            if self.params['airspeed']['unit'] in ("mph", "kt", "kmh"):
                self._airspeed()
                run_something = True
            else:
                log.warning("Unknown unit \"%s\" for 'airspeed'!" % self.params['airspeed']['unit'])

        # Altitude indicator
        if self.params['altitude']['display']:
            if self.params['altitude']['unit'] in ("ft", "m"):
                self._altitude()
                run_something = True
            else:
                log.warning("Unknown unit \"%s\" for 'altitude'!" % self.params['altitude']['unit'])

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
                log.warning("Unknown unit \"%s\" for 'vsi'!" % self.params['vsi']['unit'])

        # Check if at least one gauge was selected.
        if not run_something:
            log.warning("No gauge selected and no output produced!")


    # ---------------------------------------------------------------------------------------------
    # - Help text                                                                                 -
    # ---------------------------------------------------------------------------------------------


    def _displayHelp(self):
        """
        Display Help-text and terminate program.
        """

        if self.params["displayHelp"]:
            self._setLogFormat("%(message)s")
            log.critical("Help!!")
            self.__exit()


    # ---------------------------------------------------------------------------------------------
    # - GPX                                                                                       -
    # ---------------------------------------------------------------------------------------------


    def _readGPX(self):
        """
        Read given GPX file and extract trackpoints.
        """

        gpxfile = open(self.params['gpxfile'], 'r')
        gpx = gpxpy.parse(gpxfile, version='1.0')   # Even though that SkyDemon marks its GPX files
                                                    # as version 1.1, the trackpoints do include
                                                    # <speed></speed> which is only available in
                                                    # V1.0. Because GPXPy would parse the files
                                                    # header, it need to be forced to read in 1.0.
        self.trkPts = []

        # Construct Waypoit class
        self._wp = WP()

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
                    self._wp.addWP(lat=point.latitude, lon=point.longitude, altitude=point.elevation, \
                        speed=point.speed, time=point.time)


    # ---------------------------------------------------------------------------------------------
    # - Call of gauge classes                                                                     -
    # ---------------------------------------------------------------------------------------------


    def _airspeed(self):
        """
        Handle class operation for airspeed indicator.
        """

        params = self.params['airspeed']
        gauge = gauges.Airspeed.Airspeed(
            self.trkPts,
            self._wp,
            unit=params['unit'],
            digSpeed=False,
            autorun=False,
            settings=self.VIDEOSETTINGS
        )

        """
        # Background color
        r, g, b = colorHex2RGB(params['bg'])
        gauge.setBackground(r, g, b)

        # Position
        gauge.setPosition(splitXY(params['position']))

        # Size
        w, h = splitXY(params['size'])
        gauge.setSize(w, h)
        """

        clip = gauge.make()

        filename  = self.params['outputfolder']
        filename += "airspeed"
        filename += self.VIDEOSETTINGS['filetype']

        gauge.save(clip, filename)


    def _altitude(self):
        """
        Handle class operation for altitude indicator.
        """

        log.warning("Altitude indicator will be added later!")


    def _attitude(self):
        """
        Handle class operation for attitude indicator.
        """

        log.warning("Attitude indicator will be added later!")


    def _compass(self):
        """
        Handle class operation for compass.
        """

        log.warning("Compass will be added later!")


    def _g_meter(self):
        """
        Handle class operation for G-Meter.
        """

        log.warning("G-Meter will be added later!")


    def _vsi(self):
        """
        Handle class operation for vertical speed indicator.
        """

        log.warning("Vertical speed indicator will be added later!")


    # ---------------------------------------------------------------------------------------------
    # - Other stuff                                                                               -
    # ---------------------------------------------------------------------------------------------


    def __output_folder(self):
        """
        Handle output folder for video files.
        """

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
                self.__exit("Aborted by user...")

        # Create new folder.
        os.mkdir(self.params['outputfolder'])



# *************************************************************************************************
# * Run app                                                                                       *
# *************************************************************************************************

if __name__ == "__main__":
    try:
        app = VideoGauge()
    except KeyboardInterrupt:
        print("\nERROR: Aborted by user with Keyboard Interrupt!")
        sys.exit(2)


# EOF
