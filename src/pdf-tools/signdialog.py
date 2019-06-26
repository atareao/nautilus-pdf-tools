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
    gi.require_version('Gtk', '3.0')
    gi.require_version('Poppler', '0.18')
    gi.require_version('GdkPixbuf', '2.0')
except Exception as e:
    print(e)
    exit(1)
from gi.repository import Gtk
from gi.repository import Poppler
from gi.repository import GdkPixbuf
from miniview import MiniView
from PIL import Image
import os
import comun
from comun import _
from comun import MIMETYPES_IMAGE, MMTOPIXEL


class SignDialog(Gtk.Dialog):
    def __init__(self, filename=None, window=None):
        Gtk.Dialog.__init__(
            self,
            _('Sign'),
            window,
            Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            (Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT,
             Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        self.set_resizable(False)
        self.set_icon_from_file(comun.ICON)
        self.connect('destroy', self.close_application)
        vbox0 = Gtk.VBox(spacing=5)
        vbox0.set_border_width(5)
        self.get_content_area().add(vbox0)

        notebook = Gtk.Notebook()
        vbox0.add(notebook)

        frame = Gtk.Frame()
        notebook.append_page(frame, tab_label=Gtk.Label(_('Sign')))

        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        grid.set_margin_bottom(10)
        grid.set_margin_left(10)
        grid.set_margin_right(10)
        grid.set_margin_top(10)
        frame.add(grid)

        frame1 = Gtk.Frame()
        grid.attach(frame1, 0, 0, 4, 1)
        scrolledwindow1 = Gtk.ScrolledWindow()
        scrolledwindow1.set_size_request(300, 400)
        frame1.add(scrolledwindow1)

        self.viewport1 = MiniView(width=300, height=400,
                                  margin=0.0, border=0.0)
        self.viewport1.connect('button-release-event',
                               self.on_viewport1_clicked)
        scrolledwindow1.add(self.viewport1)

        self.scale = 100

        label = Gtk.Label(_('Append to file') + ':')
        label.set_alignment(0, .5)
        grid.attach(label, 0, 1, 1, 1)

        self.extension = Gtk.Entry()
        self.extension.set_tooltip_text(_(
            'Append to file to create output filename'))
        self.extension.set_text(_('_signed'))
        grid.attach(self.extension, 1, 1, 1, 1)

        vbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        grid.attach(vbox, 0, 2, 2, 1)

        label = Gtk.Label(_('Sign') + ':')
        label.set_alignment(0, 0.5)
        vbox.pack_start(label, False, False, 0)

        self.entry = Gtk.Entry()
        self.entry.set_width_chars(10)
        self.entry.set_sensitive(False)
        vbox.pack_start(self.entry, True, True, 0)

        button = Gtk.Button(_('Choose File'))
        button.connect('clicked', self.on_button_clicked)
        vbox.pack_start(button, False, False, 0)

        label = Gtk.Label(_('sign zoom') + ':')
        label.set_alignment(0, 0.5)
        grid.attach(label, 0, 6, 1, 1)

        self.watermark_zoom = Gtk.SpinButton()
        self.watermark_zoom.connect('value-changed',
                                    self.update_preview)
        self.watermark_zoom.set_adjustment(
            Gtk.Adjustment(100, 0, 1010, 1, 10, 10))
        grid.attach(self.watermark_zoom, 1, 6, 1, 1)

        self.position_x = 0
        self.position_y = 0
        self.original_position_x = 0
        self.original_position_y = 0

        self.show_all()
        if filename is not None:
            uri = "file://" + filename
            document = Poppler.Document.new_from_file(uri, None)
            if document.get_n_pages() > 0:
                self.viewport1.set_page(document.get_page(0))

    def on_viewport1_clicked(self, widget, event):
        if self.viewport1.image_width > 0 and self.viewport1.image_height > 0:
            deltay = abs(self.viewport1.get_allocation().height -
                         self.viewport1.page_height) / 2.0
            deltax = abs(self.viewport1.get_allocation().width -
                         self.viewport1.page_width) / 2.0
            self.position_x = (event.x - deltax)
            self.position_y = (event.y - deltay)
            self.original_position_x = (event.x - deltax) / self.viewport1.zoom
            self.original_position_y = (event.y - deltay) / self.viewport1.zoom
            iw = self.viewport1.image_width * self.viewport1.zoom / MMTOPIXEL
            ih = self.viewport1.image_height * self.viewport1.zoom / MMTOPIXEL
            self.position_x -= iw / 2.0
            self.position_y -= ih / 2.0
            self.position_x = self.position_x / self.viewport1.zoom
            self.position_y = self.position_y / self.viewport1.zoom
            print(self.original_position_x, self.original_position_y)
            self.update_preview()

    def on_value_changed(self, widget):
        self.update_preview()

    def get_watermark_zoom(self):
        return self.watermark_zoom.get_value()

    def get_extension(self):
        return self.extension.get_text()

    def get_image_filename(self):
        return self.entry.get_text()

    def on_button_clicked(self, button):
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
            filter = Gtk.FileFilter()
            filter.set_name(aMimetype)
            for mime_type in MIMETYPES_IMAGE[aMimetype]['mimetypes']:
                filter.add_mime_type(mime_type)
            for pattern in MIMETYPES_IMAGE[aMimetype]['patterns']:
                filter.add_pattern(pattern)
            dialog.add_filter(filter)
        preview = Gtk.Image()
        dialog.set_preview_widget(preview)
        dialog.connect('update-preview', self.update_preview_cb, preview)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.entry.set_text(dialog.get_filename())
        dialog.destroy()

        file_watermark = self.entry.get_text()
        im = Image.open(file_watermark)
        width, height = im.size
        self.update_preview()

    def update_preview_cb(self, file_chooser, preview):
        filename = file_chooser.get_preview_filename()
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(filename, 128, 128)
            preview.set_from_pixbuf(pixbuf)
            has_preview = True
        except Exception as e:
            print(e)
            has_preview = False
        file_chooser.set_preview_widget_active(has_preview)
        return

    def update_preview(self, widget=None):
        file_watermark = self.entry.get_text()
        if file_watermark and os.path.exists(file_watermark):
            self.viewport1.set_image(file_watermark)
            self.viewport1.image_zoom = float(
                self.watermark_zoom.get_value() / 100.0)
            self.viewport1.image_margin_width = self.position_x
            self.viewport1.image_margin_height = self.position_y
            self.viewport1.refresh()

    def close_application(self, widget):
        self.hide()


if __name__ == '__main__':
    dialog = SignDialog('/home/lorenzo/Escritorio/pdfs/ejemplo_pdf_01.pdf')
    dialog.run()