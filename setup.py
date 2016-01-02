from setuptools import setup, find_packages

setup (
       name='surveillance',
       version='0.1',
       packages=find_packages(),

       # Declare your packages' dependencies here, for eg:
       install_requires=['cv2>=3'],

       # Fill in these to make your Egg ready for upload to
       # PyPI
       author='Maikel Nadolski',
       author_email='maikel.nadolski@googlemail.com',

       #summary = 'Just another Python package for the cheese shop',
       url='',
       license='Apache License, Version 2.0',
       long_description='Various Scripts to control the camera in a car.',

       # could also include long_description, download_url, classifiers,
       # etc.

  
       )