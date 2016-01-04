import unittest
import logging
import cv2
import taxicam.camera


class TestCamera(unittest.TestCase):

    def test_max_faces_greater_max_frames(self):
        camera = taxicam.camera.Camera(max_frames=10, max_pictures=11)
        pictures = camera.scan_faces()
        print pictures
        self.assertEqual(len(pictures), 10)


if __name__ == '__main__':
    unittest.main()