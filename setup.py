#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="purpleair_data_logger",
    version="0.5",
    license="MIT",
    author="Carlos Santos",
    author_email="email@example.com",
    packages=find_packages("src"),
    package_dir={"": "src"},
    url="https://github.com/carlkid1499/purpleair_data_logger",
    keywords="example project",
    install_requires=[
          "pg8000",
          "requests"
      ],

)