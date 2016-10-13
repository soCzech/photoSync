#!/usr/bin/env python

from photoSync import __ver__
try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

setup(
	name="photoSync",
	version=__ver__,
	description="Flickr and Google Drive photo synchronization in Python",
	long_description=open("README.md").read(),
	author="Tomáš Souček",
	author_email="soucek.gns@gmail.com",
	url="https://github.com/soCzech",
	packages=[
		"photoSync"
	],
	license="LICENSE.txt",
	install_requires=[
		"requests >= 2.2.0"
	],
)
