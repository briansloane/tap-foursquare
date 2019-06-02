#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='tap-foursquare',
      version='0.0.1',
      description='Singer.io tap for extracting data from the Foursquare API',
      author='bsloane@gmail.com',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['tap_foursquare'],
      install_requires=[
          'singer-python==5.2.1',
          'foursquare==1!2019.2.16'
      ],
      entry_points='''
          [console_scripts]
          tap-foursquare=tap_foursquare:main
      ''',
      packages=['tap_foursquare'],
      include_package_data=True,
)
