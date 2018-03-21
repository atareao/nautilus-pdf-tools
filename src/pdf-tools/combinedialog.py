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
except Exception as e:
    print(e)
    exit(1)
from gi.repository import Gtk
import tools
import comun
from comun import _


class CombineDialog(Gtk.Dialog):
    def __init__(self, title, window):
        Gtk.Dialog.__init__(
            self, title, window,
            Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            (Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT,
             Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        self.set_size_request(350, 150)
        self.set_resizable(False)
        self.set_icon_from_file(comun.ICON)
        self.connect('destroy', self.close_application)
        vbox0 = Gtk.VBox(spacing=5)
        vbox0.set_border_width(5)
        self.get_content_area().add(vbox0)
        notebook = Gtk.Notebook()
        vbox0.add(notebook)
        frame1 = Gtk.Frame()
        notebook.append_page(frame1, tab_label=Gtk.Label(_('Pages')))

        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        grid.set_margin_bottom(10)
        grid.set_margin_left(10)
        grid.set_margin_right(10)
        grid.set_margin_top(10)
        frame1.add(grid)

        label1 = Gtk.Label(_('Paper size') + ':')
        label1.set_alignment(0, .5)
        grid.attach(label1, 0, 0, 1, 1)

        label2 = Gtk.Label(_('Orientation') + ':')
        label2.set_alignment(0, .5)
        grid.attach(label2, 0, 1, 1, 1)

        label3 = Gtk.Label(_('Pages in Page') + ':')
        label3.set_alignment(0, .5)
        grid.attach(label3, 0, 2, 1, 1)

        label4 = Gtk.Label(_('by'))
        label4.set_alignment(.5, .5)
        grid.attach(label4, 2, 2, 1, 1)

        label5 = Gtk.Label(_('Sort') + ':')
        label5.set_alignment(0, .5)
        grid.attach(label5, 0, 4, 1, 1)

        label6 = Gtk.Label(_('Set the margin') + ':')
        label6.set_alignment(0, .5)
        grid.attach(label6, 0, 5, 1, 1)

        label7 = Gtk.Label(_('Append to file') + ':')
        label7.set_alignment(0, .5)
        grid.attach(label7, 0, 6, 1, 1)

        liststore = Gtk.ListStore(str, float, float)
        liststore.append([_('A0'), 2383.9, 3370.4])
        liststore.append([_('A1'), 1683.8, 2383.9])
        liststore.append([_('A2'), 1190.6, 1683.8])
        liststore.append([_('A3'), 841.9, 1190.6])
        liststore.append([_('A4'), 595.3, 841.9])
        liststore.append([_('A5'), 419.5, 595.3])
        liststore.append([_('A6'), 297.6, 419.5])
        liststore.append([_('A7'), 209.8, 297.6])
        liststore.append([_('A8'), 147.4, 209.8])
        liststore.append([_('A9'), 104.9, 147.4])
        liststore.append([_('A10'), 73.7, 104.9])
        liststore.append([_('B0'), 2834.6, 73.7])
        liststore.append([_('B1'), 2004.1, 2834.6])
        liststore.append([_('B2'), 1417.3, 2004.1])
        liststore.append([_('B3'), 1000.6, 1417.3])
        liststore.append([_('B4'), 708.7, 1000.6])
        liststore.append([_('B5'), 498.9, 708.7])
        liststore.append([_('B6'), 354.3, 498.9])
        liststore.append([_('B7'), 249.4, 354.3])
        liststore.append([_('B8'), 175.7, 249.4])
        liststore.append([_('B9'), 124.7, 175.7])
        liststore.append([_('B10'), 87.9, 124.7])
        liststore.append([_('Letter (8 1/2x11)'), 612.0, 792.0])
        liststore.append([_('Note (8 1/2x11)'), 612.0, 792.0])
        liststore.append([_('Legal (8 1/2x14)'), 612.0, 1008.0])
        liststore.append([_('Executive (8 1/4x10 1/2)'), 522.0, 756.0])
        liststore.append([_('Halfetter (5 1/2x8 1/2)'), 396.0, 612.0])
        liststore.append([_('Halfexecutive (5 1/4x7 1/4)'), 378.0, 522.0])
        liststore.append([_('11x17 (11x17)'), 792.0, 1224.0])
        liststore.append([_('Statement (5 1/2x8 1/2)'), 396.0, 612.0])
        liststore.append([_('Folio (8 1/2x13)'), 612.0, 936.0])
        liststore.append([_('10x14 (10x14)'), 720.0, 1008.0])
        liststore.append([_('Ledger (17x11)'), 1224.0, 792.0])
        liststore.append([_('Tabloid (11x17)'), 792.0, 1224.0])
        self.entry1 = Gtk.ComboBox.new_with_model(model=liststore)
        self.entry1.set_tooltip_text(_('Select the size of the output file'))
        renderer_text = Gtk.CellRendererText()
        self.entry1.pack_start(renderer_text, True)
        self.entry1.add_attribute(renderer_text, "text", 0)
        self.entry1.set_active(0)
        grid.attach(self.entry1, 1, 0, 4, 1)

        liststore = Gtk.ListStore(str)
        liststore.append([_('Vertical')])
        liststore.append([_('Horizontal')])
        self.entry2 = Gtk.ComboBox.new_with_model(model=liststore)
        self.entry2.set_tooltip_text(_('Select the orientation of the page'))
        renderer_text = Gtk.CellRendererText()
        self.entry2.pack_start(renderer_text, True)
        self.entry2.add_attribute(renderer_text, "text", 0)
        self.entry2.set_active(0)
        grid.attach(self.entry2, 1, 1, 4, 1)

        self.entry3 = Gtk.SpinButton()
        self.entry3.set_tooltip_text(_('Select how many pages in a page'))
        self.entry3.set_adjustment(Gtk.Adjustment(1, 1, 100, 1, 10, 10))
        self.entry3.set_value(1)
        grid.attach(self.entry3, 1, 2, 1, 1)

        self.entry4 = Gtk.SpinButton()
        self.entry4.set_tooltip_text(_('rows by columns'))
        self.entry4.set_adjustment(Gtk.Adjustment(1, 1, 100, 1, 10, 10))
        self.entry4.set_value(2)
        grid.attach(self.entry4, 3, 2, 1, 1)

        liststore = Gtk.ListStore(str)
        liststore.append([_('By rows')])
        liststore.append([_('By columns')])
        self.entry5 = Gtk.ComboBox.new_with_model(model=liststore)
        self.entry5.set_tooltip_text(_('Select the combination sort'))
        renderer_text = Gtk.CellRendererText()
        self.entry5.pack_start(renderer_text, True)
        self.entry5.add_attribute(renderer_text, "text", 0)
        self.entry5.set_active(0)
        grid.attach(self.entry5, 1, 4, 4, 1)

        self.entry6 = Gtk.SpinButton()
        self.entry6.set_tooltip_text(_('The margin to the page in mm'))
        self.entry6.set_adjustment(Gtk.Adjustment(0, 0, 100, 1, 10, 10))
        self.entry6.set_value(0)
        grid.attach(self.entry6, 1, 5, 1, 1)

        self.extension = Gtk.Entry()
        self.extension.set_tooltip_text(_(
            'Append to file to create output filename'))
        self.extension.set_text(_('_combined'))
        grid.attach(self.extension, 1, 6, 4, 1)
        self.show_all()

    def on_button_output_file_clicked(self, widget, window):
        file_out = tools.dialog_save_as(
            _('Select file to save new file'),
            self.output_file.get_label(), window)
        if file_out:
            self.output_file.set_label(file_out)

    def get_extension(self):
        return self.extension.get_text()

    def get_size(self):
        tree_iter = self.entry1.get_active_iter()
        if tree_iter is not None:
            model = self.entry1.get_model()
            w = model[tree_iter][1]
            h = model[tree_iter][2]
            return w, h
        return None

    def is_vertical(self):
        tree_iter = self.entry2.get_active_iter()
        if tree_iter is not None:
            model = self.entry2.get_model()
            vertical = model[tree_iter][0]
            if vertical == _('Vertical'):
                return True
        return False

    def get_rows(self):
        return self.entry3.get_value()

    def get_columns(self):
        return self.entry4.get_value()

    def is_sort_by_rows(self):
        tree_iter = self.entry5.get_active_iter()
        if tree_iter is not None:
            model = self.entry5.get_model()
            vertical = model[tree_iter][0]
            if vertical == _('By rows'):
                return True
        return False

    def get_margin(self):
        return self.entry6.get_value()

    def close_application(self, widget):
        self.hide()


if __name__ == '__main__':
    dialog = CombineDialog('Combine', None)
    dialog.run()
