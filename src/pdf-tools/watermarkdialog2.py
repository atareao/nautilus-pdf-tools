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
from comun import MMTOPIXEL
from comun import _
from comun import MIMETYPES_IMAGE
from tools import get_ranges
from tools import get_pages_from_ranges
from tools import update_image_preview_cb
from basedialog import BaseDialog, generate_separator_row, generate_title_row
from basedialog import generate_swith_row, generate_check_entry_row
from basedialog import generate_check_row, generate_entry_row
from basedialog import generate_button_row, generate_spinbutton_row, generate_simple_button_row


class PageOptions():
    def __init__(self, x, y, zoom, afile):
        self.x = x
        self.y = y
        self.zoom = zoom
        self.file = afile

class WatermarkDialog(BaseDialog):
    def __init__(self, filename=None, window=None):
        BaseDialog.__init__(self, _('Watermark'), filename, window)
        self.viewport1.connect('button-release-event',
                               self.on_viewport1_clicked)

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
                                                  self.on_values_changed)
        self.popover_listbox.add(row)
        self.check_all, row = generate_check_row(_('All'), self.check_this,
                                                  self.on_values_changed)
        self.popover_listbox.add(row)
        self.check_range, self.range, row = generate_check_entry_row(
            _('Range'), self.check_this, self.on_values_changed)
        self.popover_listbox.add(row)

        self.popover_listbox.add(generate_separator_row())

        self.popover_listbox.add(generate_title_row(_('Watermark'), True))

        self.zoom_entry, row = generate_spinbutton_row(_('Zoom'),
                                                       self.on_values_changed)
        self.zoom_entry.set_adjustment(Gtk.Adjustment(1, 100, 1000, 1, 100, 0))
        self.popover_listbox.add(row)
        self.file_entry, row = generate_button_row(
            _('Watermark'), self.on_button_watermark_clicked)
        self.file_entry.set_label(_('Select watermark file'))
        self.popover_listbox.add(row)
        self.clear, row = generate_simple_button_row(_('Clear watermark'),
                                              self.on_clear_watermark)
        self.popover_listbox.add(row)


    def on_clear_watermark(self, button):
        self.zoom_entry.set_value(1)
        self.file_entry.set_label(_('Select watermark file'))
        del self.pages[str(self.no_page)]
        self.on_values_changed(None, None, None)

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
        for aMimetype in MIMETYPES_IMAGE.keys():
            filtert = Gtk.FileFilter()
            filtert.set_name(aMimetype)
            for mime_type in MIMETYPES_IMAGE[aMimetype]['mimetypes']:
                filtert.add_mime_type(mime_type)
            for pattern in MIMETYPES_IMAGE[aMimetype]['patterns']:
                filtert.add_pattern(pattern)
            dialog.add_filter(filtert)
        preview = Gtk.Image()
        dialog.set_preview_widget(preview)
        dialog.connect('update-preview', update_image_preview_cb, preview)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.file_entry.set_label(dialog.get_filename())
            self.on_values_changed(None, None, None)
        dialog.destroy()

    def on_values_changed(self, widget, value, name):
        zoom = self.zoom_entry.get_value()
        file_watermark = self.file_entry.get_label()
        if file_watermark and os.path.exists(file_watermark):
            if str(self.no_page) in self.pages.keys():
                x = self.pages[str(self.no_page)].x
                y = self.pages[str(self.no_page)].y
            else:
                x = 0
                y = 0
            self.pages[str(self.no_page)] = PageOptions(x, y, zoom,
                                                        file_watermark)
        else:
            x = 0
            y = 0
            zoom = 1
            file_watermark = None
            del self.pages[str(self.no_page)]
        self.update_preview(x, y, zoom, file_watermark)

    def update_preview(self, x, y, zoom, file_watermark):
        if file_watermark and os.path.exists(file_watermark):
            self.viewport1.set_image(file_watermark)
            self.viewport1.image_zoom = float(zoom / 100.0)
            self.viewport1.image_margin_width = x
            self.viewport1.image_margin_height = y
        else:
            self.viewport1.set_image(None)
        self.viewport1.refresh()

    def on_viewport1_clicked(self, widget, event):
        if self.viewport1.image_width > 0 and self.viewport1.image_height > 0:
            deltay = abs(self.viewport1.get_allocation().height -
                         self.viewport1.page_height) / 2.0
            deltax = abs(self.viewport1.get_allocation().width -
                         self.viewport1.page_width) / 2.0
            position_x = (event.x - deltax)
            position_y = (event.y - deltay)
            original_position_x = (event.x - deltax) / self.viewport1.zoom
            original_position_y = (event.y - deltay) / self.viewport1.zoom
            iw = self.viewport1.image_width * self.viewport1.zoom / MMTOPIXEL
            ih = self.viewport1.image_height * self.viewport1.zoom / MMTOPIXEL
            position_x -= iw / 2.0
            position_y -= ih / 2.0
            position_x = position_x / self.viewport1.zoom
            position_y = position_y / self.viewport1.zoom
            print(original_position_x, original_position_y)
            zoom = self.zoom_entry.get_value()
            file_watermark = self.file_entry.get_label()
            if file_watermark and os.path.exists(file_watermark):
                if str(self.no_page) in self.pages.keys():
                    x = self.pages[str(self.no_page)].x
                    y = self.pages[str(self.no_page)].y
                else:
                    x = 0
                    y = 0
                self.pages[str(self.no_page)] = PageOptions(position_x,
                                                            position_y, zoom,
                                                            file_watermark)
            else:
                x = 0
                y = 0
                zoom = 1
                file_watermark = None
                del self.pages[str(self.no_page)]
            self.update_preview(position_x, position_y, zoom, file_watermark)


if __name__ == '__main__':
    dialog = WatermarkDialog(comun.SAMPLE)
    dialog.run()
