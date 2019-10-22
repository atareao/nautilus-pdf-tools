#!/usr/bin/env python3
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
    gi.require_version('Gtk', '3.0')
except ValueError as e:
    print(e)
    exit(1)
from gi.repository import Gtk

from basicdialog import BasicDialog
from comun import MIMETYPES_IMAGE, _


class ConvertDialog(BasicDialog):
    def __init__(self, window=None):
        BasicDialog.__init__(self, _('Convert to'), window)
        self.set_size_request(300, 80)

    def init_ui(self):
        BasicDialog.init_ui(self)

        options = Gtk.ListStore(str)
        for extension in MIMETYPES_IMAGE.keys():
            if extension != _('ALL'):
                options.append([extension])
        label = Gtk.Label(_('Convert to') + ':')
        self.grid.attach(label, 0, 0, 1, 1)
        self.convert_to = Gtk.ComboBox.new_with_model_and_entry(options)
        self.convert_to.set_entry_text_column(0)
        self.convert_to.set_active(0)
        self.grid.attach(self.convert_to, 1, 0, 1, 1)

    def get_convert_to(self):
        tree_iter = self.convert_to.get_active_iter()
        if tree_iter is not None:
            model = self.convert_to.get_model()
            return model[tree_iter][0]
        return 'PNG'


if __name__ == '__main__':
    dialog = ConvertDialog()
    dialog.run()
