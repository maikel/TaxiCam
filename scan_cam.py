#!/usr/bin/env python
"""Scan camera for a face"""

import logging
import sys, getopt
import taxicam.camera
from ast import literal_eval # safe type converting

def main(argv):
    max_frames = 100   # how many frames are processed max
    max_faces  = 4     # how many faces shall be matched max
    framerate  = 100   # pause between images in milliseconds
    source     = 0     # device number or video file
    scale      = 1.2   # scaling factor in haar cascading (>1)
    neighbors  = 3     # min neighbor points in cascading
    verbose    = False # print matches to stdout
    show_image = False # call cv2.imshow (needs monitor)
    min_size   = (100,100) # minimum size of faces in pixel
    loglevel   = None # default log level
    cascade_filename='haarcascade_frontalface_default.xml'

    try:
        opts, args = getopt.getopt(argv,"h:ivp",
                ["max-frames=",
                 "max-faces="
                 "help",
                 "framerate=",
                 "scale=",
                 "neighbors=",
                 "soruce=",
                 "min-size=",
                 "cascade-file=",
                 "debug"])

    except getopt.GetoptError:
        print 'Use "', sys.argv[0],' --help", if you dont know what to do.'
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            # TODO write help...
            print 'Oups...'
            sys.exit()
        elif opt in ("-i", "--cascade_file"):
            haar_cascade_filename=arg
        elif opt == "-v":
            verbose=True
        elif opt == "-p":
            show_image=True
        elif opt == "--max-frames":
            max_frames = literal_eval(arg)
        elif opt == "--max-faces":
            max_faces = literal_eval(arg)
        elif opt == '--framerate':
            framerate = literal_eval(arg)
        elif opt == "--scale":
            scale = literal_eval(arg)
        elif opt == "--neighbors":
            neighbors = literal_eval(arg)
        elif opt == "--source":
            source = literal_eval(arg)
        elif opt == "--min-size":
            min_size = literal_eval(arg)
        elif opt == "--cascade-file":
            cascade_filename = arg
        elif opt == "--debug":
            loglevel=logging.DEBUG
   
    logging.basicConfig(
            format='%(asctime)s %(name)s [%(levelname)s] %(message)s',
            datefmt='%m/%d/%Y %I:%M:%S %p',
            level=loglevel)

    camera = taxicam.camera.Camera(
                source=source,
                max_frames=max_frames,
                max_faces=max_faces,
                framerate=framerate,
                detect_min_size=min_size,
                detect_neighbors=neighbors,
                detect_scale=scale,
                print_on_match=verbose,
                show_image=show_image,
                cascade_filename=cascade_filename)    
    camera.scan_faces()

if __name__ == "__main__":    
    main(sys.argv[1:])
