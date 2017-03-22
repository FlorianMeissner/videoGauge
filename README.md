<<<<<<< HEAD
# videoGauge
Converts a GPX file into a video file displaying values in aviation like gauges.
=======
# Video Gauge Creator

## Description

Video Gauge Creator , short VGC, is build to enhance aviation videos by overlaying them
with mock up gauges showing several airplane parameters. Therefore the
software expects a GPX file containing GPS data to the flight. It outputs an
MP4 video stream of the hole duration of the GPX track containing the
configured gauges on a transparent background show the data of the GPX file.
More gauges will be added in the future.


## Installation

Installation instaructions provided under Ubuntu.

1. Download this archive.

    `wget https://github.com/FlorianMeissner/videoGauge/archive/master.zip`
    
2. Extract the archive.

    `unzip master.zip`
    
3. Go into the directory of VGC.

    `cd videoGauge`
    
4. Install dependencies as listed below.

    `sudo apt-get install python python-pip`

    `sudo pip install terminaltabels gpxpy moviepy Pillow`
    
5. Make Video Gauge Creator executable.

    `chmod +x videoGauge.py`
    
6. Start VGC.

    `python ./videoGauge.py --help`


## Command line parameters

pending...
    

## DEPENDENCIES

- Python 2.7
- PIP
    - terminaltables
    - gpxpy
    - moviepy
    - Pillow


## TODO
See TODO.txt


## ABOUT

Creator:  Florian Meissner (n1990b@gmx.de)

Version:  0.3

Date:     2017/03/10


## VERSION HISTORY

0.1:  
- Initial Beta

0.2:  
- Added title centered in console window
- Adjusted gauge class calls to new gauge structure
- Switched gpxpy from local lib to pypi.

0.3:
- Created Class for waypoint storage.
>>>>>>> 7cb66a2... Fixed typo
