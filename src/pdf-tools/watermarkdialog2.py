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
import os
import comun
from comun import _
from tools import get_ranges
from tools import get_pages_from_ranges
from basedialog import BaseDialog, generate_separator_row, generate_title_row
from basedialog import generate_swith_row, generate_check_entry_row
from basedialog import generate_check_row, generate_entry_row


class PageOptions():
    def __init__(self, x, y, zoom, afile):
        self.x = x
        self.y = y
        self.zoom = zoom
        self.file = afile

class WatermarkDialog(BaseDialog):
    def __init__(self, filename=None, window=None):
        BaseDialog.__init__(self, _('Watermark'), filename, window)
    
    def set_page(self, page):
        if self.document.get_n_pages() > 0 and \
                page < self.document.get_n_pages() and\
                page >= 0:
            self.no_page = page
            self.show_page.set_text(str(self.no_page + 1))
            self.show_title_page.set_text(str(self.no_page + 1))
            self.viewport1.set_page(self.document.get_page(self.no_page))
            if str(self.no_page) in self.pages.keys():
                self.update_preview(self.pages[str(self.no_page)].x,
                                    self.pages[str(self.no_page)].y,
                                    self.pages[str(self.no_page)].zoom,
                                    self.pages[str(self.no_page)].file)

    def init_adicional_popover(self):
        self.popover_listbox.add(generate_title_row(_('Apply'), True))

        self.check_this, row = generate_check_row(_('This page'), None,
                                                  self.slider_on_value_changed)
        self.popover_listbox.add(row)
        self.check_all, row = generate_check_row(_('All'), self.check_this,
                                                  self.slider_on_value_changed)
        self.popover_listbox.add(row)
        self.check_range, self.range, row = generate_check_entry_row(
            _('Range'), self.check_this, self.slider_on_value_changed)
        self.popover_listbox.add(row)

        self.popover_listbox.add(generate_separator_row())

        self.popover_listbox.add(generate_title_row(_('Rotate'), True))

    def slider_on_value_changed(self, widget, value, name):
        flip_horizontal = self.check_horizontal.get_active()
        flip_vertical = self.check_vertical.get_active()
        if name == '90':
            rotation_angle = 1.0
        elif name == '180':
            rotation_angle = 2.0
        elif name == '270':
            rotation_angle = 3.0
        else:
            rotation_angle = 0.0
        update = False
        if self.check_this.get_active():
            update = True
            self.pages[str(self.no_page)] = PageOptions(rotation_angle,
                                                        flip_horizontal,
                                                        flip_vertical)
        elif self.check_all.get_active():
            update = True
            for i in range(0, self.document.get_n_pages()):
                self.pages[str(i)] = PageOptions(rotation_angle,
                                                 flip_horizontal,
                                                 flip_vertical)
        elif self.check_range.get_active():
            text = self.range.get_text()
            if text:
                ranges = get_ranges(text)
                pages = get_pages_from_ranges(ranges)
                update = (str(self.no_page) in self.pages.keys())
                for i in pages:
                    self.pages[str(i)] = PageOptions(rotation_angle,
                                                     flip_horizontal,
                                                     flip_vertical)
        if update:
            self.viewport1.rotation_angle = rotation_angle
            self.viewport1.flip_horizontal = flip_horizontal
            self.viewport1.flip_vertical = flip_vertical
            self.viewport1.queue_draw()

    def update_preview(self, x, y, zoom, file_watermark):
        if file_watermark and os.path.exists(file_watermark):
            self.viewport1.set_image(file_watermark)
            self.viewport1.image_zoom = float(zoom / 100.0)
            self.viewport1.image_margin_width = x
            self.viewport1.image_margin_height = y
            self.viewport1.refresh()

if __name__ == '__main__':
    dialog = WatermarkDialog(comun.SAMPLE)
    dialog.run()
