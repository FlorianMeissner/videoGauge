#!/usr/bin/env python3

# *************************************************************************************************
# * Airspeed Indicator Luscombe Style MPH                                                         *
# *************************************************************************************************


# Description
# ===========

# Airspeed indicator in old Luscombe style for Video Gauge Creator. Indicating in MPH.


# TODO
# ====

# -


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


from lib.calculations import conversions
from lib.calculations import interpolation
import moviepy.editor as mpy
from PIL import Image


class AirspeedLuscombeMPH(object):


    def __init__(self, Parent, autorun=False):

        # Variables
        self.Parent = Parent
        self.tmpFolder = Parent.TMP_FOLDER
        self.bgcolor = (0, 0, 255)
        self.cumDuration = 0
        self.position = "center"

        # Administrative prework
        self.setNeedle(self.Parent.basePath + "gauges/airspeed_luscombe_mph/needle.png")
        self.setFaceplate(self.Parent.basePath + "gauges/airspeed_luscombe_mph/faceplate2.png")

        # If autorun is enabled, video animation will be written to disk immediately after gathering
        # all data.
        if autorun:
            self.make()


    # ---------------------------------------------------------------------------------------------
    # - Needle                                                                                    -
    # ---------------------------------------------------------------------------------------------


    # Calibrate given speed to turning angle of needle.
    # Convert speed from native GPX m/s to indicators MPH. Then convert into rotating angle for
    # needle.
    def __convert_speeds(self):

        for trkPt in self.Parent.trkPts:

            # Get key of track point.
            key = self.Parent.trkPts.index(trkPt)

            # m/s to MPH
            trkPt['speed'] = conversions.ms2mph(trkPt['speed'])

            # MPH to rotation angle
            trkPt['angle'] = self.__calibration(trkPt['speed'])

            # Tranfer altered track point back into list.
            self.Parent.trkPts[key] = trkPt


    # Calibate scale of facceplate to MPH.
    def __calibration(self, speed):

        # Define calibration table. Non existing speed values will be interpolated between existing
        # neighbours linearly.
        calibration = { # MPH : Degree
                            0 :   0.0,
                           30 :  13.9,
                           35 :  18.5,
                           40 :  24.3,
                           45 :  30.8,
                           50 :  37.1,
                           55 :  46.6,
                           60 :  49.1,
                           70 :  68.2,
                           80 :  85.7,
                           90 : 109.5,
                          100 : 133.4,
                          110 : 155.5,
                          120 : 180.0,
                          130 : 205.2,
                          140 : 230.2,
                          150 : 258.9,
                          160 : 287.4,
                          170 : 311.9,
                          180 : 337.0
                      }

        # Get list of known speed values.
        knownSpeeds = list(calibration.keys())
        knownSpeeds.sort()

        # Check if value is out of scale.
        if speed > max(knownSpeeds):
            speed = max(knownSpeeds)

        # Check for known values and return in directly.
        if speed in calibration:
            return calibration[speed]

        # If value is unknown, calculate intermittend one from linear equation between known neighbours
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
            return angle * -1


    # Rotate needle image by given angle of track point.
    def __rotate_needle(self):
        self.__print("Creating needle images. This may take a while...")
        for trkPt in self.Parent.trkPts:
            key = self.Parent.trkPts.index(trkPt)
            angle = trkPt['angle']
            filename = self.tmpFolder + "/needle" + "%2.1f" % (angle * -1) + ".png"
            img = self.baseNeedle
            img = img.rotate(angle)
            img = img.save(filename)
            self.Parent.trkPts[key]['path'] = filename
        self.__print("Needle images created!")


    # Set base image containing the needle and convert it to be processed further.
    def setNeedle(self, path):
        self.baseNeedle = Image.open(path)
        self.baseNeedle = self.baseNeedle.convert('RGBA')


    # Create video containing all needle positions after antother with respective length.
    def __concate_needles(self):
        needleClips = []
        for trkPt in self.Parent.trkPts:

            # Get key of track point.
            key = self.Parent.trkPts.index(trkPt)

            # Get image and append to clip. Display duration will be set to length of track point.
            needleImgPath = trkPt['path']
            needleDuration = trkPt['length']
            needleClips.append(mpy.ImageClip(needleImgPath).set_duration(needleDuration))

            # Add length of track point to cumulated length of all track points. Will be used as
            # duration of faceplate and background.
            self.cumDuration += needleDuration

        self.needleClip = mpy.concatenate_videoclips(needleClips)


    # ---------------------------------------------------------------------------------------------
    # - Faceplate                                                                                 -
    # ---------------------------------------------------------------------------------------------


    # Define image containing the faceplate.
    def setFaceplate(self, path):
        self.faceplateImage = path

        # Get image size.
        with Image.open(path) as im:
            self.size = im.size


    # Create clip with stanting image of faceplate.
    def __create_faceplate_clip(self):
        self.faceplateClip = mpy.ImageClip(self.faceplateImage)
        self.faceplateClip = self.faceplateClip.set_duration(self.cumDuration)


    # ---------------------------------------------------------------------------------------------
    # - Background color (blue wall)                                                              -
    # ---------------------------------------------------------------------------------------------


    # Set color for background. Overwrites default.
    def setBackground(self, r, g, b):
        self.bgcolor = (r, g, b)


    # Get clip showing background color over the hole duration of the video.
    def __create_background(self):
        self.bgClip = mpy.ColorClip(
                                    conversions.splitXY(self.Parent.VIDEOSETTINGS['format']),
                                    col=self.bgcolor,
                                    duration=self.cumDuration
                                   )



    # ---------------------------------------------------------------------------------------------
    # - Digital speeds                                                                            -
    # ---------------------------------------------------------------------------------------------


    # In verboe mode show speeds digitally below airspeed indicator.
    def __show_speed(self):

        # Only shw speeds in verbose mode.
        if self.Parent.params['verbose']:

            # Iterate threw track points and grap speed and length.
            speedClips = []
            for trkPt in self.Parent.trkPts:
                speed = "%2.1f" % trkPt['speed']
                length = trkPt['length']

                # Create TextClip for each track point.
                speedClips.append(mpy.TextClip( txt             =   speed,
                                                color           =   "white",
                                                bg_color        =   "transparent",
                                                fontsize        =   30,
                                                #size            =   (100,20),
                                                print_cmd       =   False,
                                                tempfilename    =   self.tmpFolder + "/text" + speed + ".png",
                                                #temptxt         =   "text.txt",
                                                remove_temp     =   False
                                              ).set_duration(length)
                                 )

            # Merge track point text clips.
            self.speedClip = mpy.concatenate_videoclips(speedClips)


    # ---------------------------------------------------------------------------------------------
    # - Composition                                                                               -
    # ---------------------------------------------------------------------------------------------


    def setPosition(self, pos):
        self.position = pos


    def setSize(self, w, h):
        self.size = (w, h)


    # Create final video clip.
    def make(self):
        # Create needles
        self.__convert_speeds()
        self.__rotate_needle()
        self.__concate_needles()

        # Create faceplate
        self.__create_faceplate_clip()

        # Create background.
        self.__create_background()

        # Get clips in order. First clip will be played at the bottom, last at the top.
        composition = [self.bgClip,
                       self.faceplateClip.resize(self.size).set_position(self.position),
                       self.needleClip.resize(self.size).set_position(self.position)]

        # Create digital speed display.
        if self.Parent.params['verbose']:
            self.__show_speed()
            composition.append(self.speedClip)

        # Get filename for video output.
        filename  = self.Parent.params['outputfolder']
        filename += "airspeed"
        filename += self.Parent.VIDEOSETTINGS['filetype']

        # Compose clips and export.
        final_video = mpy.CompositeVideoClip(composition)
        final_video.write_videofile(filename,
                                    fps     =   self.Parent.VIDEOSETTINGS['framerate'],
                                    codec   =   self.Parent.VIDEOSETTINGS['codec'],
                                    audio   =   self.Parent.VIDEOSETTINGS['audio'],
                                    threads =   self.Parent.VIDEOSETTINGS['ffmpeg_threads'],
                                    preset  =   self.Parent.VIDEOSETTINGS['ffmpeg_preset'])


    # ---------------------------------------------------------------------------------------------
    # - Other stuff                                                                               -
    # ---------------------------------------------------------------------------------------------


    # Helper method to print messages. 'v' triggers messages only to be displayed in verbose mode.
    def __print(self, msg, v=False):
        if self.Parent.params['verbose'] and v:
            print(msg, "verbose")
        elif not self.Parent.params['quiet'] and not v:
            print(msg)


# EOF

