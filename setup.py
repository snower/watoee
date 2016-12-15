# -*- coding: utf-8 -*-
# 14-8-8
# create by: snower

from setuptools import setup


setup(
    name='watoee',
    version='0.0.1',
    packages=['watoee', 'watoee.store', 'watoee.auth', 'watoee.handlers'],
    install_requires=[
        'tornado>=4.1',
        'motor>=1.1'
    ],
    author=['snower'],
    author_email=['sujian199@gmail.com'],
    url='https://github.com/snower/watoee',
    license='MIT',
    keywords=[
        "tornado", "mongodb"
    ],
    description='Tornado asynchronous rest api',
    long_description=open("README.md").read(),
    zip_safe=False,
)
