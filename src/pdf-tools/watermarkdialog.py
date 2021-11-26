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
import os
import comun
from basedialog import (generate_button_row,
                        generate_spinbutton_row, generate_title_row)
from basedialogwithapply import BaseDialogWithApply
from comun import MIMETYPES_IMAGE, _
from pageoptions import PageOptions
from tools import get_pages_from_ranges, get_ranges, update_preview_cb


class WatermarkDialog(BaseDialogWithApply):
    def __init__(self, title=_('Watermark'), filename=None, window=None):
        BaseDialogWithApply.__init__(self, title, filename, window)
        self.x = 0.0
        self.y = 0.0
        self.viewport1.connect('button-release-event',
                               self.on_viewport1_clicked)

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
        self.file_entry.set_label(_('Select watermark file'))


    def init_adicional_popover(self):
        BaseDialogWithApply.init_adicional_popover(self)
        self.popover_listbox.add(generate_title_row(_('Watermark'), True))

        self.zoom_entry, row = generate_spinbutton_row(_('Zoom'), None)
        self.zoom_entry.set_adjustment(Gtk.Adjustment(1, 100, 1000, 1, 100, 0))
        self.popover_listbox.add(row)
        self.file_entry, row = generate_button_row(
            _('Watermark'), self.on_button_watermark_clicked)
        self.file_entry.set_label(_('Select watermark file'))
        self.popover_listbox.add(row)


    def on_apply_clicked(self, widget, clear=False):
        if clear:
            self.reset()
        file_watermark = self.file_entry.get_label()
        if not os.path.exists(file_watermark):
            file_watermark = None
        zoom = float(self.zoom_entry.get_value() / 100.0)
        if self.check_this.get_active():
            to_update = [ self.no_page]
        elif self.check_all.get_active():
            to_update = range(0, self.document.get_n_pages())
        elif self.check_range.get_active():
            to_update = get_pages_from_ranges(
                get_ranges(self.range.get_text()))
        for i in to_update:
            if clear and str(i) in self.pages.keys():
                del self.pages[str(i)]
            else:
                self.pages[str(i)] = PageOptions(image_x=self.x,
                    image_y=self.y, image_zoom=zoom, image_file=file_watermark)
        if self.no_page in to_update:
            self.preview()

    def preview(self):
        file_watermark = self.file_entry.get_label()
        zoom = float(self.zoom_entry.get_value() / 100.0)
        if not os.path.exists(file_watermark):
            file_watermark = None
        self.viewport1.set_page_options(PageOptions(
            image_x=self.x+20, image_y=self.y+15, image_zoom=zoom,
            image_file=file_watermark))

    def on_button_watermark_clicked(self, button):
        dialog = Gtk.FileChooserDialog(_('Select one image'),
                                       self,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL,
                                        Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN,
                                        Gtk.ResponseType.OK))
        dialog.set_default_response(Gtk.ResponseType.OK)
        dialog.set_select_multiple(False)
        dialog.set_current_folder(os.getenv('HOME'))
        png_filtert = None
        for aMimetype in MIMETYPES_IMAGE.keys():
            filtert = Gtk.FileFilter()
            filtert.set_name(aMimetype)
            for mime_type in MIMETYPES_IMAGE[aMimetype]['mimetypes']:
                filtert.add_mime_type(mime_type)
            for pattern in MIMETYPES_IMAGE[aMimetype]['patterns']:
                filtert.add_pattern(pattern)
            dialog.add_filter(filtert)
            if aMimetype == 'PNG':
                png_filtert = filtert
        preview = Gtk.Image()
        dialog.set_preview_widget(preview)
        dialog.set_filter(png_filtert)
        dialog.connect('update-preview', update_preview_cb, preview)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.file_entry.set_label(dialog.get_filename())
        dialog.destroy()

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
    dialog = WatermarkDialog(filename=comun.SAMPLE)
    dialog.run()
