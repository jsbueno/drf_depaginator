# coding: utf-8

from setuptools import setup

setup(
    name = 'drf_depaginator',
    version = "0.3",
    package_dir = { '': 'src'},
    license = "APACHE",
    author = "João S. O. Bueno",
    author_email = "gwidion@gmail.com",
    description = "Tool to create a record generator for all results from a Django Rest Framework API",
    keywords = "django rest api consumer generator pagination depagination",
    py_modules = ['drf_depaginator'],
    tests_require = ['pytest'],
    url = 'https://github.com/jsbueno/drf_depaginator',
    long_description = open('README.rst').read()
)
