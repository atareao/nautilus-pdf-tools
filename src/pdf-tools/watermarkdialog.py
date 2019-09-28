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
from comun import TOP, MIDLE, BOTTOM, LEFT, CENTER, RIGHT, MIMETYPES_IMAGE
from tools import update_preview_cb

class WatermarkDialog(Gtk.Dialog):
    def __init__(self, filename=None, window=None):
        Gtk.Dialog.__init__(
            self,
            _('Watermark'),
            window,
            Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            (Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT,
             Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        self.set_size_request(500, 140)
        self.set_resizable(False)
        self.set_icon_from_file(comun.ICON)
        self.connect('destroy', self.close_application)
        vbox0 = Gtk.VBox(spacing=5)
        vbox0.set_border_width(5)
        self.get_content_area().add(vbox0)

        notebook = Gtk.Notebook()
        vbox0.add(notebook)

        frame = Gtk.Frame()
        notebook.append_page(frame, tab_label=Gtk.Label(_('Watermark')))

        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        grid.set_margin_bottom(10)
        grid.set_margin_left(10)
        grid.set_margin_right(10)
        grid.set_margin_top(10)
        frame.add(grid)

        frame1 = Gtk.Frame()
        grid.attach(frame1, 0, 0, 2, 1)
        self.scrolledwindow1 = Gtk.ScrolledWindow()
        self.scrolledwindow1.set_size_request(320, 320)
        frame1.add(self.scrolledwindow1)

        self.viewport1 = MiniView()
        self.scrolledwindow1.add(self.viewport1)

        frame2 = Gtk.Frame()
        grid.attach(frame2, 2, 0, 2, 1)
        scrolledwindow2 = Gtk.ScrolledWindow()
        scrolledwindow2.set_size_request(320, 320)
        frame2.add(scrolledwindow2)

        self.viewport2 = MiniView()
        scrolledwindow2.add(self.viewport2)

        self.scale = 100

        vertical_options = Gtk.ListStore(str, int)
        vertical_options.append([_('Top'), TOP])
        vertical_options.append([_('Middle'), MIDLE])
        vertical_options.append([_('Bottom'), BOTTOM])

        horizontal_options = Gtk.ListStore(str, int)
        horizontal_options.append([_('Left'), LEFT])
        horizontal_options.append([_('Center'), CENTER])
        horizontal_options.append([_('Right'), RIGHT])

        label = Gtk.Label(_('Append to file') + ':')
        label.set_alignment(0, .5)
        grid.attach(label, 0, 1, 1, 1)

        self.extension = Gtk.Entry()
        self.extension.set_tooltip_text(_(
            'Append to file to create output filename'))
        self.extension.set_text(_('_watermarked'))
        grid.attach(self.extension, 1, 1, 1, 1)

        vbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        grid.attach(vbox, 0, 2, 2, 1)

        label = Gtk.Label(_('Watermark') + ':')
        label.set_alignment(0, 0.5)
        vbox.pack_start(label, False, False, 0)

        self.entry = Gtk.Entry()
        self.entry.set_width_chars(10)
        self.entry.set_sensitive(False)
        vbox.pack_start(self.entry, True, True, 0)

        button = Gtk.Button(_('Choose File'))
        button.connect('clicked', self.on_button_clicked)
        vbox.pack_start(button, False, False, 0)

        label = Gtk.Label(_('Horizontal position') + ':')
        label.set_alignment(0, .5)
        grid.attach(label, 0, 4, 1, 1)

        self.horizontal = Gtk.ComboBox.new_with_model_and_entry(
            horizontal_options)
        self.horizontal.set_entry_text_column(0)
        self.horizontal.set_active(0)
        self.horizontal.connect('changed', self.on_value_changed)
        grid.attach(self.horizontal, 1, 4, 1, 1)

        label = Gtk.Label(_('Vertical position') + ':')
        label.set_alignment(0, .5)
        grid.attach(label, 2, 4, 1, 1)

        self.vertical = Gtk.ComboBox.new_with_model_and_entry(vertical_options)
        self.vertical.set_entry_text_column(0)
        self.vertical.set_active(0)
        self.vertical.connect('changed', self.on_value_changed)
        grid.attach(self.vertical, 3, 4, 1, 1)

        label = Gtk.Label(_('Set horizontal margin') + ':')
        label.set_alignment(0, .5)
        grid.attach(label, 0, 5, 1, 1)

        self.horizontal_margin = Gtk.SpinButton()
        self.horizontal_margin.set_adjustment(
            Gtk.Adjustment(5, 0, 100, 1, 10, 10))
        self.horizontal_margin.connect('value-changed',
                                       self.on_margin_changed)
        grid.attach(self.horizontal_margin, 1, 5, 1, 1)

        label = Gtk.Label(_('Set vertical margin') + ':')
        label.set_alignment(0, .5)
        grid.attach(label, 2, 5, 1, 1)

        self.vertical_margin = Gtk.SpinButton()
        self.vertical_margin.set_adjustment(
            Gtk.Adjustment(5, 0, 100, 1, 10, 10))
        self.vertical_margin.connect('value-changed',
                                     self.on_margin_changed)
        grid.attach(self.vertical_margin, 3, 5, 1, 1)

        label = Gtk.Label(_('Watermark zoom') + ':')
        label.set_alignment(0, 0.5)
        grid.attach(label, 0, 6, 1, 1)

        self.watermark_zoom = Gtk.SpinButton()
        self.watermark_zoom.connect('value-changed',
                                    self.update_preview)
        self.watermark_zoom.set_adjustment(
            Gtk.Adjustment(100, 0, 1010, 1, 10, 10))
        grid.attach(self.watermark_zoom, 1, 6, 1, 1)

        self.show_all()
        if filename is not None:
            uri = "file://" + filename
            document = Poppler.Document.new_from_file(uri, None)
            if document.get_n_pages() > 0:
                self.viewport1.set_page(document.get_page(0))
                self.viewport2.set_page(document.get_page(0))

    def on_margin_changed(self, widget):
        self.viewport2.text_margin_width = self.horizontal_margin.get_value()
        self.viewport2.text_margin_height = self.vertical_margin.get_value()
        self.update_preview()

    def on_value_changed(self, widget):
        self.update_preview()

    def get_watermark_zoom(self):
        return self.watermark_zoom.get_value()

    def get_horizontal_margin(self):
        return self.horizontal_margin.get_value()

    def get_vertical_margin(self):
        return self.vertical_margin.get_value()

    def get_extension(self):
        return self.extension.get_text()

    def get_image_filename(self):
        return self.entry.get_text()

    def get_horizontal_option(self):
        tree_iter = self.horizontal.get_active_iter()
        if tree_iter is not None:
            model = self.horizontal.get_model()
            return model[tree_iter][1]
        return 0

    def get_vertical_option(self):
        tree_iter = self.vertical.get_active_iter()
        if tree_iter is not None:
            model = self.vertical.get_model()
            return model[tree_iter][1]
        return 0

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
            filtert = Gtk.FileFilter()
            filtert.set_name(aMimetype)
            for mime_type in MIMETYPES_IMAGE[aMimetype]['mimetypes']:
                filtert.add_mime_type(mime_type)
            for pattern in MIMETYPES_IMAGE[aMimetype]['patterns']:
                filtert.add_pattern(pattern)
            dialog.add_filter(filtert)
        preview = Gtk.Image()
        dialog.set_preview_widget(preview)
        dialog.connect('update-preview', update_preview_cb, preview)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.entry.set_text(dialog.get_filename())
        dialog.destroy()

        file_watermark = self.entry.get_text()
        im = Image.open(file_watermark)
        width, height = im.size
        self.update_preview()

    def update_preview(self, widget=None):
        file_watermark = self.entry.get_text()
        if file_watermark and os.path.exists(file_watermark):
            self.viewport2.set_image(file_watermark)
            self.viewport2.image_zoom = float(
                self.watermark_zoom.get_value() / 100.0)
            self.viewport2.set_image_position_vertical(
                self.get_vertical_option())
            self.viewport2.set_image_position_horizontal(
                self.get_horizontal_option())
            self.viewport2.image_margin_width =\
                self.horizontal_margin.get_value()
            self.viewport2.image_margin_height =\
                self.vertical_margin.get_value()
            self.viewport2.refresh()

    def close_application(self, widget):
        self.hide()


if __name__ == '__main__':
    dialog = WatermarkDialog(
        '/home/lorenzo/Escritorio/pdfs/ejemplo_pdf_01.pdf')
    dialog.run()
