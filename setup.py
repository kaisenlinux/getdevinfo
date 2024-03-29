#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Setup module for GetDevInfo.
"""

import shutil
import platform

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

if platform.system() == "Linux":
    LINUX = True
    dependencies = ("lshw", "blkid", "lsblk", "lvdisplay", "dd", "strings", "blockdev")

elif "CYGWIN" in platform.system():
    LINUX = True
    CYGWIN = True
    dependencies = ("/sbin/blkid", "/usr/sbin/smartctl", "cygpath", "dd", "strings")

elif platform.system() == "Darwin":
    LINUX = False
    dependencies = ()

#Check that non-python dependencies are available.
print("Checking non-Python dependencies are present...")

failed_list = []

for cmd in dependencies:
    if shutil.which(cmd) is None:
        failed_list.append(cmd)

#Error out with a warning if any dependencies weren't found.
if failed_list:
    print("Dependency check failed!")
    print("Please install the following programs/packages:")
    print(', '.join(failed_list))
    print("\n\nInstall aborted.")
    raise RuntimeError("Dependencies not met")

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='getdevinfo',
    version='2.0.0',
    description='A device information gatherer for Linux, macOS, and Cygwin/Windows',
    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://www.hamishmb.com/',
    author='Hamish McIntyre-Bhatty',
    license='GPLv3+',

    classifiers=[
        #The most important stuff.
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',

        #Python versions.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',

        #Misc.
        'Environment :: MacOS X',
        'Environment :: Console',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities'

    ],

    keywords='devices hardware',
    packages=find_packages(),
    install_requires=['beautifulsoup4', 'lxml'],
    python_requires='>=2.8, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
)
