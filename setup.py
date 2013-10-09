#!/usr/bin/env python

'''
    This file is part of speedtest-reporter.

    Speedtest-reporter is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Speedtest-reporter is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with speedtest-reporter. If not, see <http://www.gnu.org/licenses/>
'''



from setuptools import setup, find_packages
 
import speedtest_reporter
 
setup(
 
    name='speedtest-reporter',
 
    version=speedtest_reporter.__version__,
 
    packages=find_packages(),
 
    author="Olivier Watte - GwadaLUG",
 
    author_email="olivier.watte@gmail.com",
 
    description="internet connection speedtest with results recorded and published",
 
    long_description=open('README.rst').read(),
 
    install_requires=['pygal', 'speedtest-cli'],
 
    include_package_data=True,
 
    url='https://github.com/owatte/speedtest-reporter',
 
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 1 - Planning",
        "Environment :: Console",
        "Intended Audience :: System Administrators"
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Topic :: System :: Networking :: Monitoring",
    ],
 
    entry_points = {
        'console_scripts': [
            'speedtest-reporter = speedtest_reporter:main',
        ],
    },
)
