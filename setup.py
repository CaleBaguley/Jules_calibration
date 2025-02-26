#!/usr/bin/env python

from setuptools import setup

packages = ['src',
            'src.Calibration',
            'src.general',
            'src.Namelist_management',
            'src.Run_JULES']

setup(name='JULES_Namelist_management',
      version='0.1',
      description='A package for calibrating JULES namelist variables',
      author='Cale Baguley',
      url='https://github.com/CaleBaguley/Jules_Namelist_management',
      packages=packages
      )
