import unittest
import logging
import cv2
import taxicam.camera as cam


class TestCamera(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(
                fformat='%(asctime)s %(levelname)s %(message)s',
                datefmt='%m/%d/%Y %I:%M:%S %p',
                level = logging.CRITICAL)

    def test_take_picture_0(self):
        picture = cam.take_picture(0)
        self.assertTrue(picture.size != 0)


if __name__ == '__main__':
    unittest.main()