#!/usr/bin/env python3

# *****************************************************************************
# * Base class for Gauges                                                     *
# *****************************************************************************


# Description
# ===========

# Base class for gauges used for Video Gauge Creator. This class defines methods
# common to all gauges. Specific methods for each gauge will be in the according
# file of this directory. (E.g. Airspeed.py)


# TODO
# ====

# - Add smooth needle rotation
# - Adapt for gauges with multiple needles


# ABOUT
# =====

# Creator:  Florian Meissner
#           n1990b@gmx.de
# Version:  1.0
# Date:     2017/04/07


# VERSION HISTORY
# ===============

# 0.1:  - Initial Beta
# 0.2:  - Make class abstract
# 1.0:  - Stable version
#       - Added save() method


###############################################################################


# Own libraries
from lib.calculations   import av_conv, gui_conv, interpolation, triangulation
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
        self._prepare()

        # Initializers
        self._BgColor = (0, 0, 255)
        self._Needles = []


    # -------------------------------------------------------------------------
    # - Background color (blue wall)                                          -
    # -------------------------------------------------------------------------


    def _create_background(self):
        """
        Get clip showing background color over the hole duration of the video.
        """

        self._BgClip = mpy.ColorClip(
            size=(gui_conv.splitXY(self._Settings['format'])),
            col=self._BgColor,
            duration=self._WpInst.getDuration()
        )


    def setBackground(self, r, g, b):
        """
        Set color for background. Overwrites default.
        """

        self._BgColor = (r, g, b)


    # -------------------------------------------------------------------------
    # - Composition                                                           -
    # -------------------------------------------------------------------------


    def save(self, clip, path, settings=None, force=False):
        """
        Save compiled video to disk.
        """

        if os.path.isdir(path):
            raise IOError(
                "'%s' is a directory. We can't overwrite directories with files!"
                % path
            )

        if os.path.isfile(path):
            a = "no"

            # In quiet mode force to overwrite.
            if not force:
                # If folder exists ask user to overwrite.
                q  = "The file '%s' already exists. "
                q += "It will be overridden. "
                q += "Continue? (Y/n): "
                a = raw_input(q % path)

            if a.lower() in ("", "y", "yes") or force:
                os.remove(path)
            else:
                raise IOError("Aborted by user...")

        if settings is None:
            settings = self._Settings

        clip.write_videofile(path,
                             fps=settings['framerate'],
                             codec=settings['codec'],
                             audio=settings['audio'],
                             threads=settings['ffmpeg_threads'],
                             preset=settings['ffmpeg_preset'])


    # -------------------------------------------------------------------------
    # - Faceplate                                                             -
    # -------------------------------------------------------------------------


    def _create_faceplate_clip(self):
        """
        Create clip with stanting image of faceplate.
        """

        self._FaceplateClip = mpy.ImageClip(self._FaceplateImage)
        self._FaceplateClip = \
            self._FaceplateClip.set_duration(self._WpInst.getDuration())


    def setFaceplate(self, path):
        """
        Define image containing the faceplate.
        """

        self._FaceplateImage = path

        # Get image size.
        with Image.open(path) as im:
            self._Size = im.size


    # -------------------------------------------------------------------------
    # - Initializers                                                          -
    # -------------------------------------------------------------------------

    def __parse_unit(self):
        """
        Parse unit string given to this class and select proper graphics and
        functions.
        """

        unit = self._Unit

        # Set pathes for graphics
        prefix = self.BASEPATH + self._Child.lower() + "/" + unit + "_"
        self.setNeedle(prefix + "needle.png")
        self.setFaceplate(prefix + "faceplate.png")

        # Get calibration table.
        # self.calibrator will hold the imported module named like the passed
        # unit.
        if self._Child is None:
            raise AbstractImplementationRequired("self._Child")

        module = importlib.import_module("gauges."+self._Child.lower())
        self._Gauge_script = getattr(module, unit)


    def setPosition(self, x=None, y=None, xy=None):
        """
        Define psotion to display the gauge in.
        If only x is set, y will be assumed the same.
        If xy is set, it takes x and y size like 200x300. Overwrites x and y.
        """

        if x is None and y is None and xy is None:
            raise ValueError("No value defined.")

        if x is not None:
            if y is None:
                self._Position = (x, x)
            else:
                self._Position = (x, y)

        elif xy is not None:
            self._Position = gui_conv.splitXY(xy)


    def setSize(self, x=None, y=None, xy=None):
        """
        Define size to display the gauge in.
        If only x is set, y will be assumed the same.
        If xy is set, it takes x and y size like 200x300. Overwrites x and y.
        """

        if x is None and y is None and xy is None:
            raise ValueError("No value defined.")

        if x is not None:
            if y is None:
                self._Size = (x, x)
            else:
                self._Size = (x, y)

        elif xy is not None:
            self._Size = gui_conv.splitXY(xy)


    # -------------------------------------------------------------------------
    # - Needle                                                                -
    # -------------------------------------------------------------------------

    def __animateNeedleRotation(self, aFrom, aTo, dur):
        """
        Animate rotation of the needle over a given timeframe. This method
        should only be called from s_rotate_needle(). It wrties the rusulting
        animation directly to self.Needles.
        """

        # Get base needle instance and set duration for animation.
        baseNeedle = self.BaseNeedle.set_duration(dur)

        # Calculate rotation angle. (Way to go)
        # Calculation is valid for 1 sec. So divide by duration of animation.
        # Using starting point first in the subtraction results in negative
        # delta values if needle should show rise.
        delta = (aFrom - aTo) / dur

        # Invert starting angle because of rotation direction.
        aFrom = aFrom * -1

        # Rotate needle
        # For clockwise rotation use negative values.
        self._Needles.append(
            baseNeedle.rotate(
                lambda t: aFrom+t*delta
            )
        )


    def _calibration(self, value, calFunc='calibration'):
        """
        Calibate scale of faceplate.
        """

        calibration = self._Gauge_script.calibration()

        # Get list of known values.
        knownValues = list(calibration.keys())
        knownValues.sort()

        # Check if value is out of scale.
        if value > max(knownValues):
            value = max(knownValues)

        # Check for known values and return in directly.
        if value in calibration:
            return calibration[value]

        # If value is unknown, calculate intermittent one from linear equation
        # between known neighbours of calibration table.
        else:
            # Get neighbours of requested value.
            lowerNeighbour = 0
            higherNeighbour = 0

            for i in knownValues:
                if i < value:
                    lowerNeighbour = i
                    continue
                if i > value:
                    higherNeighbour = i
                    break

            # Get angle with linear equation.
            angle = interpolation.linEqu2pt(lowerNeighbour,
                                            calibration[lowerNeighbour],
                                            higherNeighbour,
                                            calibration[higherNeighbour],
                                            value)

            # MoviePy uses positive values for counter-clockwise turns.
            return angle


    def _concate_needles(self):
        """
        Create video containing all needle positions after another with
        respective length.
        """

        self._NeedleClip = mpy.concatenate_videoclips(
            self._Needles,
            method="compose",
            bg_color=None
        )


    def _rotate_needle(self, values):
        """
        Rotate needle image by given angle of track point.
        This function does the preamptive work for the rotation.
        """

        for v in values:
            if v['duration'] > 0:
                self.__animateNeedleRotation(
                    v['angleFrom'],
                    v['angleTo'],
                    v['duration']
                )


    def setNeedle(self, path):
        """
        Set base image containing the needle and convert it to be processed
        further.
        """

        self.BaseNeedle = mpy.ImageClip(path)


#EOF
