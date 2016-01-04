#! /usr/bin/env python
import RPi.GPIO as GPIO
import taxicam.camera as taxi
import logging

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(True)

button = 14

logging.basicConfig(
        format='%(asctime)s %(name)s [%(levelname)s] %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        level=logging.INFO)

log = logging.getLogger(__name__)
camera = taxi.Camera(pub_keys='pub.gpg', framerate=50, max_frames=50)

GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
while True:
    try:
        log.info('Waiting for activation button.')
        GPIO.wait_for_edge(button, GPIO.RISING)
        log.info('Button pushed!')
        camera.scan_faces()
    except KeyboardInterrupt:
        GPIO.cleanup()
GPIO.cleanup()
