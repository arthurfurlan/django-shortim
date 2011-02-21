#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Strongly inspired (copied :D) from:
# http://jacobian.org/writing/django-apps-with-buildout/
#


import os

from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="django-shortim",
    version="1.2.1",
    url='http://github.com/valvim/django-shortim',
    license='GPLv3',
    description=("Django application for creating short URLs. "
                 "This code is currently running on http://va.mu."),
    author='Arthur Furlan',
    long_description = read('README'),
    author_email='afurlan@afurlan.org',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=['setuptools'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
