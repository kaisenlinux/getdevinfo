# getdevinfo

This repository holds my new getdevinfo module. This module was originally integrated directly into the source code of Wine Autostart, DDRescue-GUI, and WxFixBoot, but has now been separated for ease of maintenance. Because it's on GitLab (https://gitlab.com/hamishmb/getdevinfo) and on PyPI (the Python Package Index) (https://pypi.org/project/getdevinfo/), and released under the GPLv3+, this means other people can use it too.

[![pipeline status](https://gitlab.com/hamishmb/getdevinfo/badges/master/pipeline.svg)](https://gitlab.com/hamishmb/getdevinfo/-/commits/master)
[![PyPI](https://img.shields.io/pypi/v/getdevinfo.svg)](https://pypi.org/project/getdevinfo)
[![Total Downloads on PyPI](https://pepy.tech/badge/getdevinfo)](https://pepy.tech/project/getdevinfo)
[![Downloads/Month on PyPI](https://pepy.tech/badge/getdevinfo/month)](https://pepy.tech/project/getdevinfo)
[![Downloads/Week on PyPI](https://pepy.tech/badge/getdevinfo/week)](https://pepy.tech/project/getdevinfo)

Description of Package
======================
A device information gatherer for Linux, macOS and Cygwin/Windows.

Working on Linux, macOS and Cygwin, this script makes use of lshw, lvdisplay, and blkid (Linux), as well as diskutil (macOS) and smartctl and blkid (Cygwin) to get a comprehensive amount of disk information. This information is available in a structured dictionary for ease of use.

NOTE: Cygwin is supported since v1.1.0, Python 2 is unsupported since v1.0.7.

Features:
---------

Uses the operating system\'s built-in tools to gather lots of helpful information about disks connected to the system. This is returned as a hierarchical python dictionary. For the full details on the format, read the documentation here: https://www.hamishmb.com/html/Docs/getdevinfo.php

Dependencies:
-------------

Linux: The lshw, blkid, lvdisplay, and blockdev commands need to be installed, as well as the beautifulsoup4 (bs4) and lxml Python modules.

macOS: Nothing beyond a default install of Python 3 is needed. bs4 and lxml will still be installed if you install with the Python wheel or with pip.

Cygwin: The smartmontools and util-linux packages need to be installed, as well as the beautifulsoup4 (bs4) and lxml Python modules.

Building
========

Source Distribution
-------------------

Run:

```python setup.py sdist```

Wheels
------

Make sure you've installed the "wheel" package:

```pip3 install wheel```

Universal Wheel
---------------

This is the recommended choice, though GetDevInfo no longer runs on Python 2 from version 1.0.7 onwards,

```python3 setup.py bdist_wheel --universal```

Pure Python Wheel
-----------------

Not sure why you'd do this, but you can run:

```python3 setup.py bdist_wheel```

to acheive this if you want.


Distribution Packages
=====================

You can find these at https://www.launchpad.net/getdevinfo or https://www.hamishmb.com/html/downloads.php?program_name=getdevinfo.

Documentation
=============
This can be found at https://www.hamishmb.com/support/getdevinfo.php.

Running directly from the command line
======================================

Run:

```sudo python3 -m getdevinfo```

Running The Tests
=================

These have to be run as the superuser/administrator, because low-level access to hardware is required to gather information.

The process for running these is the same on both Linux and macOS. Note that prior to version 1.0.7, GetDevInfo ran on Python 2 as well.

Without Coverage Reporting
--------------------------
Change directory to the getdevinfo subfolder, and run:

```sudo python3 ./tests.py```

With Coverage Reporting
-----------------------
Make sure you have installed Coverage.py using pip or your package manager.

Change directory to the getdevinfo subfolder, and run:

```sudo python3 -m coverage run --rcfile=../.coveragerc ./tests.py```

To run the tests. Then run:

```sudo python3 -m coverage report```

To see the report.
