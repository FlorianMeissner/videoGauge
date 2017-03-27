#!/usr/bin/env python3

# *****************************************************************************
# * Video Gauge Creator                                                       *
# *****************************************************************************


# Description
# ===========

# Video Gauge Creator is build to enhance aviation videos by overlaying them
# with mock up gauges showing several airplane parameters. Therefore the
# software expects a GPX file containing GPS data to the flight. It outputs an
# MP4 video stream of the hole duration of the GPX track containing the
# configured gauges on a transparent background show the data of the GPX file.
# More gauges will be added in the future.


# TODO
# ====

# See TODO.txt


# DEPENDENCIES
# ============

# Python 2.7
# PIP terminaltables
#     gpxpy
#     moviepy
#     Pillow


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


###############################################################################


# Gauge modules
import gauges

# Own libraries
from lib.calculations.gui_conv  import colorHex2RGB, splitXY
from lib.Datapoint              import WP
from lib.myMisc                 import basePath
from lib.terminalSize           import getTerminalSize

# Foreign libraries
import getopt
import gpxpy
import logging                  as log
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
        self.LOG_FORMAT = "%(levelname)s: %(message)s"
        self.LOG_LEVEL = "WARNING"
        self.BASEPATH = basePath(__file__)

        # Construct Waypoint class
        self._wp = WP()

        # Start calling methods
        self.__eventlogger()
        self._getCmdParams()
        self.__title()
        self._displayHelp()
        self.__output_folder()
        self._chkMissingParams()
        self._readGPX()
        #~ self._wp.changeWP(1, altitude=1000, altitude_unit=self._wp.U_M)
        self._wp.changeWP(1, altitude=1000)
        self._runGauges()

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


    # -------------------------------------------------------------------------
    # - Parameter handling                                                    -
    # -------------------------------------------------------------------------


    def _getCmdParams(self):
        """
        Get all commandline parameters. Function holds a list of default values
        for each parameter which will be overridden by command line. Required
        parameters hold default value "None".
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



        # Define string with short options. Colon used when parameter is
        # expected.
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

        # Parse arguemnts. "opts" contains recognised parameters. "args"
        # contains unrecognized ones.
        try:
            opts, args = getopt.getopt(sys.argv[1:], options, long_options)
        except getopt.GetoptError as err:
            self.__exit(str(err), True)
        else:

            # Parse recognized arguments and overwrite default parameters
            for opt, arg in opts:

                # display help
                if opt in ("-h", "--help"):
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
        Check for missing but required parameters from the command line. A
        missing parameter is expected to hold default value "None".
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


    # -------------------------------------------------------------------------
    # - Help text                                                             -
    # -------------------------------------------------------------------------


    def _displayHelp(self):
        """
        Display Help-text and terminate program.
        """

        def linewrapper(arg, helptxt, indent=25):
            """
            Breakes lines at the right border of the terminal and continue in
            the next line with the specified indent.
            """

            # Add colon to argument and wrap line instantly if argument is
            # longer than indent. In this case fill new line with indent amount
            # of whitespaces. If argument is shorter than indent, fill up
            # argument with whitespace up to indent length.
            arg += ": "
            if len(arg) > indent:
                arg = arg + "\n" + " " * indent
            else:
                arg = arg + " " * (indent - len(arg))

            # Iterate threw each word of the help text. If length of line will
            # go beyound terminal size, wrap line and fill with indent amount
            # of whitespaces, then continue text.
            linelen = 0
            width, hight = getTerminalSize()
            txt = ""
            for word in helptxt.split():
                word += " "
                if linelen + len(word) < width - indent:
                    txt += word
                    linelen += len(word)
                else:
                    txt += "\n"
                    txt  = txt + " " * indent
                    txt += word
                    linelen = len(word)

            return arg + txt + "\n"

        h  = "usage: videogauge [--help | -h]\n"
        h += "                  [--version]\n"
        h += "                  -g | --gpxfile FILE\n"
        h += "                  [-o | --outputfolder PATH]\n"
        h += "                  [-f] [-v] [-q]\n"
        h += "                  [--airspeed UNIT]\n"
        h += "                  [--airspeed-size WIDTHxHEIGHT]\n"
        h += "                  [--airspeed-position POSXxPOSY]\n"
        h += "                  [--airspeed-background HEXRGB]\n"
        h += "                  [--airspeed-outputfile FILE]\n"
        #~ h += "                  [--altitude UNIT]\n"
        #~ h += "                  [--altitude-size WIDTHxHEIGHT]\n"
        #~ h += "                  [--altitude-position POSXxPOSY]\n"
        #~ h += "                  [--altitude-background HEXRGB]\n"
        #~ h += "                  [--altitude-outputfile FILE]\n"
        #~ h += "                  [--attitude]\n"
        #~ h += "                  [--attitude-size WIDTHxHEIGHT]\n"
        #~ h += "                  [--attitude-position POSXxPOSY]\n"
        #~ h += "                  [--attitude-background HEXRGB]\n"
        #~ h += "                  [--attitude-outputfile FILE]\n"
        #~ h += "                  [--compass]\n"
        #~ h += "                  [--compass-size WIDTHxHEIGHT]\n"
        #~ h += "                  [--compass-position POSXxPOSY]\n"
        #~ h += "                  [--compass-background HEXRGB]\n"
        #~ h += "                  [--compass-outputfile FILE]\n"
        #~ h += "                  [--gmeter]\n"
        #~ h += "                  [--gmeter-size WIDTHxHEIGHT]\n"
        #~ h += "                  [--gmeter-position POSXxPOSY]\n"
        #~ h += "                  [--gmeter-background HEXRGB]\n"
        #~ h += "                  [--gmeter-outputfile FILE]\n"
        #~ h += "                  [--gyro]\n"
        #~ h += "                  [--gyro-size WIDTHxHEIGHT]\n"
        #~ h += "                  [--gyro-position POSXxPOSY]\n"
        #~ h += "                  [--gyro-background HEXRGB]\n"
        #~ h += "                  [--gyro-outputfile FILE]\n"
        #~ h += "                  [--rpm]\n"
        #~ h += "                  [--rpm-size WIDTHxHEIGHT]\n"
        #~ h += "                  [--rpm-position POSXxPOSY]\n"
        #~ h += "                  [--rpm-background HEXRGB]\n"
        #~ h += "                  [--rpm-outputfile FILE]\n"
        #~ h += "                  [--vsi UNIT]\n"
        #~ h += "                  [--vsi-size WIDTHxHEIGHT]\n"
        #~ h += "                  [--vsi-position POSXxPOSY]\n"
        #~ h += "                  [--vsi-background HEXRGB]\n"
        #~ h += "                  [--vsi-outputfile FILE]\n"
        h += "\n"
        h += "Control arguments:\n"
        h += linewrapper("-h | --help",
            "Show this help text.")
        h += linewrapper("--version",
            "Show the version of this program as wellas the versions of each \
            gauge.")
        h += linewrapper("-g | --gpxfile FILE",
            "Specify the GPX file acting as data source. Provide either \
            absolute or relative path.")
        h += linewrapper("-o | --outputfolder PATH",
            "Specify the output path for the created video files here. Provide \
            either relative or absolute path. Do not add a filename! \
            DEFAULT: Present working directory.")
        h += linewrapper("-f",
            "Force overwriting existing files.")
        h += linewrapper("-v",
            "Verbose mode. Shows tables with parsed waypointsfrom GPX file.")
        h += linewrapper("-q",
            "Quiet mode. Reduces output to a minimum. Implies -f.")
        h += "\n"
        h += "Airspeed indicator:\n"
        h += linewrapper("--airspeed UNIT",
            "Airspeed indicator will only be shown if this argument is passed. \
            UNIT can be either of kt, mph.")
        h += linewrapper("--airspeed-size WIDTHxHEIGHT",
            "Define size of airspeed indicator in pixels. DEFAULT: %s" %
            self.params['airspeed']['size'])
        h += linewrapper("--airspeed-position POSXxPOSY",
            "Define position of gauge in video. DEFAULT: %s" %
            self.params['airspeed']['position'])
        h += linewrapper("--airspeed-background HEXRGB",
            "Define background color as HTML RGB hex code. DEFAULT: %s" %
            self.params['airspeed']['bg'])
        h += linewrapper("--airspeed-outputfile FILE",
            "Specify a filename for the output file. The file will be saved relative to the path specified in --outputfolder. File extension must be *.mp4.")
        """
        h += linewrapper("--altitude UNIT",
            "")
        h += linewrapper("--altitude-size WIDTHxHEIGHT",
            "")
        h += linewrapper("--altitude-position POSXxPOSY",
            "")
        h += linewrapper("--altitude-background HEXRGB",
            "")
        h += linewrapper("--altitude-outputfile FILE",
            "")
        h += linewrapper("--attitude",
            "")
        h += linewrapper("--attitude-size WIDTHxHEIGHT",
            "")
        h += linewrapper("--attitude-position POSXxPOSY",
            "")
        h += linewrapper("--attitude-background HEXRGB",
            "")
        h += linewrapper("--attitude-outputfile FILE",
            "")
        h += linewrapper("--compass",
            "")
        h += linewrapper("--compass-size WIDTHxHEIGHT",
            "")
        h += linewrapper("--compass-position POSXxPOSY",
            "")
        h += linewrapper("--compass-background HEXRGB",
            "")
        h += linewrapper("--compass-outputfile FILE",
            "")
        h += linewrapper("--gmeter",
            "")
        h += linewrapper("--gmeter-size WIDTHxHEIGHT",
            "")
        h += linewrapper("--gmeter-position POSXxPOSY",
            "")
        h += linewrapper("--gmeter-background HEXRGB",
            "")
        h += linewrapper("--gmeter-outputfile FILE",
            "")
        h += linewrapper("--gyro",
            "")
        h += linewrapper("--gyro-size WIDTHxHEIGHT",
            "")
        h += linewrapper("--gyro-position POSXxPOSY",
            "")
        h += linewrapper("--gyro-background HEXRGB",
            "")
        h += linewrapper("--gyro-outputfile FILE",
            "")
        h += linewrapper("--rpm",
            "")
        h += linewrapper("--rpm-size WIDTHxHEIGHT",
            "")
        h += linewrapper("--rpm-position POSXxPOSY",
            "")
        h += linewrapper("--rpm-background HEXRGB",
            "")
        h += linewrapper("--rpm-outputfile FILE",
            "")
        h += linewrapper("--vsi UNIT",
            "")
        h += linewrapper("--vsi-size WIDTHxHEIGHT",
            "")
        h += linewrapper("--vsi-position POSXxPOSY",
            "")
        h += linewrapper("--vsi-background HEXRGB",
            "")
        h += linewrapper("--vsi-outputfile FILE",
            "")
        """

        if self.params["displayHelp"]:
            self._setLogFormat("%(message)s")
            log.critical(h)
            self.__exit()


    # -------------------------------------------------------------------------
    # - GPX                                                                   -
    # -------------------------------------------------------------------------


    def _readGPX(self):
        """
        Read given GPX file and extract trackpoints.
        """

        log.info("Reading GPX file. This may take a few seconds...")

        gpxfile = open(self.params['gpxfile'], 'r')
        gpx = gpxpy.parse(gpxfile, version='1.0')   # Even though that SkyDemon
                                                    # marks its GPX files as
                                                    # version 1.1, the
                                                    # trackpoints do include
                                                    # <speed></speed> which is
                                                    # only available in V1.0.
                                                    # Because GPXPy would parse
                                                    # the files header, it need
                                                    # to be forced to read in
                                                    # 1.0.

        # Parse tracks.
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    self._wp.addWP(
                        lat=point.latitude, lat_unit=self._wp.U_DEG, \
                        lon=point.longitude, lon_unit=self._wp.U_DEG, \
                        altitude=point.elevation, altitude_unit=self._wp.U_M, \
                        speed=point.speed, speed_unit=self._wp.U_MS, \
                        time=point.time
                    )
        self._wp.showWPtable()


    # -------------------------------------------------------------------------
    # - Call of gauge classes                                                 -
    # -------------------------------------------------------------------------


    def _airspeed(self):
        """
        Handle class operation for airspeed indicator.
        """

        params = self.params['airspeed']
        gauge = gauges.Airspeed.Airspeed(
            wpInst=self._wp,
            unit=params['unit'],
            digSpeed=False,
            autorun=False,
            settings=self.VIDEOSETTINGS
        )

        gauge.setSize(xy=params['size'])


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


    # -------------------------------------------------------------------------
    # - Other stuff                                                           -
    # -------------------------------------------------------------------------


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



# *****************************************************************************
# * Run app                                                                   *
# *****************************************************************************

if __name__ == "__main__":
    try:
        app = VideoGauge()
    except KeyboardInterrupt:
        print("\nERROR: Aborted by user with Keyboard Interrupt!")
        sys.exit(2)


# EOF
