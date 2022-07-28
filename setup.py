#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="purpleair_data_logger",
    version="0.0.5a1",
    license="MIT",
    author="Carlos Santos",
    author_email="email@example.com",
    packages=find_packages("purpleair_data_logger"),
    url="https://github.com/carlkid1499/purpleair_data_logger",
    keywords=["purpleair_data_logger", "purpleair", "data logger"],
    install_requires=[
        "pg8000",
        "requests"
    ],
)
