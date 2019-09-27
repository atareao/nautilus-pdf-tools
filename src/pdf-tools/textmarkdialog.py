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
    gi.require_version('Poppler', '0.18')
except Exception as e:
    print(e)
    exit(1)
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Poppler
from miniview import MiniView
import comun
from comun import _
from comun import TOP, MIDLE, BOTTOM, LEFT, CENTER, RIGHT


class TextmarkDialog(Gtk.Dialog):
    def __init__(self, filename=None, window=None):
        Gtk.Dialog.__init__(
            self,
            _('Textmark'),
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
        notebook.append_page(frame, tab_label=Gtk.Label(_('Textmark')))

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
        frame1.add(self.scrolledwindow1)

        self.viewport1 = MiniView()
        self.scrolledwindow1.add(self.viewport1)

        frame2 = Gtk.Frame()
        grid.attach(frame2, 2, 0, 2, 1)
        scrolledwindow2 = Gtk.ScrolledWindow()
        scrolledwindow2.set_size_request(420, 420)
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
        self.extension.set_text(_('_textmarked'))
        grid.attach(self.extension, 1, 1, 1, 1)

        vbox1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        grid.attach(vbox1, 0, 2, 2, 1)

        button_font = Gtk.Button(_('Select font'))
        button_font.connect('clicked', self.on_button_font_activated, self)
        vbox1.pack_start(button_font, False, False, 0)

        button_color = Gtk.Button(_('Select color'))
        button_color.connect('clicked', self.on_button_color_activated, self)
        vbox1.pack_start(button_color, False, False, 0)

        vbox3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        grid.attach(vbox3, 2, 2, 2, 1)

        label = Gtk.Label(_('Text') + ':')
        vbox3.pack_start(label, False, False, 0)

        self.entry = Gtk.Entry()
        self.entry.set_width_chars(50)
        self.entry.connect('changed', self.on_entry_changed)
        vbox3.pack_start(self.entry, True, True, 0)

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

    def on_button_color_activated(self, widget, window):
        dialog = Gtk.ColorSelectionDialog(
            parent=window,
            title=_('Select color'),
            flags=Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT)
        dialog.get_color_selection().set_current_color(
            Gdk.Color(self.viewport2.color[0] * 65535,
                      self.viewport2.color[1] * 65535,
                      self.viewport2.color[2] * 65535))
        dialog.get_color_selection().set_current_alpha(
            self.viewport2.color[3] * 65535)
        response = dialog.run()
        print(response)
        if response == -5:
            color1 = dialog.get_color_selection().get_current_color()
            color2 = dialog.get_color_selection().get_current_alpha()
            self.viewport2.color = [color1.red / 65535.0,
                                    color1.green / 65535.0,
                                    color1.blue / 65535.0,
                                    color2 / 65535.0]
            print(self.viewport2.color)
            self.update_preview()
        dialog.destroy()

    def on_button_font_activated(self, widget, window):
        dialog = Gtk.FontSelectionDialog(
            parent=window,
            title=_('Select font'),
            flags=Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT)
        print(self.viewport2.font + ' ' + str(int(self.viewport2.size)))
        dialog.set_font_name(
            self.viewport2.font + ' ' + str(int(self.viewport2.size)))
        answer = dialog.run()
        if answer == -5:
            fs = dialog.get_font_selection()
            self.viewport2.font = ' '.join(fs.get_font_name().split()[:-1])
            self.viewport2.size = float(fs.get_font_name().split()[-1])
            self.update_preview()
        dialog.destroy()

    def get_horizontal_margin(self):
        return self.horizontal_margin.get_value()

    def get_vertical_margin(self):
        return self.vertical_margin.get_value()

    def get_color(self):
        return self.viewport2.color

    def get_font(self):
        return self.viewport2.font

    def get_size(self):
        return self.viewport2.size

    def get_text(self):
        return self.entry.get_text()

    def get_extension(self):
        return self.extension.get_text()

    def on_value_changed(self, widget):
        self.update_preview()

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

    def on_entry_changed(self, widget):
        self.update_preview()

    def update_preview(self):
        text = self.entry.get_text()
        if len(text) > 0:
            self.viewport2.set_text(self.entry.get_text())
            self.viewport2.set_image_position_vertical(
                self.get_vertical_option())
            self.viewport2.set_image_position_horizontal(
                self.get_horizontal_option())
            self.viewport2.refresh()

    def close_application(self, widget):
        self.hide()


if __name__ == '__main__':
    dialog = TextmarkDialog()
    dialog.run()
