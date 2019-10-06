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
    gi.require_version('Gdk', '3.0')
except Exception as e:
    print(e)
    exit(1)
from gi.repository import Gdk, Gtk
import comun
from basedialog import (generate_title_row,
                        generate_widget_row)
from basedialogwithapply import BaseDialogWithApply
from comun import _
from pageoptions import PageOptions
from textmarkdialog import TextmarkDialog
from tools import get_pages_from_ranges, get_ranges


class PaginateDialog(TextmarkDialog):
    def __init__(self, title=_('Paginate'), filename=None, window=None):
        TextmarkDialog.__init__(self, title, filename, window)

    def set_page(self, page):
        if self.document.get_n_pages() > 0 and \
                page < self.document.get_n_pages() and\
                page >= 0:
            self.no_page = page
            self.show_page.set_text(str(self.no_page + 1))
            self.show_title_page.set_text(str(self.no_page + 1))
            if str(self.no_page) in self.pages.keys():
                self.x = self.pages[str(self.no_page)].text_x
                self.y = self.pages[str(self.no_page)].text_y
                font = self.pages[str(self.no_page)].text_font
                size = self.pages[str(self.no_page)].text_size
                color = self.pages[str(self.no_page)].text_color
                self.button_font.set_font(font + ' ' + str(size))
                self.button_color.set_rgba(color)
                pageOptions = self.pages[str(self.no_page)]
            else:
                self.reset()
                pageOptions = PageOptions(text_x=0, text_y=0,
                                          text_font='Ubuntu', text_size=12,
                                          text_color=Gdk.RGBA(0, 0, 0, 1),
                                          text_text='')
            self.viewport1.set_page(self.document.get_page(self.no_page),
                                    pageOptions)

    def reset(self):
        self.x = 0.0
        self.y = 0.0
        self.button_font.set_font('Ubuntu 12')
        self.button_color = Gtk.ColorButton.new_with_rgba(Gdk.RGBA(0, 0, 0, 1))

    def init_adicional_popover(self):
        BaseDialogWithApply.init_adicional_popover(self)
        self.popover_listbox.add(generate_title_row(_('Pagination'), True))

        self.button_font = Gtk.FontButton()
        self.button_font.set_size_request(165, 25)
        self.button_font.set_font('Ubuntu 12')
        row = generate_widget_row(_('Font'), self.button_font)
        self.popover_listbox.add(row)

        self.button_color = Gtk.ColorButton. new_with_rgba(Gdk.RGBA(0, 0, 0, 1))
        self.button_color.set_size_request(165, 25)
        row = generate_widget_row(_('Color'), self.button_color)
        self.popover_listbox.add(row)

    def on_apply_clicked(self, widget, clear=False):
        if clear:
            self.reset()
        color = self.button_color.get_rgba()
        font = self.button_font.get_font()
        size = int(self.button_font.get_font_desc().get_size()/1000)
        x = self.x
        y = self.y
        if self.check_this.get_active():
            to_update = [self.no_page]
        elif self.check_all.get_active():
            to_update = range(0, self.document.get_n_pages())
        elif self.check_range.get_active():
            to_update = get_pages_from_ranges(
                get_ranges(self.range.get_text()))
        for i in to_update:
            if clear and str(i) in self.pages.keys():
                    del self.pages[str(i)]
            else:
                text = '{}/{}'.format(str(i + 1),
                                      str(self.document.get_n_pages()))
                self.pages[str(i)] = PageOptions(text_text=text,
                    text_color=color, text_font=font, text_size=size,
                    text_x=x, text_y=y)
        if self.no_page in to_update:
            self.preview()

    def preview(self):
        text = '{}/{}'.format(str(self.no_page + 1),
                              str(self.document.get_n_pages()))
        color = self.button_color.get_rgba()
        font = self.button_font.get_font()
        size = int(self.button_font.get_font_desc().get_size()/1000)
        self.viewport1.set_page_options(PageOptions(text_text=text,
                    text_color=color, text_font=font, text_size=size,
                    text_x=self.x, text_y=self.y))

    def on_viewport1_clicked(self, widget, event):
        deltay = abs(self.viewport1.get_allocation().height -
                        self.viewport1.page_height) / 2.0
        deltax = abs(self.viewport1.get_allocation().width -
                        self.viewport1.page_width) / 2.0
        position_x = (event.x - deltax)
        position_y = (event.y - deltay)
        position_x = position_x / self.viewport1.zoom
        position_y = position_y / self.viewport1.zoom
        self.x = position_x
        self.y = position_y
        self.preview()

if __name__ == '__main__':
    dialog = PaginateDialog(filename=comun.SAMPLE)
    dialog.run()
