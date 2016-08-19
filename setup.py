#!/usr/bin/env python

from setuptools import setup

setup(
      name='ftntlib',
      version='0.4.0.dev13',
      description='Python modules to interact with Fortinet products',
      install_requires=['requests','suds-jurko','lxml'],
      author='Ashton Turpin',
      author_email='',
      url='https://fndn.fortinet.net',
      packages=['ftntlib'],
      )
