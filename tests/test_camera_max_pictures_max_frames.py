'''import unittest
import logging
import cv2
import sys
import taxicam.camera

max_framess = range(5, 11)
max_picturess = range(1, 12)

class TestCameraMaxPicutresMaxFrames(unittest.TestCase):
    def setUp(self):
        self.camera = taxicam.camera.Camera(framerate=1)

def test_generator(a, b):
    def test(self):
        self.camera.max_frames = mf
        self.camera.max_pictures = mp
        pictures = self.camera.scan_faces()
        self.assertEqual(len(pictures), min(mf,mp))
    return test

def test_picture
    def test(self)
        self.camera.take_picture()

for mf in max_framess:
    for mp in max_picturess:
        test_name = 'test_max_pictures_%d_max_frames_%d' % (mp, mf)
        test = test_generator(mf, mp)
        setattr(TestCamera, test_name, test)
'''