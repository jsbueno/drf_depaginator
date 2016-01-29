# coding: utf-8

from setuptools import setup

setup(
    name = 'drf_depaginator',
    version = "0.3.2",
    package_dir = { '': 'src'},
    license = "APACHE",
    author = "João S. O. Bueno",
    author_email = "gwidion@gmail.com",
    description = "Tool to create a record generator for all results from a Django Rest Framework API",
    keywords = "django rest api consumer generator pagination depagination",
    py_modules = ['drf_depaginator'],
    tests_require = ['pytest'],
    url = 'https://github.com/jsbueno/drf_depaginator',
    long_description = open('README.rst').read(),
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Framework :: Django :: 1.8",
        "Framework :: Django :: 1.9",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ]
)
