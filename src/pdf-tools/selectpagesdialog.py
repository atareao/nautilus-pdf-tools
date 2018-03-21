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
import comun
import tools
from comun import _


class SelectPagesDialog(Gtk.Dialog):
    def __init__(self, title, afile, window):
        Gtk.Dialog.__init__(
            self,
            title,
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
        frame1 = Gtk.Frame()
        notebook.append_page(frame1, tab_label=Gtk.Label(_('Select Pages')))

        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        grid.set_margin_bottom(10)
        grid.set_margin_left(10)
        grid.set_margin_right(10)
        grid.set_margin_top(10)
        frame1.add(grid)

        label = Gtk.Label(_('Pages') + ':')
        label.set_tooltip_text(_('Type page number and/or page\nranges\
 separated by commas\ncounting from start of the\ndocument ej. 1,4,6-9'))
        label.set_alignment(0, .5)
        grid.attach(label, 0, 0, 1, 1)

        self.entry1 = Gtk.Entry()
        self.entry1.set_tooltip_text(_('Type page number and/or page\nranges\
 separated by commas\ncounting from start of the\ndocument ej. 1,4,6-9'))
        grid.attach(self.entry1, 1, 0, 1, 1)

        if afile is not None:
            label = Gtk.Label(_('Output file') + ':')
            label.set_tooltip_text(_('Select the output file'))
            label.set_alignment(0, .5)
            grid.attach(label, 0, 1, 1, 1)

            self.output_file = Gtk.Button.new_with_label(afile)
            self.output_file.connect('clicked',
                                     self.on_button_output_file_clicked,
                                     window)
            grid.attach(self.output_file, 1, 1, 1, 1)
        self.show_all()

    def on_button_output_file_clicked(self, widget, window):
        file_out = tools.dialog_save_as(
            _('Select file to save new file'),
            self.output_file.get_label(),
            window)
        if file_out:
            self.output_file.set_label(file_out)

    def get_file_out(self):
        return self.output_file.get_label()

    def close_application(self, widget):
        self.hide()


if __name__ == '__main__':
    dialog = SelectPagesDialog('Test', None, None)
    dialog.run()
