# -*- coding: utf-8 -*-
"""Control a surveillance/video camera in a car.

This module grabs single frames from a running video device to process
them and stores only gpg-encrypted data on the file system. For this to
be effective, the underlying operating system must not have a swap.

Example:
    $ picture = camera.take_picture_from_device(0)
    $ camera.encrypt_picture_to_file(picture, 'picture.png.gpg')
"""

import logging
import numpy
import gnupg
import time
import tarfile
import sys
import cv2
import os.path # does file exist

########################################################################
# DEFAULT CAMERA VALUES
########################################################################

# target directory to save the compressed archives
DEFAULT_TARGET_DIRECTORY = 'pictures'
# default value for source device number
DEFAULT_SOURCE = 0
# maximum number of frames being processed by
DEFAULT_MAX_FRAMES = 100
# maximum number of pictures, that will be saved
DEFAULT_MAX_FACES = 4
# waiting time in milliseconds before taking next picture
DEFAULT_FRAMERATE = 200
# boolean for calling `cv2.imshow('name', frame)` (only on computers)
DEFAULT_SHOW_IMAGE = False
# boolean for printing matching coordinates of faces upon match
DEFAULT_PRINT_MATCH_COORDS = False         
# scaling factor for haar-cascade, has to be greater than 1
# smaller values will slow the process down but deliver better results
# normally between 1.05 and 1.8
DEFAULT_DETECT_SCALE_FACTOR = 1.3
# required number of neighbors for matching faces. required for cascade
# higher values for better but fewer matches
DEFAULT_DETECT_NEIGHBORS = 3
# haar cascade database
DEFAULT_CASCADE_FILENAME = "haarcascade_frontalface_default.xml"
# flags for haar cascade
DEFAULT_DETECT_FLAGS = cv2.cv.CV_HAAR_SCALE_IMAGE
# minimum size in pixel of detected faces
DEFAULT_DETECT_MIN_SIZE=(20,20)
# color of rectangle drawn around matched faces
DEFAULT_RECT_COLOR = (0,255,0) # green
# width of rectangle drawn around matched faces
DEFAULT_RECT_WIDTH = 2


# make it constant?
log = logging.getLogger(__name__)

class Camera:
    def __init__(self, *initial_data, **kwargs):
        self.source           = DEFAULT_SOURCE
        self.max_frames       = DEFAULT_MAX_FRAMES
        self.max_faces        = DEFAULT_MAX_FACES
        self.show_image       = DEFAULT_SHOW_IMAGE
        self.print_on_match   = DEFAULT_PRINT_MATCH_COORDS
        self.framerate        = DEFAULT_FRAMERATE
        self.cascade_filename = DEFAULT_CASCADE_FILENAME
        self.detect_scale     = DEFAULT_DETECT_SCALE_FACTOR
        self.detect_neighbors = DEFAULT_DETECT_NEIGHBORS
        self.detect_min_size  = DEFAULT_DETECT_MIN_SIZE
        self.detect_flags     = DEFAULT_DETECT_FLAGS
        self.rect_color       = DEFAULT_RECT_COLOR
        self.rect_width       = DEFAULT_RECT_WIDTH
        self.target_dir       = DEFAULT_TARGET_DIRECTORY        
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])
        # TODO make this configurable
        self.gpg = gnupg.GPG(gnupghome='/home/maikel/.gnupg')
        # this needs python-gnupg (>0.3.7)
        # for older versions use 
        # pub_keys = gpg.list_keys()   (gets ALL registered public keys)
        self.pub_keys = self.gpg.scan_keys('public_keys')
        log.debug("Using '"+self.cascade_filename+"' as cascade database.")        
        self.face_cascade = cv2.CascadeClassifier(self.cascade_filename)

    def encrypt_picture_to_file(self, picture, file_name):
        """Uses all known gpg public keys to encrypt and store a picture"""
        (ret, data) = cv2.imencode('.png', picture)
        data = [data.tostring()]
        for key in self.pub_keys:
            log.info("Picture gets encrypted for " + str(key['uids']) + ".")
            encrypted = self.gpg.encrypt(data[-1], key['fingerprint'], armor=True)
            data.append(encrypted.data)
        log.info("Save encrypted picture as '" + file_name + "'.")
        fd = open(file_name, "wb")
        fd.write(data[-1])
        fd.close()
        return data[-1]

    def scan_for_faces(self):
        """Use webcam and take pictures of faces, if you see them."""        
        log.debug("Starting camera.")
        cap = cv2.VideoCapture(self.source)
        ret, frame = cap.read()
        count = 0
        candidate_num = 0
        faces_max_save_steps = self.max_frames/self.max_faces
        if not os.path.exists(self.target_dir):
            os.makedirs(self.target_dir)

        pictures = []
        while ret:
            log.debug("Processing Frame #" + str(count+1) + ".")
            # check here if we are looking for the next candidate
            # if counts gets bigger than a threshhold we save our current
            # candidate and look for the candidate of the next image
            if count >= candidate_num*faces_max_save_steps \
                    and candidate_num < self.max_faces:
                if candidate_num > 0:
                    pictures.append(self.current_candidate_path)
                    log.info("Picture number #"+str(candidate_num)+
                             " found and saved!")
                candidate_num += 1
                self.current_candidate_faces = 0
            # construct candidate path                    
            self.current_candidate_path = \
                    self.target_dir+"/picture_"+str(candidate_num)+".png.gpg"
            # if we dont have any candidate yet save next picture
            if not os.path.isfile(self.current_candidate_path):
                log.info("First candidate for picture number "+str(candidate_num)+
                         ". Simply saving next frame.")        
                self.encrypt_picture_to_file(frame, self.current_candidate_path)
            # otherwise check if frame got more faces then previous candidate
            else:            
                self._save_frame_if_next_candidate(frame)
            # next frame step
            if self.show_image:
                cv2.imshow('camera', frame)
            cv2.waitKey(self.framerate)
            if (self.max_frames <= count):
                cap.release()
                break
            count = count + 1
            ret, frame = cap.read()
        # remember last picture to be compressed
        pictures.append(self.current_candidate_path)
        log.info("Picture number #"+str(candidate_num)+
                 " found and saved!")
        cap.release()
        # compress the images in one tar ball and remove the uncompressed ones
        _create_bz2_from_files('pictures.tar.bz2', pictures, self.target_dir)
        if self.show_image:
            cv2.destroyAllWindows()

    def _save_frame_if_next_candidate(self, current_frame):
        # Use haar-detection for finding faces
        gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        detected_faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=self.detect_scale,
                minNeighbors=self.detect_neighbors,
                minSize=self.detect_min_size,
                flags=self.detect_flags)
        for (x,y,w,h) in detected_faces:
            cv2.rectangle(current_frame, (x,y), (x+w, y+h),
                          self.rect_color, self.rect_width)
        # check for found faces and store frame as new candidate if it has more
        # faces than before!
        # if no faces are found detected_faces is a tuple. otherwise a numpy array!
        if not(isinstance(detected_faces, tuple)) \
                and self.current_candidate_faces < detected_faces.size:
            log.info("Updating candidate. Found " +
                      str(detected_faces.size) + " face(s)!")
            self.encrypt_picture_to_file(current_frame, self.current_candidate_path)
            self.current_candidate_faces = detected_faces.size

    def take_picture(self):
        """Takes a picture from source and returns it."""
        log.debug("Taking picture.")
        log.debug("Opening source device '" + str(self.source) + "'.")
        cap = cv2.VideoCapture(self.source)
        if cap.isOpened():
            ret, frame = cap.read()
            log.debug("Got picutre! Releasing device.")
            cap.release()
            return frame
        else:
            log.error(
                "Could not open '" + str(source) + "' as video capturing device!")
            raise Exception("Could not open the camera!")

def _create_bz2_from_files(archive, files, target_dir):
    """Take a list of file names and add them `archive`.

    Example:
        _create_bz2_from_files('pictures.tar.bz2',
                               ['pic1.png.gpg', 'pic2.png.gpg'])
    Params:
        archive - name of the archive to be created
        files   - list of files to add to archive
    """
    # prepare target directories and build target name
    directory_name = target_dir+time.strftime("/%d.%m.%Y/%H:%M:%S")
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
    tarname = directory_name+"/"+archive
    # create archive with python module 'tarfile'
    archive_type = str.split(archive,'.')[-1]
    tarfd = tarfile.open(tarname, 'w:'+archive_type)
    for f in files:
        tarfd.add(f)
        os.remove(f)
    tarfd.close()
    log.info('Created archive "'+tarname+'"!')