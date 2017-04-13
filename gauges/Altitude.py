#!/usr/bin/env python3

# *****************************************************************************
# * Altitude Indicator                                                        *
# *****************************************************************************


# Description
# ===========

# Altitude indicator for Video Gauge Creator.

# TODO
# ====

# -


# ABOUT
# =====

# Creator:  Florian Meissner
#           n1990b@gmx.de
# Version:  0.1
# Date:     2017/04/07


# VERSION HISTORY
# ===============

# 0.1:  - Initial Beta


###############################################################################


# Gauge modules
import BaseGauge

# Own library modules
from lib.calculations       import av_conv
from lib.myMisc             import splitPower

# Foreign libraries
import moviepy.editor       as mpy


class Altitude(BaseGauge.AbstractBaseGauge):

    def __init__(self, wpInst, unit, digSpeed=False, autorun=False, \
        settings=None):

        # Variables used in base class, too.
        self._Unit = unit.lower()
        self._Child = self.__class__.__name__

        # Variables
        #~ self._DigSpeed  =   digSpeed    # Show digital speed number in upper
                                        # left corner.
        self._Settings  =   settings    # Video settings
        self._Altitudes =   []          # List with altitudes from track point
                                        # list. Populated by self.__convert().
        self._WpInst    =   wpInst      # Instance of waypoint class.
        self._Needle10000 = []
        self._Needle1000 = []
        self._Needle100 = []

        # Base class constructor
        super(self.__class__, self).__init__()

        # Initializing methods
        self.setNeedle(filename='needle10000.png', var="BaseNeedle10000")
        self.setNeedle(filename='needle1000.png', var="BaseNeedle1000")
        self.setNeedle(filename='needle100.png', var="BaseNeedle100")
        self.setFaceplate()

        # If autorun is enabled, video animation will be written to disk
        # immediately after gathering all data.
        if autorun:
            clip = self.make()
            self.save(clip, "altitude.mp4")


    def _prepare(self):
        """
        Prepare a list with all data of all waypoints needed to create gauge.
        """

        # Get data from waypoint class.
        self._Altitudes = self._WpInst.getAllByField(
            ('altitude', 'duration', 'higherNeighbour'),
            (self._WpInst.U_FT, None, None)
        )

        # Calibrate into rotation angles.
        for wp in self._Altitudes:

            key = self._Altitudes.index(wp)
            altSplit = splitPower(wp['altitude'])

            self._Altitudes[key]['angleFrom10000'] = self._calibration(altSplit[0])
            self._Altitudes[key]['angleFrom1000'] = self._calibration(altSplit[1])
            self._Altitudes[key]['angleFrom100'] = self._calibration(altSplit[2])

            if isinstance(wp['higherNeighbour'], int):
                altSplitHN = \
                    splitPower(self._Altitudes[wp['higherNeighbour']]['altitude'])

                self._Altitudes[key]['angleTo10000'] = \
                    self._calibration(altSplitHN[0])

                self._Altitudes[key]['angleTo1000'] = \
                    self._calibration(altSplitHN[1])

                self._Altitudes[key]['angleTo100'] = \
                    self._calibration(altSplitHN[2])

            else:
                self._Altitudes[key]['angleTo10000'] = \
                    self._calibration(altSplit[0])

                self._Altitudes[key]['angleTo1000'] = \
                    self._calibration(altSplit[1])

                self._Altitudes[key]['angleTo100'] = \
                    self._calibration(altSplit[2])


    # -------------------------------------------------------------------------
    # - Composition                                                           -
    # -------------------------------------------------------------------------

    def make(self):
        """
        Create final video clip.
        """

        # Create needles
        tenthousend = []
        thousend = []
        hundret = []
        for alt in self._Altitudes:
            tenthousend.append(
                {
                    'duration'  : alt['duration'],
                    'angleFrom' : alt['angleFrom10000'],
                    'angleTo'   : alt['angleTo10000']
                }
            )
            thousend.append(
                {
                    'duration'  : alt['duration'],
                    'angleFrom' : alt['angleFrom1000'],
                    'angleTo'   : alt['angleTo1000']
                }
            )
            hundret.append(
                {
                    'duration'  : alt['duration'],
                    'angleFrom' : alt['angleFrom100'],
                    'angleTo'   : alt['angleTo100']
                }
            )
        self._rotate_needle(tenthousend, "_Needle10000", "BaseNeedle10000")
        self._rotate_needle(thousend, "_Needle1000", "BaseNeedle1000")
        self._rotate_needle(hundret, "_Needle100", "BaseNeedle100")
        """
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

        # Get clips in order. First clip will be played at the bottom, last at
        # the top.
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
        """
        pass

    # -------------------------------------------------------------------------
    # - Digital speeds                                                        -
    # -------------------------------------------------------------------------


    '''
    def __show_speed(self):
        """
        In verbose mode show speeds digitally below airspeed indicator.
        """

        # Only shw speeds in verbose mode.
        if self._DigSpeed:

            # Iterate threw track points and grap speed and length.
            speedClips = []
            for trkPt in self._Altitudes:
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
    '''


# EOF

