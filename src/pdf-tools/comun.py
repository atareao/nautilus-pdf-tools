#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of nautilus-pdf-tools
#
# Copyright (C) 2012-2018 Lorenzo Carbonell
# <lorenzo.carbonell.cerezo@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gi
try:
    gi.require_version('GdkPixbuf', '2.0')
except Exception as e:
    print(e)
    exit(1)
import os
import locale
import gettext
import sys
from gi.repository import GdkPixbuf
import collections

USRDIR = '/usr/share/'


def is_package():
    return (__file__.startswith(USRDIR) or os.getcwd().startswith(USRDIR))


APP = 'nautilus-pdf-tools'
APPNAME = 'Nautilus PDF Tools'

if is_package():
    ROOTDIR = '/usr/share/'
    LANGDIR = os.path.join(ROOTDIR, 'locale-langpack')
    APPDIR = os.path.join(ROOTDIR, 'nautilus-python/extensions/pdf-tools/')
    ICONDIR = os.path.join(ROOTDIR, 'icons')
    CHANGELOG = os.path.join(APPDIR, 'changelog')
else:
    ROOTDIR = os.path.dirname(__file__)
    LANGDIR = os.path.normpath(os.path.join(ROOTDIR, '../../po'))
    APPDIR = ROOTDIR
    DATADIR = os.path.normpath(os.path.join(ROOTDIR, '../../data'))
    ICONDIR = os.path.normpath(os.path.join(ROOTDIR, '../../data/icons'))
    SOCIALDIR = os.path.normpath(os.path.join(ROOTDIR, '../../data/social'))
    DEBIANDIR = os.path.normpath(os.path.join(ROOTDIR, '../../debian'))
    CHANGELOG = os.path.join(DEBIANDIR, 'changelog')

ICON = os.path.join(ICONDIR, 'updf.svg')

f = open(CHANGELOG, 'r')
line = f.readline()
f.close()
pos = line.find('(')
posf = line.find(')', pos)
VERSION = line[pos + 1: posf].strip()
if not is_package():
    VERSION = VERSION + '-src'
try:
    current_locale, encoding = locale.getdefaultlocale()
    language = gettext.translation(APP, LANGDIR, [current_locale])
    language.install()
    if sys.version_info[0] == 3:
        _ = language.gettext
    else:
        _ = language.ugettext
except Exception as e:
    print(e)
    _ = str
APPNAME = _(APPNAME)


RESOLUTION = 110.0 / 72.0
MMTOPIXEL = 3.779527559055
MMTOPDF = 4
MMTOPNG = 1169.0 / 842.0
TOP = -1
MIDLE = 0
BOTTOM = 1
LEFT = -1
CENTER = 0
RIGHT = 1
ROTATE_000 = 0.0
ROTATE_090 = 90.0
ROTATE_180 = 180.0
ROTATE_270 = 270.0

EXTENSIONS_TO = ['.djvu', '.html', '.txt', '.jpg', '.png']
EXTENSIONS_FROM = ['.bmp', '.gif', '.jpg', '.jpeg', '.jp2', '.jpx', '.pcx',
                   '.png', '.pnm', '.ras', '.tif', '.tiff', '.xbm', '.xpm']
MIMETYPES_TO = ['image/vnd.djvu', 'text/html', 'text/plain', 'image/jpeg',
                'image/png']
MIMETYPES_FROM = ['image/x-ms-bmp', 'image/gif', 'image/jpeg', 'image/jp2',
                  'image/jpx', 'image/pcx', 'image/png',
                  'image/x-portable-anymap', 'image/x-cmu-raster',
                  'image/tiff', 'image/x-xpixmap']

MIMETYPES_PDF = ['application/pdf']
MIMETYPES_PNG = ['image/png']
MIMETYPES_IMAGE = {}

all_mime_types = []
all_paterns = []
for aformat in GdkPixbuf.Pixbuf.get_formats():
    mime_types = []
    patterns = []
    for amimetype in aformat.get_mime_types():
            mime_types.append(amimetype)
            all_mime_types.append(amimetype)
    for extension in aformat.get_extensions():
            patterns.append('*.' + extension)
            all_paterns.append('*.' + extension)
    MIMETYPES_IMAGE[aformat.get_description()] = {
        'mimetypes': mime_types, 'patterns': patterns}
MIMETYPES_IMAGE[_('ALL')] = {
    'mimetypes': all_mime_types, 'patterns': all_paterns}
MIMETYPES_IMAGE = collections.OrderedDict(sorted(MIMETYPES_IMAGE.items()))
