#!/usr/bin/env python

from setuptools import setup

packages = ['Calibration',
            'Calibration.Calibration',
            'Calibration.general',
            'Calibration.Namelist_management',
            'Calibration.Run_JULES']

setup(name='Calibration',
      version='0.1',
      description='A package for calibrating JULES namelist variables',
      author='Cale Baguley',
      url='https://github.com/CaleBaguley/Jules_Namelist_management',
      packages=packages
      )
