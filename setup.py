#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  6 15:53:12 2022

@author: milasiunaite
"""

import distutils.core
import Cython.Build
import numpy

distutils.core.setup(
    ext_modules=Cython.Build.cythonize("optimise.pyx", annotate=True),
    include_dirs=[numpy.get_include()])
