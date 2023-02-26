#!/usr/bin/env python3
from setuptools import setup
import os


def read_file(filename):
    with open(
        os.path.join(os.path.dirname(__file__), filename), encoding="utf-8"
    ) as file:
        return file.read()


setup(
    name="purpleair_data_logger",
    version="1.2.0",
    license="MIT",
    author="Carlos Santos",
    author_email="27721404+carlkid1499@users.noreply.github.com",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    packages=["purpleair_data_logger"],
    url="https://github.com/carlkid1499/purpleair_data_logger",
    keywords=[
        "purpleair_data_logger",
        "purple air",
        "purple air data logger",
        "PurpleAirPSQLDataLogger",
        "PurpleAirCSVDataLogger",
        "purple air api",
        "PurpleAirSQLiteDataLogger",
    ],
    install_requires=["pg8000==1.29.4", "requests", "purpleair_api==1.0.1"],
    platforms=["Windows 32/64", "Linux 32/64", "MacOS 32/64"],
)
