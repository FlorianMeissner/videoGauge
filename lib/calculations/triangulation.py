#!/usr/bin/env python3

# *************************************************************************************************
# * Triangulation                                                                                 *
# *************************************************************************************************


# Description
# ===========

# Collection of functions used in triangulation.

# Triangle:
#       C
#       /\
#    b /  \ a
#     /    \
#    /      \
# A ---------- B
#       c


# TODO
# ====

# -


# ABOUT
# =====

# Creator:  Florian Meissner
#           n1990b@gmx.de
# Version:  0.1
# Date:     2017/02/28


# VERSION HISTORY
# ===============

# 0.1:  Initial Beta


###################################################################################################


from math import *


# Pythagoras sentence
def pythagoras(a=None, b=None, c=None):

    # c wanted
    if c is None and a is not None and b is not None:
        c = a ** 2 + b ** 2
        c = sqrt(c)
        return c

    # b wanted
    elif b is None and a is not None and c is not None:
        b = c**2 - a**2
        b = sqrt(b)
        return b

    # a wanted
    elif a is None and b is not None and c is not None:
        a = c**2 - b**2
        a = sqrt(a)
        return a

    # More or less than 2 sides are given.
    else:
        raise AttributeError("Specify 2 sides of the triangle!")


# Sine sentence
#               a
# sin(alpha) = ---
#               c

def sinSentence(alpha=None, a=None, c=None):

    # alpha wanted.
    if alpha is None and a is not None and c is not None:
        a = float(a)
        c = float(c)
        alpha = a / c
        alpha = asin(alpha)
        alpha = degrees(alpha)
        return alpha

    # Opposite side wanted
    elif a is None and alpha is not None and c is not None:
        alpha = radians(alpha)
        c = float(c)
        a = sin(alpha) * c
        return a

    # Hypotenuse wanted
    elif c is None and alpha is not None and a is not None:
        alpha = radians(alpha)
        a = float(a)
        c = a / sin(alpha)
        return c

    # More or less than 2 sides are given.
    else:
        raise AttributeError("Specify 2 sides of the triangle or one side and the angle!")


# Cosine sentence
#               b
# cos(alpha) = ---
#               c

def cosSentence(alpha=None, b=None, c=None):

    # alpha wanted
    if alpha is None and b is not None and c is not None:
        b = float(b)
        c = float(c)
        alpha = asin(b/c)
        alpha = degrees(alpha)
        return alpha

    # Adjacent side wanted
    elif b is None and alpha is not None and c is not None:
        alpha = radians(alpha)
        c = float(c)
        b = cos(alpha) * c
        return b

    # Hypotenuse wanted
    elif c is None and alpha is not None and b is not None:
        alpha = radians(alpha)
        b = float(b)
        c = b / cos(alpha)
        return c

    # More or less than 2 sides are given.
    else:
        raise AttributeError("Specify 2 sides of the triangle or one side and the angle!")


# Tangent sentence
#               a
# tan(alpha) = ---
#               b

def tanSentence(alpha=None, a=None, b=None):

    # alpha wanted
    if alpha is None and a is not None and b is not None:
        a = float(a)
        b = float(b)
        alpha = atan(a/b)
        alpha = degrees(alpha)
        return alpha

    # Opposite side wanted
    elif a is None and alpha is not None and b is not None:
        alpha = radians(alpha)
        b = float(b)
        a = tan(alpha) * b
        return a

    # Adjacent side wanted
    elif b is None and alpha is not None and a is not None:
        alpha = radians(alpha)
        a = float(a)
        b = a / tan(alpha)
        return b


# EOF
