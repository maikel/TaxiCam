#!/usr/bin/env python
"""Takes a picture and saves the encrypted data on disc."""

import sys, getopt
import taxicam.camera as cam
import logging

def main(argv):
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv,"h:o:",["ofile="])
    except getopt.GetoptError:
        print sys.argv[0] + ' -o <outputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print sys.argv[0] + ' -o <outputfile>'
            sys.exit()
        elif opt in ("-o", "--ofile"):
            outputfile = arg
   
    if (outputfile == ''):
        sys.exit()
    
    pic = cam.take_picture_from_device(0)
    cam.encrypt_picture_to_file(pic, outputfile)

if __name__ == "__main__":
    logging.basicConfig(
            format='%(asctime)s %(levelname)s %(message)s',
            datefmt='%m/%d/%Y %I:%M:%S %p',
            level=logging.DEBUG)
    main(sys.argv[1:])
