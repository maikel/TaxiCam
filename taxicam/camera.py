"""Provides functions to use a webcam in combination with gpg."""

import logging
import numpy
import gnupg
import cv2

log = logging.getLogger(__name__)
gpg = gnupg.GPG(gnupghome='/home/maikel/.gnupg')
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
    png = cv2.imencode('.png', picture)
    data = numpy.array(png[1]).tostring()
    for key in pub_keys:
        log.debug("Picture gets encrypted for " + str(key['uids']) + ".")
        data = gpg.encrypt(data+'\0', key['fingerprint'])
    log.info("Saving encrypted picture as '" + file_name + "'.")
    fd = open(file_name, "wb")
    fd.write(str(data))
    fd.close()
    return data

def picture_has_face(picture, cascade):
    """Use HAAR-Cascading to decide if you see a face."""
    return false

def scan_cam(source, max_frames):
    """Scan webcam for max_frames and take pictures of faces."""
    cap = cv2.VideoCapture(source)
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    while cap.isOpened():
        ref, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detected_faces = face_cascade.detectMultiScale(gray, 1.3, 3)
        for (x,y,w,h) in detected_faces:
            cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2)
        if detected_faces.empty():
            cv2.imshow('no face found', frame)
        else:
            cv2.imshow('found face(s)', frame)
        if ref > max_frames:
            cap.release()
            break
    cv2.destroyAllWindows()
