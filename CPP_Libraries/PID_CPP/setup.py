#!/usr/bin/env python3

from setuptools import setup, Extension

encoder_module = Extension(
    "_PID",
    sources=["PID_wrap.cxx", "PID.cpp"],
    # libraries=["pigpio"]
)

setup(
    name="PID",
    author="Kethan Vegunta",
    description="PID class in C++.",
    ext_modules=[encoder_module],
    py_modules=["PID"],
)
