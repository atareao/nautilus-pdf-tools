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
    gi.require_version('Gtk', '3.0')
except Exception as e:
    print(e)
    exit(1)
from gi.repository import Gtk
import comun
from comun import _
from watermarkdialog import WatermarkDialog
from pageoptions import PageOptions
from basedialogwithapply import BaseDialogWithApply
from basedialog import generate_title_row, generate_spinbutton_row
from basedialog import generate_button_row


class SignDialog(WatermarkDialog):
    def __init__(self, filename=None, window=None):
        WatermarkDialog.__init__(self, _('Sign'), filename, window)


    def set_page(self, page):
        if self.document.get_n_pages() > 0 and \
                page < self.document.get_n_pages() and\
                page >= 0:
            self.no_page = page
            self.show_page.set_text(str(self.no_page + 1))
            self.show_title_page.set_text(str(self.no_page + 1))
            if str(self.no_page) in self.pages.keys():
                self.x = self.pages[str(self.no_page)].image_x
                self.y = self.pages[str(self.no_page)].image_y
                self.zoom_entry.set_value(self.pages[str(self.no_page)].image_zoom * 100.0)
                self.file_entry.set_label(self.pages[str(self.no_page)].image_file)
                pageOptions = self.pages[str(self.no_page)]
            else:
                self.reset()
                pageOptions = PageOptions(image_x=0, image_y=0, image_zoom=1.0,
                                          image_file=None)
            self.viewport1.set_page(self.document.get_page(self.no_page),
                                    pageOptions)

    def reset(self):
        self.x = 0.0
        self.y = 0.0
        self.zoom_entry.set_value(100.0)
        self.file_entry.set_label(_('Select signature file'))


    def init_adicional_popover(self):
        BaseDialogWithApply.init_adicional_popover(self)
        self.popover_listbox.add(generate_title_row(_('Signature'), True))

        self.zoom_entry, row = generate_spinbutton_row(_('Zoom'), None)
        self.zoom_entry.set_adjustment(Gtk.Adjustment(1, 100, 1000, 1, 100, 0))
        self.popover_listbox.add(row)
        self.file_entry, row = generate_button_row(
            _('Signature'), self.on_button_watermark_clicked)
        self.file_entry.set_label(_('Select signature file'))
        self.popover_listbox.add(row)

if __name__ == '__main__':
    dialog = SignDialog(comun.SAMPLE)
    dialog.run()
