# setup.py
from setuptools import setup
from Cython.Build import cythonize
import numpy

setup(
    name = "Cython functions",
    ext_modules = cythonize("cython_functions.pyx"),
    include_dirs=[numpy.get_include()]
)
