# -*- coding: utf-8 -*-

# Resource object code
#
# Created by: The Resource Compiler for PyQt5 (Qt v5.15.8)
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore

qt_resource_data = b"\
\x00\x00\x00\x1b\
\x5b\
\x50\x61\x74\x68\x73\x5d\x0a\x50\x72\x65\x66\x69\x78\x20\x3d\x20\
\x6c\x69\x62\x2f\x50\x79\x51\x74\x35\x0a\
"

qt_resource_name = b"\
\x00\x02\
\x00\x00\x07\x84\
\x00\x71\
\x00\x74\
\x00\x03\
\x00\x00\x6c\xa3\
\x00\x65\
\x00\x74\x00\x63\
\x00\x07\
\x08\x74\xa6\xa6\
\x00\x71\
\x00\x74\x00\x2e\x00\x63\x00\x6f\x00\x6e\x00\x66\
"

qt_resource_struct_v1 = b"\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x01\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x02\
\x00\x00\x00\x0a\x00\x02\x00\x00\x00\x01\x00\x00\x00\x03\
\x00\x00\x00\x16\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\
"

qt_resource_struct_v2 = b"\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x01\
\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x02\
\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x0a\x00\x02\x00\x00\x00\x01\x00\x00\x00\x03\
\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x16\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\
\x00\x00\x01\x89\xa4\x57\x42\x57\
"

qt_version = [int(v) for v in QtCore.qVersion().split('.')]
if qt_version < [5, 8, 0]:
    rcc_version = 1
    qt_resource_struct = qt_resource_struct_v1
else:
    rcc_version = 2
    qt_resource_struct = qt_resource_struct_v2

def qInitResources():
    QtCore.qRegisterResourceData(rcc_version, qt_resource_struct, qt_resource_name, qt_resource_data)

def qCleanupResources():
    QtCore.qUnregisterResourceData(rcc_version, qt_resource_struct, qt_resource_name, qt_resource_data)

qInitResources()
