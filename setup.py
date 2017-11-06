#!/usr/bin/env python

from setuptools import setup

setup(
      name='ftntlib',
      version='0.4.0.dev14',
      description='Python modules to interact with Fortinet products',
      install_requires=['requests','suds-jurko','lxml'],
      author='Original: Ashton Turpin, Current: Jean-Pierre Forcioli',
      author_email='jpforcioli@fortinet.com',
      url='https://fndn.fortinet.net',
      packages=['ftntlib'],
      )
