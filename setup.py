#!/usr/bin/env python

import os
from setuptools import setup


# Read function
def safe_read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ""

# Setup
setup(
    name="rpm2",
    version="0.1.0",
    packages=['rpm2'],
    description="Provide a setuptools command called bdist_rpm2",
    long_description=safe_read("README.md"),
    entry_points={'distutils.commands': ['bdist_rpm2 = rpm2.bdist_rpm2:bdist_rpm2']},

    author="Vincent Michel",
    author_email="vincent.michel@maxlab.lu.se",
    license="GPLv3",
    url="http://www.maxlab.lu.se")
