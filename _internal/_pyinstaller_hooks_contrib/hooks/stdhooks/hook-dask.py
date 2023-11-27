#-----------------------------------------------------------------------------
# Copyright (c) 2005-2020, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------
"""
Collects in-repo dask.yaml and dask-schema.yaml data files.
"""

from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('dask', includes=['*.yml', '*.yaml'])
