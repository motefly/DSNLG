#!/usr/bin/env python

from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()

setup(name='nalangen',
    version='0.1',
    description='Generating parametrized sentences',
    url='https://github.com/guhur/nalangen',
    long_description=readme(),
    license='GNU GPL',
    author='Pierre-Louis Guhur',
    author_email='pierre-louis.guhur@inria.fr',
    packages=find_packages(exclude=['tests', 'doc']),
    zip_safe=False,
    include_package_data=True,
    install_requires=[],
     )
