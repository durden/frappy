#!/usr/bin/env python

from distutils.core import setup

setup(name='Frappy',
      version='0.1',
      description='Framework for creating Web APIs in Python',
      author='Luke Lee',
      author_email='durdenmisc@gmail.com',
      url='http://github.com/durden/frappy',
      packages=['frappy', 'frappy.services', 'frappy.core',
                'frappy.services.twitter']
    )
