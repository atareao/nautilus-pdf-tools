#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gi
try:
    gi.require_version('Gtk', '3.0')
except Exception as e:
    print(e)
    exit(1)
from gi.repository import Gtk
import comun
from comun import _

class ReduceDialog(Gtk.Dialog):
    def __init__(self, title, window):
        Gtk.Dialog.__init__(
            self,
            title,
            window,
            Gtk.DialogFlags.MODAL |
            Gtk.DialogFlags.DESTROY_WITH_PARENT,
            (Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT,
             Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        self.set_size_request(200, 150)
        self.set_resizable(False)
        self.set_icon_from_file(comun.ICON)
        self.set_default_response(Gtk.ResponseType.ACCEPT)
        self.connect('destroy', self.close_application)
        vbox0 = Gtk.VBox(spacing=5)
        vbox0.set_border_width(5)
        self.get_content_area().add(vbox0)

        frame1 = Gtk.Frame()
        vbox0.add(frame1)

        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        grid.set_margin_bottom(10)
        grid.set_margin_left(10)
        grid.set_margin_right(10)
        grid.set_margin_top(10)
        frame1.add(grid)

        label1 = Gtk.Label(_('Image resolution') + ':')
        label1.set_alignment(0, .5)
        grid.attach(label1, 0, 0, 1, 1)

        label2 = Gtk.Label(_('Append to file') + ':')
        label2.set_alignment(0, .5)
        grid.attach(label2, 0, 1, 1, 1)

        self.dpi_entry = Gtk.Entry()
        self.dpi_entry.set_tooltip_text(_('Set dpi to reduce file'))
        self.dpi_entry.set_text('100')
        grid.attach(self.dpi_entry, 1, 0, 1, 1)

        self.dpi_entry.set_activates_default(True)
        self.dpi_entry.grab_focus()

        self.append_entry = Gtk.Entry()
        self.append_entry.set_tooltip_text(_('Append to file to create output filename'))
        self.append_entry.set_text('_reduced')
        grid.attach(self.append_entry, 1, 1, 1, 1)

        self.show_all()

    def get_dpi(self):
        return self.dpi_entry.get_text()

    def get_append(self):
        return self.append_entry.get_text()

    def close_application(self, widget):
        self.hide()

if __name__ == '__main__':
    dialog = ReduceDialog('Test', None)
    dialog.run()