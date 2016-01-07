import unittest
import gnupg
import cv2
import taxicam.camera
import filecmp
import os.path # does file exist

class TestCameraMethods(unittest.TestCase):
	def setUp(self):
		self.camera = taxicam.camera.Camera(framerate=1)
	
	def test_get_camera(self):
		cap = self.camera.get_camera()
		self.assertTrue(cap.isOpened())
		if cap.isOpened():
			cap.release()

	def test_take_picture(self):
		picture = self.camera.take_picture()
		self.assertTrue(picture.size > 0)

	def test_scan_face(self):
		img1 = cv2.imread('pictures/example/Foto.png',0) # Has a face
		detected_faces_img1 = self.camera.detect_faces(img1)
		self.assertTrue(detected_faces_img1 > 0)

	def test_scan_picture(self):
		img2 = cv2.imread('pictures/example/Sign.png',0) # Does not have a face
		detected_faces_img2 = self.camera.detect_faces(img2)
		self.assertTrue(detected_faces_img2 == 0)

	def test_encrypt_picture(self):
		img = cv2.imread('pictures/example/Foto.png',0) # Has a face
		(ret, data) = cv2.imencode('.png', img)
		data = data.tostring()
		gpg = gnupg.GPG(gnupghome='')
		keys = gpg.scan_keys('public_keys')  
		encrypted_pic = img.tostring() 
		for key in keys:
			encrypted = gpg.encrypt(data, key['fingerprint'])
			encrypted_pic = encrypted.data
		encypt_call = self.camera.encrypt_picture(img, "/pictures/example/enc_picture.png.gpg") 
		self.assertTrue(filecmp.cmp(encrypted_pic,encypt_call))

	def test_archive_file(self):
		target_directory='pictures/test/archive'
		target_filename='testarchive'
		source='pictures/example/Foto.png'
		self.camera.archive_file(source, target_directory, target_filename)
		self.assertTrue(os.path.exists(target_directory + '/' + target_filename))

