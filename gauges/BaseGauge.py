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
# Version:  0.1
# Date:     2017/03/06


# VERSION HISTORY
# ===============

# 0.1:  Initial Beta


###################################################################################################

# Own libraries
from lib.calculations   import conversions, triangulation
from lib.myMisc         import basePath

# Foreign libraries
from PIL                import Image
import logging          as log
import moviepy.editor   as mpy
import os


class BaseGauge(object):

    def __init__(self):

        # Constands
        self.BASEPATH = basePath(__file__)

        # Defaults
        self.position = "center"
        self.tmpFolder = "videoGauge_tmp/"

        # Initializers
        self.BgColor = (0, 0, 255)
        self.Duration = 0
        self.Needles = []


    # ---------------------------------------------------------------------------------------------
    # - Needle                                                                                    -
    # ---------------------------------------------------------------------------------------------

    # Rotate needle image by given angle of track point.
    def _rotate_needle(self, values):

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


    def __animateNeedleRotation(self, aFrom, aTo, dur):

            # Get base needle instance and set duration for animation.
            baseNeedle = self.BaseNeedle.set_duration(dur)

            # Calculate rotation angle. (Way to go)
            # Calculation is valid for 1 sec. So divide by duration of animation.
            # Using starting point first in the subtraction results in negative delta values if
            # needle should show rise.
            delta = (aFrom - aTo) / dur

            print(aFrom, aTo, delta, dur, self.Duration)

            # Invert starting angle because of rotation direction.
            aFrom = aFrom * -1

            # Rotate needle
            # For clockwise rotaion use negative values.
            self.Needles.append(
                baseNeedle.rotate(
                    lambda t: aFrom+t*delta
                )
            )


    # Set base image containing the needle and convert it to be processed further.
    def setNeedle(self, path):
        self.BaseNeedle = mpy.ImageClip(path)


    # Create video containing all needle positions after another with respective length.
    def _concate_needles(self):
        self.NeedleClip = mpy.concatenate_videoclips(self.Needles, method="compose", bg_color=None)


    # ---------------------------------------------------------------------------------------------
    # - Faceplate                                                                                 -
    # ---------------------------------------------------------------------------------------------


    # Define image containing the faceplate.
    def setFaceplate(self, path):
        self.FaceplateImage = path

        # Get image size.
        with Image.open(path) as im:
            self.Size = im.size


    # Create clip with stanting image of faceplate.
    def _create_faceplate_clip(self):
        self.FaceplateClip = mpy.ImageClip(self.FaceplateImage)
        self.FaceplateClip = self.FaceplateClip.set_duration(self.Duration)


    # ---------------------------------------------------------------------------------------------
    # - Background color (blue wall)                                                              -
    # ---------------------------------------------------------------------------------------------


    # Set color for background. Overwrites default.
    def setBackground(self, r, g, b):
        self.BgColor = (r, g, b)


    # Get clip showing background color over the hole duration of the video.
    """
    def _create_background(self):
        self.bgClip = mpy.ColorClip(
                                    conversions.splitXY(self.Settings['format']),
                                    col=self.bgcolor,
                                    duration=self.cumDuration
                                   )
    """
    def _create_background(self):
        bgSize = int(triangulation.pythagoras(a=self.Size[0], b=self.Size[1]))
        self.BgClip = mpy.ColorClip(size=(bgSize, bgSize), col=self.BgColor, duration=self.Duration)


    # ---------------------------------------------------------------------------------------------
    # - Composition                                                                               -
    # ---------------------------------------------------------------------------------------------


    """
    def setPosition(self, pos):
        self.position = pos


    def setSize(self, w, h):
        self.size = (w, h)
    """


    # Adds aspecified amound of time to overall clip duration.
    def _addDuration(self, t):
        self.Duration += t

#EOF
