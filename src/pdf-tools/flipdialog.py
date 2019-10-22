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

import comun
from basedialog import (generate_check_row, generate_entry_row,
                        generate_separator_row, generate_swith_row,
                        generate_title_row)
from basedialogwithapply import BaseDialogWithApply
from comun import _
from pageoptions import PageOptions
from tools import get_pages_from_ranges, get_ranges


class FlipDialog(BaseDialogWithApply):
    def __init__(self, filename=None, window=None):
        BaseDialogWithApply.__init__(self, _('Rotate and flid PDF'),
                                     filename, window)

    def set_page(self, page):
        if self.document.get_n_pages() > 0 and \
                page < self.document.get_n_pages() and\
                page >= 0:
            self.no_page = page
            self.show_page.set_text(str(self.no_page + 1))
            self.show_title_page.set_text(str(self.no_page + 1))
            if str(self.no_page) in self.pages.keys():
                rotation_angle = self.pages[str(self.no_page)].rotation_angle
                flip_horizontal = self.pages[str(self.no_page)].flip_horizontal
                flip_vertical = self.pages[str(self.no_page)].flip_vertical
                self.check_horizontal.set_active(flip_horizontal)
                self.check_vertical.set_active(flip_vertical)
                if rotation_angle == 0.0:
                    self.rotate_0.set_active(True)
                elif rotation_angle == 1.0:
                    self.rotate_90.set_active(True)
                elif rotation_angle == 2.0:
                    self.rotate_180.set_active(True)
                elif rotation_angle == 3.0:
                    self.rotate_270.set_active(True)
                pageOptions = self.pages[str(self.no_page)]
            else:
                rotation_angle = 0
                flip_horizontal = False
                flip_vertical = False
                self.check_horizontal.set_active(False)
                self.check_vertical.set_active(False)
                self.rotate_0.set_active(True)
                pageOptions = PageOptions(flip_horizontal=False,
                                          flip_vertical=False,
                                          rotation_angle=0.0)

            self.viewport1.set_page(self.document.get_page(self.no_page),
                                    pageOptions)

    def init_adicional_popover(self):
        BaseDialogWithApply.init_adicional_popover(self)
        self.popover_listbox.add(generate_title_row(_('Rotate'), True))

        self.rotate_0, row = generate_check_row(
            '0', None, None)
        self.popover_listbox.add(row)
        self.rotate_90, row = generate_check_row(
            '90', self.rotate_0, None)
        self.popover_listbox.add(row)
        self.rotate_180, row = generate_check_row(
            '180', self.rotate_0, None)
        self.popover_listbox.add(row)
        self.rotate_270, row = generate_check_row(
            '270', self.rotate_0, None)
        self.popover_listbox.add(row)

        self.popover_listbox.add(generate_separator_row())
        self.popover_listbox.add(generate_title_row(_('Flip'), True))

        self.check_vertical, row = generate_swith_row(
            _('Vertical'), None)
        self.popover_listbox.add(row)
        self.check_horizontal, row = generate_swith_row(
            _('Horizontal'), None)
        self.popover_listbox.add(row)

    def reset(self):
        self.check_horizontal.set_active(False)
        self.check_vertical.set_active(False)
        self.rotate_0.set_active(True)

    def on_apply_clicked(self, widget, clear=False):
        if clear:
            self.reset()
        flip_horizontal = self.check_horizontal.get_active()
        flip_vertical = self.check_vertical.get_active()
        if self.rotate_90.get_active():
            rotation_angle = 1.0
        elif self.rotate_180.get_active():
            rotation_angle = 2.0
        elif self.rotate_270.get_active():
            rotation_angle = 3.0
        else:
            rotation_angle = 0.0
        to_update = []
        if self.check_this.get_active():
            to_update = [ self.no_page ]
        elif self.check_all.get_active():
            to_update = range(0, self.document.get_n_pages())
        elif self.check_range.get_active():
            to_update = get_pages_from_ranges(
                get_ranges(self.range.get_text()))
        for i in to_update:
            if clear and str(i) in self.pages.keys():
                del self.pages[str(i)]
            else:
                self.pages[str(i)] = PageOptions(rotation_angle,
                                                 flip_horizontal,
                                                 flip_vertical)
        if self.no_page in to_update:
            self.preview()

    def preview(self):
        flip_horizontal = self.check_horizontal.get_active()
        flip_vertical = self.check_vertical.get_active()
        if self.rotate_90.get_active():
            rotation_angle = 1.0
        elif self.rotate_180.get_active():
            rotation_angle = 2.0
        elif self.rotate_270.get_active():
            rotation_angle = 3.0
        else:
            rotation_angle = 0.0
        self.viewport1.set_page_options(
            PageOptions(flip_horizontal=flip_horizontal,
                        flip_vertical=flip_vertical,
                        rotation_angle=rotation_angle))


if __name__ == '__main__':
    dialog = FlipDialog(comun.SAMPLE)
    dialog.run()
