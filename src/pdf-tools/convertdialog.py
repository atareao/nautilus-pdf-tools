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
from comun import MIMETYPES_IMAGE
from comun import _


class ConvertDialog(Gtk.Dialog):
    def __init__(self):
        Gtk.Dialog.__init__(
            self, _('Convert to'), None,
            Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            (Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT,
             Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        self.set_size_request(300, 140)
        self.set_resizable(False)
        self.set_icon_from_file(comun.ICON)
        self.connect('destroy', self.close_application)
        vbox0 = Gtk.VBox(spacing=5)
        vbox0.set_border_width(5)
        self.get_content_area().add(vbox0)
        #
        notebook = Gtk.Notebook()
        vbox0.add(notebook)
        #
        frame1 = Gtk.Frame()
        notebook.append_page(frame1, tab_label=Gtk.Label(_('Convert to')))
        #
        table1 = Gtk.Table(rows=1, columns=2, homogeneous=False)
        table1.set_border_width(5)
        table1.set_col_spacings(5)
        table1.set_row_spacings(5)
        frame1.add(table1)
        #
        options = Gtk.ListStore(str)
        for extension in MIMETYPES_IMAGE.keys():
            if extension != _('ALL'):
                options.append([extension])
        label = Gtk.Label(_('Convert to') + ':')
        table1.attach(label, 0, 1, 0, 1,
                      xoptions=Gtk.AttachOptions.EXPAND,
                      yoptions=Gtk.AttachOptions.SHRINK)
        self.convert_to = Gtk.ComboBox.new_with_model_and_entry(options)
        self.convert_to.set_entry_text_column(0)
        self.convert_to.set_active(0)
        table1.attach(self.convert_to, 1, 2, 0, 1,
                      xoptions=Gtk.AttachOptions.EXPAND,
                      yoptions=Gtk.AttachOptions.SHRINK)
        self.show_all()

    def get_convert_to(self):
        tree_iter = self.convert_to.get_active_iter()
        if tree_iter is not None:
            model = self.convert_to.get_model()
            return model[tree_iter][0]
        return 'PNG'

    def close_application(self, widget):
        self.hide()


if __name__ == '__main__':
    dialog = ConvertDialog()
    dialog.run()
