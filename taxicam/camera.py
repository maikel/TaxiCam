"""Provides functions to use a webcam in combination with gpg."""

import logging
import numpy
import gnupg
import time
import sys
import cv2
import os.path # does file exist

log = logging.getLogger(__name__)
gpg = gnupg.GPG(gnupghome='/home/maikel/.gnupg')
gpg.encoding = 'utf8'
pub_keys = gpg.list_keys()

def take_picture_from_device(source):
    """Takes a picture from source and returns it."""
    log.debug("Taking picture.")
    log.debug("Opening source device '" + str(source) + "'.")
    cap = cv2.VideoCapture(source)
    if cap.isOpened():
        ret, frame = cap.read()
        log.debug("Got picutre! Releasing device.")
        cap.release()
        return frame
    else:
        log.error(
            "Could not open '" + str(source) + "' as video capturing device!")
        raise Exception("Could not open the camera!")

def encrypt_picture_to_file(picture, file_name):
    """Takes a cv-picture, converts to PNG in memory and encrypt it."""
    (ret, data) = cv2.imencode('.png', picture)
    data = data.tostring()
    for key in pub_keys:
        log.info("Picture gets encrypted for " + str(key['uids']) + ".")
        encrypted = gpg.encrypt(data, key['fingerprint'], armor=False)
        data = encrypted.data
    log.info("Save encrypted picture as '" + file_name + "'.")
#    print data
    fd = open(file_name, "wb")
    fd.write(data)
    fd.close()
    return data

def scan_cam(source=0,
             max_frames=100,
             max_faces=4,
             show_image=False,
             print_on_match=False,
             framerate=200,
             cascade_filename="haarcascade_frontalface_default.xml",
             detect_scale=1.3,
             detect_neighbors=4,
             detect_min_size=(20,20),
             detect_flags=cv2.cv.CV_HAAR_SCALE_IMAGE,
             rect_color=(0,255,0),
             rect_width=2):
    """Scan webcam and take pictures of faces."""
    starting_time = time.strftime("%d.%m.%y_%H:%M:%S-")
    cap = cv2.VideoCapture(source)
    log.debug("Using '"+cascade_filename+"' as cascade database.")
    face_cascade = cv2.CascadeClassifier(cascade_filename)
    log.debug("Starting camera.")
    ret, frame = cap.read()
    count = 0
    faces_saved = 0
    faces_max_save_steps = max_frames/max_faces
    while ret:
        log.debug("Processing Frame #" + str(count+1) + ".")
        if count >= faces_saved*faces_max_save_steps and faces_saved < max_faces:
            faces_saved += 1
        # if we dont have an image yet, just save and look for better later
        image_file_name = starting_time+"image"+str(faces_saved)+".png.gpg"
        if not os.path.isfile(image_file_name):
            log.info("Time for another image!" +
                      " Saving first candidate no. #" + str(faces_saved) + ".")
            encrypt_picture_to_file(frame, image_file_name)
            updated = 0

        # detect and mark faces ...
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # gray = cv2.equalizeHist(gray) maybe better results?
        detected_faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=detect_scale,
                minNeighbors=detect_neighbors,
                minSize=detect_min_size,
                flags=detect_flags)
        for (x,y,w,h) in detected_faces:
            cv2.rectangle(frame, (x,y), (x+w, y+h), rect_color, rect_width)

        # check if we have match!
        if not(isinstance(detected_faces, tuple)) or detected_faces:
            if print_on_match:
                log.info("Found face(s) at:")
                for (x,y,w,h) in detected_faces:
                    log.info("\t(x="+str(x)+",y="+str(y)+")")
            # if we found a "better" update, update the image!
            if updated < detected_faces.size:
                log.info("Updating candidate #" + str(faces_saved) + ".")
                encrypt_picture_to_file(frame, image_file_name)
                updated = detected_faces.size

        if show_image: 
            cv2.imshow('camera', frame)
        cv2.waitKey(framerate)
        if (max_frames <= count):
            cap.release()
            break
        count = count + 1
        ret, frame = cap.read()
    cv2.destroyAllWindows()
