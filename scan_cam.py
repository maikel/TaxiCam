#!/usr/bin/env python
"""Scan camera for a face"""

import logging
import sys
import argparse
import taxicam.camera
from ast import literal_eval # safe type converting

loglevels = {
    "info": logging.INFO,
    "debug": logging.DEBUG
}

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--loglevel", help="set log level to info or debug")
    parser.add_argument("--source", type=int)
    parser.add_argument("--max_frames", type=int)
    parser.add_argument("--max_pictures", type=int)
    parser.add_argument("--framerate", type=int)
    parser.add_argument("--detect_neighbors", type=int)
    parser.add_argument("--detect_scale", type=float)
    parser.add_argument("--detect_min_size", type=tuple)
    parser.add_argument("--cascade_filename")
    parser.add_argument("--print_coordinates_on_match", action="store_true")
    parser.add_argument("--show_image", action="store_true")
    parser.add_argument("--rect_draw", action="store_true")
    parser.add_argument("--rect_color", type=tuple)
    parser.add_argument("--rect_width", type=int)
    parser.add_argument("--gnupghome")
    parser.add_argument("--pub_keys")

    args = vars(parser.parse_args())

    if args['loglevel']:
        args['loglevel'] = loglevels[args['loglevel']]
    logging.basicConfig(
            format='%(asctime)s %(name)s [%(levelname)s] %(message)s',
            datefmt='%m/%d/%Y %I:%M:%S %p',
            level=args['loglevel'])

    args = { k : args[k] for k in args if args[k] != None }

    camera = taxicam.camera.Camera(args)    
    camera.scan_faces()

if __name__ == "__main__":    
    main(sys.argv[1:])
