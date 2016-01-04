from setuptools import setup, find_packages
from pip.req import parse_requirements

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements('requirements.txt', session=False)

# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
reqs = [str(ir.req) for ir in install_reqs]

setup (
       name='surveillance',
       version='0.1',
       packages=find_packages(),
       description='Various Scripts to control the camera in a car.',

       # Declare your packages' dependencies here, for eg:
       install_requires=reqs,

       # Fill in these to make your Egg ready for upload to
       # PyPI
       author='Maikel Nadolski',
       author_email='maikel.nadolski@googlemail.com',

       #summary = 'Just another Python package for the cheese shop',
       url='https://github.com/maikel/taxicam',
       license='Apache License, Version 2.0',
       long_description='Various Scripts to control the camera in a car.',

       # could also include long_description, download_url, classifiers,
       # etc.

  
       )