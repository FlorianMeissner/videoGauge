#!/usr/bin/env python3

# *************************************************************************************************
# * Airspeed Indicator Luscombe Style MPH                                                         *
# *************************************************************************************************


# Description
# ===========

# Airspeed indicator in old Luscombe style for Video Gauge Creator. Indicating in MPH.


# TODO
# ====

# - Implement smooth needle rotation.


# ABOUT
# =====

# Creator:  Florian Meissner
#           n1990b@gmx.de
# Version:  0.2
# Date:     2017/02/21


# VERSION HISTORY
# ===============

# 0.1:  - Initial Beta
# 0.2:  - Implemented base class for all gauges.
#       - Moved file out of template folder
#       - Rework interfaces to better split between gauge class


###################################################################################################


# Gauge modules
import airspeed
import BaseGauge

# Own library modules
from lib.calculations       import conversions
from lib.calculations       import interpolation
from lib.myMisc             import lookahead

# Foreign libraries
from PIL                    import Image
import moviepy.editor       as mpy


class Airspeed(BaseGauge.BaseGauge):


    def __init__(self, points, unit, digSpeed=False, autorun=False, settings=None):

        # Base class constructor
        BaseGauge.BaseGauge.__init__(self)

        # Variables
        self.DigSpeed   =   digSpeed    # Show digital speed number in upper left corner.
        self.Settings   =   settings    # Video settings
        self.Speeds     =   []          # List with speeds from track point list. Populated by
                                        # self.__convert().

        # Initializing methods
        self.__parse_unit(unit)
        self.__parse_speeds(points)


        # If autorun is enabled, video animation will be written to disk immediately after gathering
        # all data.
        if autorun:
            clip = self.make()
            self.save(clip, "output.mp4")


    def __parse_unit(self, unit):

        unit = unit.lower()
        self.Unit = unit

        # Set pathes for graphics
        prefix = self.BASEPATH + "airspeed/" + unit + "_"
        self.setNeedle(prefix + "needle2.png")
        self.setFaceplate(prefix + "faceplate.png")

        # Get calibration table.
        # self.calibrator will hold the imported module named like the passed unit.
        self.calibrator = getattr(airspeed, unit)


    # ---------------------------------------------------------------------------------------------
    # - Needle                                                                                    -
    # ---------------------------------------------------------------------------------------------


    # Calibrate given speed to turning angle of needle.
    # Convert speed from native GPX m/s to indicators MPH. Then convert into rotating angle for
    # needle.
    def __convert_speed(self, speed):

        # m/s to MPH
        if self.Unit == "mph":
            speed = conversions.ms2mph(speed)

        # m/s to kt
        elif self.Unit == "kt":
            speed = conversions.ms2kt(speed)

        return speed


    # Calibate scale of facceplate to MPH.
    def __calibration(self, speed):

        calibration = self.calibrator.calibration()

        # Get list of known speed values.
        knownSpeeds = list(calibration.keys())
        knownSpeeds.sort()

        # Check if value is out of scale.
        if speed > max(knownSpeeds):
            speed = max(knownSpeeds)

        # Check for known values and return in directly.
        if speed in calibration:
            return calibration[speed]

        # If value is unknown, calculate intermittent one from linear equation between known neighbours
        # of calibration table.
        else:
            # Get neighbours of requested value.
            lowerNeighbour = 0
            higherNeighbour = 0

            for i in knownSpeeds:
                if i < speed:
                    lowerNeighbour = i
                    continue
                if i > speed:
                    higherNeighbour = i
                    break

            # Get angle with linear equation.
            angle = interpolation.linEqu2pt(lowerNeighbour,
                                            calibration[lowerNeighbour],
                                            higherNeighbour,
                                            calibration[higherNeighbour],
                                            speed)

            # MoviePy uses positive values for counter-clockwise turns.
            #~ return angle * -1
            return angle


    def __parse_speeds(self, pts):
        for pt in lookahead(pts):
            if type(pt) is tuple:
                duration  = pt[0]['length']
                speedFrom = self.__convert_speed(pt[0]['speed'])
                angleFrom = self.__calibration(speedFrom)
                speedTo   = self.__convert_speed(pt[1]['speed'])
                angleTo   = self.__calibration(speedTo)

                self.Speeds.append(
                    {
                        'angleFrom' :   angleFrom,
                        'angleTo'   :   angleTo,
                        'duration'  :   duration,
                        'speed'     :   speedFrom
                    }
                )
        print(self.Speeds)


    # ---------------------------------------------------------------------------------------------
    # - Digital speeds                                                                            -
    # ---------------------------------------------------------------------------------------------


    # In verbose mode show speeds digitally below airspeed indicator.
    def __show_speed(self):

        # Only shw speeds in verbose mode.
        if self.DigSpeed:

            # Iterate threw track points and grap speed and length.
            speedClips = []
            for trkPt in self.Speeds:
                speed = "%2.1f" % trkPt['speed']
                length = trkPt['duration']

                # Create TextClip for each track point.
                speedClips.append(mpy.TextClip( txt             =   speed,
                                                color           =   "white",
                                                bg_color        =   "transparent",
                                                fontsize        =   30,
                                                print_cmd       =   False,
                                                tempfilename    =   "text" + speed + ".png",
                                                remove_temp     =   True
                                              ).set_duration(length)
                                 )

            # Merge track point text clips.
            self.speedClip = mpy.concatenate_videoclips(speedClips)


    # Create final video clip.
    def make(self):
        # Create needles
        #self.__convert_speeds()
        self._rotate_needle(self.Speeds)
        self._concate_needles()

        # Create faceplate
        self._create_faceplate_clip()

        # Create background.
        self._create_background()

        # Get clips in order. First clip will be played at the bottom, last at the top.
        composition = [self.BgClip,
                       self.FaceplateClip.resize(self.Size).set_position(self.position),
                       self.NeedleClip.resize(self.Size).set_position(self.position)]

        # Create digital speed display.
        if self.DigSpeed:
            self.__show_speed()
            composition.append(self.speedClip)

        # Compose clips and export.
        final_video = mpy.CompositeVideoClip(composition)
        return final_video


    def save(self, clip, filename, settings=None):

        if settings is None:
            settings = self.Settings

        clip.write_videofile(filename,
                             fps=settings['framerate'],
                             codec=settings['codec'],
                             audio=settings['audio'],
                             threads=settings['ffmpeg_threads'],
                             preset=settings['ffmpeg_preset'])


# EOF

