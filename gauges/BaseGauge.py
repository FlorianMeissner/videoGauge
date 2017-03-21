#!/usr/bin/env python3

# *************************************************************************************************
# * Base class for Gauges                                                                         *
# *************************************************************************************************


# Description
# ===========

# Base class for gauges used for Video Gauge Creator. This class defines methods common to all
# gauges. Specific methods for each gauge will be in the according file of this directory.
# (E.g. Airspeed.py)


# TODO
# ====

# - Add smooth needle rotation
# - Adapt for gauges with multiple needles


# ABOUT
# =====

# Creator:  Florian Meissner
#           n1990b@gmx.de
# Version:  0.2
# Date:     2017/03/10


# VERSION HISTORY
# ===============

# 0.1:  - Initial Beta
# 0.2:  - Make class abstract


###################################################################################################


# Own libraries
from lib.calculations   import av_conv, interpolation, triangulation
from lib.Exceptions     import *
from lib.myMisc         import basePath

# Foreign libraries
from PIL                import Image
import abc
import importlib
import logging          as log
import moviepy.editor   as mpy
import os


class AbstractBaseGauge(object):

    __metaclass__ = abc.ABCMeta
    _Child = None   # Name of child class

    def __init__(self):

        # Constands
        self.BASEPATH = basePath(__file__)

        # Defaults
        self._Position = "center"

        # Initializer methods
        self.__parse_unit()

        # Initializers
        self._BgColor = (0, 0, 255)
        self._Duration = 0
        self._Needles = []


    # ---------------------------------------------------------------------------------------------
    # - Background color (blue wall)                                                              -
    # ---------------------------------------------------------------------------------------------


    def _create_background(self):
        """
        Get clip showing background color over the hole duration of the video.
        """

        bgSize = int(triangulation.pythagoras(a=self._Size[0], b=self._Size[1]))
        self._BgClip = mpy.ColorClip(size=(bgSize, bgSize), col=self._BgColor, duration=self._Duration)


    def setBackground(self, r, g, b):
        """
        Set color for background. Overwrites default.
        """

        self._BgColor = (r, g, b)


    # ---------------------------------------------------------------------------------------------
    # - Composition                                                                               -
    # ---------------------------------------------------------------------------------------------


    def _addDuration(self, t):
        """
        Adds aspecified amound of time to overall clip duration.
        """

        self._Duration += t


    """
    def setPosition(self, pos):
        self.position = pos


    def setSize(self, w, h):
        self.size = (w, h)
    """


    # ---------------------------------------------------------------------------------------------
    # - Faceplate                                                                                 -
    # ---------------------------------------------------------------------------------------------


    def _create_faceplate_clip(self):
        """
        Create clip with stanting image of faceplate.
        """

        self._FaceplateClip = mpy.ImageClip(self._FaceplateImage)
        self._FaceplateClip = self._FaceplateClip.set_duration(self._Duration)


    def setFaceplate(self, path):
        """
        Define image containing the faceplate.
        """

        self._FaceplateImage = path

        # Get image size.
        with Image.open(path) as im:
            self._Size = im.size


    # ---------------------------------------------------------------------------------------------
    # - Initializers                                                                              -
    # ---------------------------------------------------------------------------------------------

    def __parse_unit(self):
        """
        Parse unit string given to this class and select proper graphics and functions.
        """

        unit = self._Unit

        # Set pathes for graphics
        prefix = self.BASEPATH + "airspeed/" + unit + "_"
        self.setNeedle(prefix + "needle2.png")
        self.setFaceplate(prefix + "faceplate.png")

        # Get calibration table.
        # self.calibrator will hold the imported module named like the passed unit.
        if self._Child is None:
            raise AbstractImplementationRequired("self._Child")

        #~ self.calibrator = getattr(airspeed, unit)
        module = importlib.import_module("gauges."+self._Child.lower())
        self._Gauge_script = getattr(module, unit)


    # ---------------------------------------------------------------------------------------------
    # - Needle                                                                                    -
    # ---------------------------------------------------------------------------------------------

    def __animateNeedleRotation(self, aFrom, aTo, dur):
        """
        Animate rotation of the needle over a given timeframe. This method should only be called
        from s_rotate_needle(). It wrties the rusulting animation directly to self.Needles.
        """

        # Get base needle instance and set duration for animation.
        baseNeedle = self.BaseNeedle.set_duration(dur)

        # Calculate rotation angle. (Way to go)
        # Calculation is valid for 1 sec. So divide by duration of animation.
        # Using starting point first in the subtraction results in negative delta values if
        # needle should show rise.
        delta = (aFrom - aTo) / dur

        #~ print(aFrom, aTo, delta, dur, self.Duration)

        # Invert starting angle because of rotation direction.
        aFrom = aFrom * -1

        # Rotate needle
        # For clockwise rotaion use negative values.
        self._Needles.append(
            baseNeedle.rotate(
                lambda t: aFrom+t*delta
            )
        )


    def _calibration(self, speed):
        """
        Calibate scale of faceplate to MPH.
        """

        calibration = self._Gauge_script.calibration()

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


    def _concate_needles(self):
        """
        Create video containing all needle positions after another with respective length.
        """

        self._NeedleClip = mpy.concatenate_videoclips(self._Needles, method="compose", bg_color=None)


    def _rotate_needle(self, values):
        """
        Rotate needle image by given angle of track point.
        This function does the preamptive work for the rotation.
        """

        for v in values:
            angleFrom = v['angleFrom']

            # Don't move needle on last trackpoint because there is no next point known to calculate
            # rotation angle from.
            key = values.index(v)
            if key == len(values) - 1:
                angleTo = angleFrom
            else:
                angleTo = v['angleTo']

            # Define duration of rotation.
            duration = v['duration']
            if duration > 0:
                self._addDuration(duration)
                self.__animateNeedleRotation(angleFrom, angleTo, duration)


    def setNeedle(self, path):
        """
        Set base image containing the needle and convert it to be processed further.
        """

        self.BaseNeedle = mpy.ImageClip(path)


#EOF
