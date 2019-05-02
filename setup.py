#!/usr/bin/env python

from distutils.core import setup

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
