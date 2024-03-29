#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Device Information Obtainer Package
# This file is part of GetDevInfo.
# Copyright (C) 2013-2022 Hamish McIntyre-Bhatty
# GetDevInfo is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3 or,
# at your option, any later version.
#
# GetDevInfo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GetDevInfo.  If not, see <http://www.gnu.org/licenses/>.
"""
The GetDevInfo module.
"""

from __future__ import absolute_import
from . import getdevinfo

def get_info():
    """Wrapper for getdevinfo.get_info()"""
    return getdevinfo.get_info()

if __name__ == "__main__":
    getdevinfo.run()
