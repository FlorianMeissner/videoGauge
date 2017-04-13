#!/usr/bin/env python3

# *****************************************************************************
# * Airspeed Indicator Luscombe Style MPH                                     *
# *****************************************************************************


# Description
# ===========

# Airspeed indicator in old Luscombe style for Video Gauge Creator. Indicating
# in MPH.


# TODO
# ====

# - Implement smooth needle rotation.


# ABOUT
# =====

# Creator:  Florian Meissner
#           n1990b@gmx.de
# Version:  1.0
# Date:     2017/04/07


# VERSION HISTORY
# ===============

# 0.1:  - Initial Beta
# 0.2:  - Implemented base class for all gauges.
#       - Moved file out of template folder
#       - Rework interfaces to better split between gauge class
# 0.3:  - Implemented waypoint class as data source.
# 1.0:  - Stable version
#       - Moved save() method to BaseGauge.


###############################################################################


# Gauge modules
import BaseGauge

# Own library modules
from lib.calculations       import av_conv
from lib.myMisc             import lookahead

# Foreign libraries
from math                   import sqrt
import moviepy.editor       as mpy


class Airspeed(BaseGauge.AbstractBaseGauge):

    def __init__(self, wpInst, unit, digSpeed=False, autorun=False, \
        settings=None):

        # Variables used in base class, too.
        self._Unit = unit.lower()
        self._Child = self.__class__.__name__

        # Variables
        self._DigSpeed  =   digSpeed    # Show digital speed number in upper
                                        # left corner.
        self._Settings  =   settings    # Video settings
        self._Speeds    =   []          # List with speeds from track point
                                        # list. Populated by self.__convert().
        self._WpInst    =   wpInst      # Instance of waypoint class.

        # Base class constructor
        super(self.__class__, self).__init__()

        # Initializing methods
        self.setNeedle()
        self.setFaceplate()

        # If autorun is enabled, video animation will be written to disk
        # immediately after gathering all data.
        if autorun:
            clip = self.make()
            self.save(clip, "airspeed.mp4")


    def _prepare(self):
        """
        Prepare a list with all data of all waypoints needed to create gauge.
        """

        # Get data from waypoint class.
        self._Speeds = self._WpInst.getAllByField(
            ('speed', 'duration', 'higherNeighbour'),
            (self._WpInst.U_MPH, None, None)
        )

        # Calibrate into rotation angles.
        for wp in self._Speeds:
            key = self._Speeds.index(wp)
            self._Speeds[key]['angleFrom'] = self._calibration(wp['speed'])
            if isinstance(wp['higherNeighbour'], int):
                self._Speeds[key]['angleTo'] = self._calibration(self._Speeds[wp['higherNeighbour']]['speed'])
            else:
                self._Speeds[key]['angleTo'] = self._calibration(wp['speed'])


    # -------------------------------------------------------------------------
    # - Composition                                                           -
    # -------------------------------------------------------------------------

    def make(self):
        """
        Create final video clip.
        """

        # Create needles
        self._rotate_needle(self._Speeds)
        self._concate_needles()

        # Create faceplate
        self._create_faceplate_clip()

        # Create background.
        self._create_background()

        # Create gauge clip without background at first because otherwise needle
        # will be moved out of center of faceplate.
        gaugeclip = [
            self._FaceplateClip \
                .resize(self._Size) \
                .set_position('center'),
            self._NeedleClip \
                .resize((self._Size[0]*1.5, self._Size[1]*1.5)) \
                .set_position('center')
        ]
        gaugeclip = mpy.CompositeVideoClip(gaugeclip)

        # Get clips in order. First clip will be played at the bottom, last at the top.
        composition = [
            self._BgClip,
            gaugeclip.set_position(self._Position)
        ]

        # Create digital speed display.
        if self._DigSpeed:
            self.__show_speed()
            composition.append(self._SpeedClip)

        # Compose clips and export.
        final_video = mpy.CompositeVideoClip(composition)
        return final_video


    # -------------------------------------------------------------------------
    # - Digital speeds                                                        -
    # -------------------------------------------------------------------------


    def __show_speed(self):
        """
        In verbose mode show speeds digitally below airspeed indicator.
        """

        # Only shw speeds in verbose mode.
        if self._DigSpeed:

            # Iterate threw track points and grap speed and length.
            speedClips = []
            for trkPt in self._Speeds:
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
            self._SpeedClip = mpy.concatenate_videoclips(speedClips)

# EOF

