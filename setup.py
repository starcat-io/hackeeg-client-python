#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import os
import sys
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

about = {}


with open(os.path.join(here, "hackeeg", "__version__.py")) as f:
    exec(f.read(), about)

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = "\n" + f.read()

setup(name='hackeeg',
      version=about["__version__"],
      description='Python client library for HackEEG Arduino Due shield',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='http://github.com/starcat-io/hackeeg-client-python',
      author='Starcat LLC',
      author_email='adam@starcat.io',
      license='Apache 2.0',
      packages=['hackeeg'],
      install_requires=[
			"pyserial",
			"bitstring",
			"numpy",
			"jsonlines",
			"msgpack",
			"autopep8",
			"gnureadline",
			"pylsl",
      ],
      zip_safe=False)
