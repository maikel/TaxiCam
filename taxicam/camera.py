# -*- coding: utf-8 -*-
"""Control a surveillance/video camera in a car.

This module grabs single frames from a running video device to process
them and stores only gpg-encrypted data on the file system. For this to
be effective, the underlying operating system must not have a swap.

Example:
    $ picture = camera.take_picture_from_device(0)
    $ camera encrypt_picture(picture, 'picture.png.gpg')
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

__DEFAULT_VALUES_CAMERA__ = {
    # target directory to save the compressed archives
    'target_directory': 'archives',
    # default value for source device number
    'source': 0,
    # maximum number of frames being processed by
    'max_frames': 100,
    # maximum number of pictures, that will be saved
    'max_faces': 4,
    # waiting time in milliseconds before taking next picture
    'framerate': 200,
    # boolean for calling cv2.imshow('name', frame) (only on computers)
    'show_image': False,
    # boolean for printing matching coordinates of faces upon match
    'print_coordinates_on_match': False,
    # scaling factor for haar-cascade
    # Smaller values will slow down the detection but result in better
    # matches. Has to be greater than 1 and is normally chosen between
    # 1.1 and 1.5
    'detect_scale': 1.3,
    # required number of neighbors for matching faces. required for cascade
    # higher values for better but fewer matches
    'detect_neighbors': 3,
    # haar cascade database
    'cascade_filename': "haarcascade_frontalface_default.xml",
    # flags for haar cascade
    'detect_flags': cv2.cv.CV_HAAR_SCALE_IMAGE,
    # minimum size in pixel of detected faces
    'detect_min_size': (20,20),
    # leave the image untouched if false, otherwise draw a rectangle
    # around matching faces
    'rect_draw': True,
    # color of rectangle drawn around matched faces
    'rect_color': (0,255,0), # green
    # width of rectangle drawn around matched faces
    'rect_width': 2,
    # gnupg home path
    'gnupghome': ''
}

# make it constant
log = logging.getLogger(__name__)

class Camera:
    def __init__(self, *initial_data, **kwargs):
        # set default values from dictionary
        for key in __DEFAULT_VALUES_CAMERA__:
            setattr(self, key, __DEFAULT_VALUES_CAMERA__[key])  
        # alter class values if neccessary
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])
        
        self.gpg = gnupg.GPG(gnupghome=self.gnupghome)
        # this needs python-gnupg (>0.3.7)
        self.pub_keys = self.gpg.scan_keys('public_keys')        
        log.debug("Using '"+self.cascade_filename+"' as cascade database.")        
        self.face_cascade = cv2.CascadeClassifier(self.cascade_filename)

    def scan_faces(self):
        """Use webcam and take pictures of faces, if you see them."""        
        log.debug("Starting camera.")
        cap = cv2.VideoCapture(self.source)
        ret, frame = cap.read()
        count = 0
        candidate_num = 0
        current_faces = 0
        faces_max_save_steps = self.max_frames/self.max_faces
        if not os.path.exists(self.target_directory):
            os.makedirs(self.target_directory)
        # remember paths to pictures which are chosen from the candidates
        pictures = []
        while ret:
            log.debug("Processing Frame #" + str(count+1) + ".")
            # check here if we are looking for the next candidate
            # if counts gets bigger than a threshhold we save our current
            # candidate and look for the candidate of the next image
            if count >= candidate_num*faces_max_save_steps \
                    and candidate_num < self.max_faces:
                if candidate_num > 0:
                    pictures.append(current_path)
                    log.info("Picture number #" + str(candidate_num) + 
                             " found and saved!")
                candidate_num += 1
                current_path = self.target_directory \
                    + "/picture_" + str(candidate_num) + ".png.gpg"
                if os.path.isfile(current_path):
                    os.remove(current_path)
                log.info("First candidate for picture number " + \
                         str(candidate_num) + ". Simply saving next frame.")        
                encrypted = self.encrypt_picture(frame, current_path)
                log.info('Save encrypted picture as "'+current_path+'".')
                current_faces = 0
            # Check here for the next candidate. See that function for details
            else:
                current_faces = self._save_frame_if_next_candidate(
                    frame, current_path, current_faces)

            # show image if requested (needs visual, e.g. computer monitor)
            if self.show_image:
                cv2.imshow('camera', frame)
            # waiting time in milliseconds
            cv2.waitKey(self.framerate)
            if (self.max_frames <= count):
                cap.release()
                break
            count = count + 1
            ret, frame = cap.read()

        # remember to compress last taken picture
        pictures.append(current_path)
        log.info("Picture number #"+str(candidate_num)+" found and saved!")
        cap.release()

        # compress the images in one tar ball and remove the uncompressed ones
        _create_bz2_from_files('pictures.tar.bz2', pictures, self.target_directory)
        if self.show_image:
            cv2.destroyAllWindows()

    def encrypt_picture(self, picture, save_to=''):
        """Uses all given public keys to encrypt a cv picture iteratively.

        Params:
            self
            picture  picture in opencv style
            save_to  if given save the encrypted picture there
        """
        (ret, data) = cv2.imencode('.png', picture)
        data = data.tostring()
        for key in self.pub_keys:
            log.info("Picture gets encrypted for " + str(key['uids']) + ".")
            encrypted = self.gpg.encrypt(data, key['fingerprint'])
            data = encrypted.data
        if save_to:
            encrypted_fd = open(save_to, "wb")
            encrypted_fd.write(data)
            encrypted_fd.close()
        return data

    def _save_frame_if_next_candidate(self, 
                current_frame, current_path, current_faces):
        """This method is called in scan_faces to detect and encrypt matches.

        It uses the Haar detection method from the OpenCV library to match
        faces in a given frame. If `self.rect_draw` a rectangle for each match
        is drawn into frame. The following class attributes impact this method

        * `detect_scale`:      scaling factor for cascade 
        * `detect_neighbors`:  neighbors required to be a match
        * `detect_min_size`:   minimum size for matching faces
        * `detect_flags`:      special flags for detectMultiScale()
        * ..."""
        gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        detected_faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=self.detect_scale,
                minNeighbors=self.detect_neighbors,
                minSize=self.detect_min_size,
                flags=self.detect_flags)
        if self.rect_draw:
            for (x,y,w,h) in detected_faces:
                cv2.rectangle(current_frame, (x,y), (x+w, y+h),
                              self.rect_color, self.rect_width)
        # Check for number of faces found and store the frame as a new
        # candidate picture if it has more faces than before!
        # Remark: If no faces are found at all `detected_faces` is a tuple.
        #         But otherwise a numpy array!
        if not(isinstance(detected_faces, tuple)) \
                and current_faces < len(detected_faces):
            log.info("Updating candidate. Found " +
                      str(detected_faces.size) + " face(s)!")
            self.encrypt_picture(current_frame, current_path)
            current_faces = len(detected_faces)
        return current_faces

    def take_picture(self):
        """Takes a picture from source and returns it."""
        log.debug("Taking picture.")
        log.debug("Opening  device '" + str(self.source) + "'.")
        cap = cv2.VideoCapture(self.source)
        if cap.isOpened():
            ret, frame = cap.read()
            log.debug("Got picture! Releasing device.")
            cap.release()
            return frame
        else:
            log.error("Could not open '" + str(self.source) + 
                      "' as video capturing device!")
            raise Exception("Could not open the camera!")

    def get_camera(self):
        log.debug("Opening  device '" + str(self.source) + "'.")
        return cv2.VideoCapture(self.source)

def _create_bz2_from_files(archive, files, target_directory):
    """Take a list of file names and add them `archive`.

    Example:
        _create_bz2_from_files('pictures.tar.bz2',
                               ['pic1.png.gpg', 'pic2.png.gpg'])
    Params:
        archive - name of the archive to be created
        files   - list of files to add to archive
    """
    # prepare target directories and build target name
    directory_name = target_directory
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
    tarname = directory_name+"/"+ \
              time.strftime("/%m-%d-%Y_")+str(time.time())+"-"+archive
    # create archive with python module 'tarfile'
    archive_type = str.split(archive,'.')[-1]
    tarfd = tarfile.open(tarname, 'w:'+archive_type)
    for f in files:
        tarfd.add(f)
        os.remove(f)
    tarfd.close()
    log.info('Created archive "'+tarname+'"!')