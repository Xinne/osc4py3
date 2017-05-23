#!/bin/env python
# -*- coding: utf-8 -*-
# Author: Laurent Pointal <laurent.pointal@limsi.fr> <laurent.pointal@laposte.net>

from distutils.core import setup
import sys
import io

setup(
    name='osc4py3',
    version='1.0.1',
    author='Laurent Pointal',
    author_email='laurent.pointal@limsi.fr',
    url='http://perso.limsi.fr/pointal/dev:osc4py3',
    download_url='https://sourcesup.renater.fr/projects/osc4py3/',
    description='Python3 package for Open Sound Control (OSC) communications.',
    packages=['osc4py3', 'osc4py3.tests', 'osc4py3.demos'],
    keywords=['communication', 'sound', "network", ""],
    license='CEA CNRS Inria Logiciel Libre License, version 2.1 (CeCILL-2.1)',
    classifiers=[
                'Development Status :: 5 - Production/Stable',
                'Intended Audience :: Science/Research',
                'Natural Language :: English',
                'Operating System :: OS Independent',
                'Programming Language :: Python :: 3',
                'License :: OSI Approved :: CEA CNRS Inria Logiciel Libre License, version 2.1 (CeCILL-2.1)',
                'Topic :: Scientific/Engineering',
                'Topic :: Software Development :: Libraries :: Python Modules',
                'Topic :: Text Processing :: Linguistic',
                'Topic :: Multimedia :: Sound/Audio',
             ],
    long_description=io.open("README.txt", encoding='utf-8').read(),
    )

