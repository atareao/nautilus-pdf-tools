#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of nautilus-pdf-tools
#
# Copyright (c) 2012-2019 Lorenzo Carbonell Cerezo <a.k.a. atareao>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import gi
try:
    gi.require_version('GdkPixbuf', '2.0')
except ValueError as e:
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
    ICONDIR = os.path.join(APPDIR, 'icons')
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
SAMPLE = os.path.abspath('sample/sample.pdf')

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
MINIVIEWTOPDF = 1.38
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
ALL_MIMETYPES_IMAGE = all_mime_types
