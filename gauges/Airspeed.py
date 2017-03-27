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
# Version:  0.3
# Date:     2017/02/21


# VERSION HISTORY
# ===============

# 0.1:  - Initial Beta
# 0.2:  - Implemented base class for all gauges.
#       - Moved file out of template folder
#       - Rework interfaces to better split between gauge class
# 0.3:  - Implemented waypoint class as data source.


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

        def faceplateSize(hy):
            cat = sqrt(hy**2/2)
            diff = hy - cat
            a = cat + diff/2
            return a

        def needleSize(a):
            return a * 1.075

        # Create needles
        self._rotate_needle(self._Speeds)
        self._concate_needles()

        # Create faceplate
        self._create_faceplate_clip()

        # Create background.
        self._create_background()

        # Calculate size for faceplate
        a = faceplateSize(self._Size[0])
        b = faceplateSize(self._Size[1])
        c = needleSize(self._Size[0])
        d = needleSize(self._Size[1])

        # Create gauge clip without background at first.
        gaugeclip = [
            self._FaceplateClip \
                .resize((a, b)) \
                .set_position('center'),
            self._NeedleClip \
                .resize((c, d)) \
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
        #~ final_video = mpy.CompositeVideoClip(gaugeclip)
        return final_video


    def save(self, clip, filename, settings=None):
        """
        Save compiled video to disk.
        """

        if settings is None:
            settings = self._Settings

        clip.write_videofile(filename,
                             fps=settings['framerate'],
                             codec=settings['codec'],
                             audio=settings['audio'],
                             threads=settings['ffmpeg_threads'],
                             preset=settings['ffmpeg_preset'])


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


    # -------------------------------------------------------------------------
    # - Needle                                                                -
    # -------------------------------------------------------------------------

    '''
    def __parse_speeds(self, pts):
        """
        Work through list of given track points and filter speed and duration
        from them. Also convert speeds into rotation angle for needle graphic.

        lookahead() is used because it is mandetory to remember values from last
        run of the for loop to get angle range to animate.
        """

        for pt in lookahead(pts):

            # Last value will be not tuple. Skip because it has no following
            # point.
            if type(pt) is tuple:
                duration  = pt[0]['length']
                speedFrom = self.__convert_speed(pt[0]['speed'])
                angleFrom = self._calibration(speedFrom)
                speedTo   = self.__convert_speed(pt[1]['speed'])
                angleTo   = self._calibration(speedTo)

                self._Speeds.append(
                    {
                        'angleFrom' :   angleFrom,
                        'angleTo'   :   angleTo,
                        'duration'  :   duration,
                        'speed'     :   speedFrom
                    }
                )
    '''

# EOF

