#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of nautilus-pdf-tools
#
# Copyright (c) 2012 Lorenzo Carbonell Cerezo <a.k.a. atareao>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
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
    gi.require_version('Gtk', '3.0')
except ValueError as e:
    print(e)
    exit(1)
from gi.repository import Gtk
from basicdialog import BasicDialog
from comun import _

class ReduceDialog(BasicDialog):
    def __init__(self, title, window):
        BasicDialog.__init__(self, title, window)
        self.set_size_request(200, 150)

    def init_ui(self):
        BasicDialog.init_ui(self)

        label1 = Gtk.Label(_('Image resolution') + ':')
        label1.set_alignment(0, .5)
        self.grid.attach(label1, 0, 0, 1, 1)

        label2 = Gtk.Label(_('Append to file') + ':')
        label2.set_alignment(0, .5)
        self.grid.attach(label2, 0, 1, 1, 1)

        self.dpi_entry = Gtk.Entry()
        self.dpi_entry.set_tooltip_text(_('Set dpi to reduce file'))
        self.dpi_entry.set_text('100')
        self.grid.attach(self.dpi_entry, 1, 0, 1, 1)

        self.dpi_entry.set_activates_default(True)
        self.dpi_entry.grab_focus()

        self.append_entry = Gtk.Entry()
        self.append_entry.set_tooltip_text(_('Append to file to create output filename'))
        self.append_entry.set_text('_reduced')
        self.grid.attach(self.append_entry, 1, 1, 1, 1)

        self.show_all()

    def get_dpi(self):
        return self.dpi_entry.get_text()

    def get_append(self):
        return self.append_entry.get_text()


if __name__ == '__main__':
    dialog = ReduceDialog('Test', None)
    dialog.run()
