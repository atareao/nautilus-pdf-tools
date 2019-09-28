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
import comun
from comun import _
from comun import ROTATE_000, ROTATE_090, ROTATE_180, ROTATE_270


class FlipDialog(Gtk.Dialog):
    def __init__(self, filename=None, window=None):
        Gtk.Dialog.__init__(
            self, _('Rotate and flid PDF'), window,
            Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            (Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT,
             Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        self.set_default_size(800, 400)
        self.set_resizable(True)
        self.set_icon_from_file(comun.ICON)
        self.connect('destroy', self.close)

        vbox = Gtk.VBox(spacing=5)
        vbox.set_border_width(5)
        self.get_content_area().add(vbox)

        frame = Gtk.Frame()
        vbox.pack_start(frame, True, True, 0)

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
        self.scrolledwindow1.set_size_request(420, 420)
        self.connect('key-release-event', self.on_key_release_event)
        frame1.add(self.scrolledwindow1)

        self.viewport1 = MiniView()
        self.scrolledwindow1.add(self.viewport1)

        frame2 = Gtk.Frame()
        grid.attach(frame2, 2, 0, 2, 1)
        scrolledwindow2 = Gtk.ScrolledWindow()
        scrolledwindow2.set_size_request(420, 420)
        self.connect('key-release-event', self.on_key_release_event)
        frame2.add(scrolledwindow2)

        self.viewport2 = MiniView()
        scrolledwindow2.add(self.viewport2)

        self.scale = 100

        label = Gtk.Label(_('Append to file') + ':')
        label.set_alignment(0, .5)
        grid.attach(label, 0, 1, 1, 1)

        self.extension = Gtk.Entry()
        self.extension.set_tooltip_text(_(
            'Append to file to create output filename'))
        self.extension.set_text(_('_flip_and_rotated'))
        grid.attach(self.extension, 1, 1, 1, 1)

        label = Gtk.Label(_('Flip vertical'))
        label.set_alignment(0, .5)
        grid.attach(label, 2, 1, 1, 1)

        self.switch1 = Gtk.Switch()
        self.switch1.connect("notify::active",
                             self.slider_on_value_changed)
        self.switch1.set_name('switch1')
        hbox1 = Gtk.HBox()
        hbox1.pack_start(self.switch1, 0, 0, 0)
        grid.attach(hbox1, 3, 1, 1, 1)

        label = Gtk.Label(_('Flip horizontal'))
        label.set_alignment(0, .5)
        grid.attach(label, 2, 2, 1, 1)

        self.switch2 = Gtk.Switch()
        self.switch2.connect("notify::active",
                             self.slider_on_value_changed)
        self.switch2.set_name('switch2')
        hbox2 = Gtk.HBox()
        hbox2.pack_start(self.switch2, 0, 0, 0)
        grid.attach(hbox2, 3, 2, 1, 1)

        label = Gtk.Label(_('Rotate'))
        label.set_alignment(0, .5)
        grid.attach(label, 0, 2, 1, 1)

        hbox3 = Gtk.HBox()
        grid.attach(hbox3, 1, 2, 1, 1)

        self.rbutton1 = Gtk.RadioButton.new_with_label_from_widget(None, '0')
        self.rbutton1.set_name('0')
        self.rbutton1.connect("notify::active", self.slider_on_value_changed)
        hbox3.pack_start(self.rbutton1, 0, 0, 0)

        self.rbutton2 = Gtk.RadioButton.new_with_label_from_widget(
            self.rbutton1, '90')
        self.rbutton2.set_name('90')
        self.rbutton2.connect("notify::active", self.slider_on_value_changed)
        hbox3.pack_start(self.rbutton2, 0, 0, 0)

        self.rbutton3 = Gtk.RadioButton.new_with_label_from_widget(
            self.rbutton1, '180')
        self.rbutton3.set_name('180')
        self.rbutton3.connect("notify::active", self.slider_on_value_changed)
        hbox3.pack_start(self.rbutton3, 0, 0, 0)

        self.rbutton4 = Gtk.RadioButton.new_with_label_from_widget(
            self.rbutton1, '270')
        self.rbutton4.set_name('270')
        self.rbutton4.connect("notify::active", self.slider_on_value_changed)
        hbox3.pack_start(self.rbutton4, 0, 0, 0)

        if filename is not None:
            uri = "file://" + filename
            document = Poppler.Document.new_from_file(uri, None)
            if document.get_n_pages() > 0:
                self.viewport1.set_page(document.get_page(0))
                self.viewport2.set_page(document.get_page(0))

        print(1)
        self.show_all()

    def slider_on_value_changed(self, widget, calue):
        print(widget.get_name())
        if widget.get_name() == 'switch1':
            self.viewport2.set_flip_vertical(self.switch1.get_active())
        elif widget.get_name() == 'switch2':
            self.viewport2.set_flip_horizontal(self.switch2.get_active())
        elif widget.get_name() == '0':
            self.viewport2.set_rotation_angle(0.0)
        elif widget.get_name() == '90':
            self.viewport2.set_rotation_angle(1.0)
        elif widget.get_name() == '180':
            self.viewport2.set_rotation_angle(2.0)
        elif widget.get_name() == '270':
            self.viewport2.set_rotation_angle(3.0)

    def on_key_release_event(self, widget, event):
        print((event.keyval))
        if event.keyval == 65451 or event.keyval == 43:
            self.scale = self.scale * 1.1
        elif event.keyval == 65453 or event.keyval == 45:
            self.scale = self.scale * .9
        elif event.keyval == 65456 or event.keyval == 48:
            factor_w = (float(self.scrolledwindow1.get_allocation().width) /
                        float(self.pixbuf1.get_width()))
            factor_h = (float(self.scrolledwindow1.get_allocation().height) /
                        float(self.pixbuf1.get_height()))
            if factor_w < factor_h:
                factor = factor_w
            else:
                factor = factor_h
            self.scale = int(factor * 100)
            w = int(self.pixbuf1.get_width() * factor)
            h = int(self.pixbuf1.get_height() * factor)
            self.image1.set_from_pixbuf(
                self.pixbuf1.scale_simple(w, h, GdkPixbuf.InterpType.BILINEAR))
            self.image2.set_from_pixbuf(
                self.pixbuf2.scale_simple(w, h, GdkPixbuf.InterpType.BILINEAR))
        elif event.keyval == 65457 or event.keyval == 49:
            self.scale = 100
        if self.image1:
            w = int(self.pixbuf1.get_width() * self.scale / 100)
            h = int(self.pixbuf1.get_height() * self.scale / 100)
            self.image1.set_from_pixbuf(
                self.pixbuf1.scale_simple(w, h, GdkPixbuf.InterpType.BILINEAR))
            self.image2.set_from_pixbuf(
                self.pixbuf2.scale_simple(w, h, GdkPixbuf.InterpType.BILINEAR))

    def close(self, widget):
        self.destroy()

    def get_extension(self):
        return self.extension.get_text()

    def get_rotate(self):
        if self.rbutton2.get_active():
            return ROTATE_090
        elif self.rbutton3.get_active():
            return ROTATE_180
        elif self.rbutton4.get_active():
            return ROTATE_270
        return ROTATE_000

    def get_flip_vertical(self):
        return self.switch1.get_active()

    def get_flip_horizontal(self):
        return self.switch2.get_active()


if __name__ == '__main__':
    dialog = FlipDialog()
    dialog.run()
