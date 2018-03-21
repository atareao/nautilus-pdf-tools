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
    def __init__(self, filename=None, window):
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
        #
        table = Gtk.Table(rows=4, columns=2, homogeneous=False)
        table.set_border_width(5)
        table.set_col_spacings(5)
        table.set_row_spacings(5)
        frame.add(table)
        #
        frame1 = Gtk.Frame()
        table.attach(frame1, 0, 1, 0, 1,
                     xoptions=Gtk.AttachOptions.EXPAND,
                     yoptions=Gtk.AttachOptions.SHRINK)
        self.scrolledwindow1 = Gtk.ScrolledWindow()
        self.scrolledwindow1.set_size_request(420, 420)
        frame1.add(self.scrolledwindow1)
        self.viewport1 = MiniView()
        self.scrolledwindow1.add(self.viewport1)
        frame2 = Gtk.Frame()
        table.attach(frame2, 1, 2, 0, 1,
                     xoptions=Gtk.AttachOptions.EXPAND,
                     yoptions=Gtk.AttachOptions.SHRINK)
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
        self.rbutton0 = Gtk.CheckButton(_('Overwrite original file?'))
        table.attach(self.rbutton0, 0, 2, 1, 2,
                     xoptions=Gtk.AttachOptions.FILL,
                     yoptions=Gtk.AttachOptions.SHRINK)
        vbox1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        table.attach(vbox1, 0, 2, 2, 3,
                     xoptions=Gtk.AttachOptions.FILL,
                     yoptions=Gtk.AttachOptions.SHRINK)
        button_font = Gtk.Button(_('Select Font'))
        button_font.connect('clicked', self.on_button_font_activated)
        vbox1.pack_start(button_font, False, False, 0)
        button_color = Gtk.Button(_('Select color'))
        button_color.connect('clicked', self.on_button_color_activated)
        vbox1.pack_start(button_color, False, False, 0)
        vbox3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        table.attach(vbox3, 0, 2, 4, 5,
                     xoptions=Gtk.AttachOptions.FILL,
                     yoptions=Gtk.AttachOptions.SHRINK)
        label = Gtk.Label(_('Text') + ':')
        vbox3.pack_start(label, False, False, 0)
        self.entry = Gtk.Entry()
        self.entry.set_width_chars(50)
        self.entry.connect('changed', self.on_entry_changed)
        vbox3.pack_start(self.entry, True, True, 0)
        label = Gtk.Label(_('Horizontal position') + ':')
        label.set_alignment(0, .5)
        table.attach(label, 0, 1, 5, 6,
                     xoptions=Gtk.AttachOptions.FILL,
                     yoptions=Gtk.AttachOptions.SHRINK)
        self.horizontal = Gtk.ComboBox.new_with_model_and_entry(
            horizontal_options)
        self.horizontal.set_entry_text_column(0)
        self.horizontal.set_active(0)
        self.horizontal.connect('changed', self.on_value_changed)
        table.attach(self.horizontal, 1, 2, 5, 6,
                     xoptions=Gtk.AttachOptions.FILL,
                     yoptions=Gtk.AttachOptions.SHRINK)
        label = Gtk.Label(_('Vertical position') + ':')
        label.set_alignment(0, .5)
        table.attach(label, 0, 1, 6, 7,
                     xoptions=Gtk.AttachOptions.FILL,
                     yoptions=Gtk.AttachOptions.SHRINK)
        #
        self.vertical = Gtk.ComboBox.new_with_model_and_entry(vertical_options)
        self.vertical.set_entry_text_column(0)
        self.vertical.set_active(0)
        self.vertical.connect('changed', self.on_value_changed)
        table.attach(self.vertical, 1, 2, 6, 7,
                     xoptions=Gtk.AttachOptions.FILL,
                     yoptions=Gtk.AttachOptions.SHRINK)
        label = Gtk.Label(_('Set horizontal margin') + ':')
        label.set_alignment(0, .5)
        table.attach(label, 0, 1, 7, 8,
                     xoptions=Gtk.AttachOptions.FILL,
                     yoptions=Gtk.AttachOptions.SHRINK)
        self.horizontal_margin = Gtk.SpinButton()
        self.horizontal_margin.set_adjustment(
            Gtk.Adjustment(5, 0, 100, 1, 10, 10))
        table.attach(self.horizontal_margin, 1, 2, 7, 8,
                     xoptions=Gtk.AttachOptions.FILL,
                     yoptions=Gtk.AttachOptions.SHRINK)
        self.horizontal_margin.connect('value-changed',
                                       self.on_margin_changed)
        label = Gtk.Label(_('Set vertical margin') + ':')
        label.set_alignment(0, .5)
        table.attach(label, 0, 1, 8, 9,
                     xoptions=Gtk.AttachOptions.FILL,
                     yoptions=Gtk.AttachOptions.SHRINK)
        self.vertical_margin = Gtk.SpinButton()
        self.vertical_margin.set_adjustment(
            Gtk.Adjustment(5, 0, 100, 1, 10, 10))
        table.attach(self.vertical_margin, 1, 2, 8, 9,
                     xoptions=Gtk.AttachOptions.FILL,
                     yoptions=Gtk.AttachOptions.SHRINK)
        self.vertical_margin.connect('value-changed',
                                     self.on_margin_changed)
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

    def on_button_color_activated(self, widget):
        dialog = Gtk.ColorSelectionDialog(
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

    def on_button_font_activated(self, widget):
        dialog = Gtk.FontSelectionDialog(
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

    def on_value_changed(self, widget):
        self.update_preview()

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
