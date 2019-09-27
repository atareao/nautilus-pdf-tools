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
import comun
import tools
from comun import _


class SelectPagesRotateDialog(Gtk.Dialog):
    def __init__(self, title, last_page, afile, window):
        Gtk.Dialog.__init__(
            self,
            title,
            window,
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
        notebook = Gtk.Notebook()
        vbox0.add(notebook)
        frame1 = Gtk.Frame()
        notebook.append_page(frame1, tab_label=Gtk.Label(_('Select Pages')))
        table1 = Gtk.Table(rows=3, columns=3, homogeneous=False)
        table1.set_border_width(5)
        table1.set_col_spacings(5)
        table1.set_row_spacings(5)
        frame1.add(table1)
        label1 = Gtk.Label(_('Pages') + ':')
        label1.set_tooltip_text(_('Type page number and/or page\nranges\
 separated by commas\ncounting from start of the\ndocument ej. 1,4,6-9'))
        label1.set_alignment(0, .5)
        table1.attach(label1, 0, 1, 0, 1,
                      xoptions=Gtk.AttachOptions.FILL,
                      yoptions=Gtk.AttachOptions.SHRINK)
        self.entry1 = Gtk.Entry()
        self.entry1.set_tooltip_text(_('Type page number and/or page\nranges\
 separated by commas\ncounting from start of the\ndocument ej. 1,4,6-9'))
        table1.attach(self.entry1, 1, 3, 0, 1,
                      xoptions=Gtk.AttachOptions.EXPAND,
                      yoptions=Gtk.AttachOptions.SHRINK)
        self.rbutton1 = Gtk.RadioButton.new_from_widget(None)
        self.rbutton1.add(Gtk.Image.new_from_icon_name(
            'object-rotate-left', Gtk.IconSize.BUTTON))
        table1.attach(self.rbutton1, 0, 1, 2, 3,
                      xoptions=Gtk.AttachOptions.EXPAND,
                      yoptions=Gtk.AttachOptions.SHRINK)
        self.rbutton2 = Gtk.RadioButton.new_from_widget(self.rbutton1)
        self.rbutton2.add(Gtk.Image.new_from_icon_name(
            'object-rotate-right', Gtk.IconSize.BUTTON))
        table1.attach(self.rbutton2, 1, 2, 2, 3,
                      xoptions=Gtk.AttachOptions.EXPAND,
                      yoptions=Gtk.AttachOptions.SHRINK)
        self.rbutton3 = Gtk.RadioButton.new_from_widget(self.rbutton1)
        self.rbutton3.add(Gtk.Image.new_from_icon_name(
            'object-flip-vertical', Gtk.IconSize.BUTTON))
        table1.attach(self.rbutton3, 2, 3, 2, 3,
                      xoptions=Gtk.AttachOptions.EXPAND,
                      yoptions=Gtk.AttachOptions.SHRINK)
        label = Gtk.Label(_('Output file') + ':')
        label.set_tooltip_text(_('Select the output file'))
        label.set_alignment(0, .5)
        table1.attach(label, 0, 1, 3, 4,
                      xoptions=Gtk.AttachOptions.FILL,
                      yoptions=Gtk.AttachOptions.SHRINK)
        self.output_file = Gtk.Button.new_with_label(afile)
        self.output_file.connect('clicked',
                                 self.on_button_output_file_clicked,
                                 window)
        table1.attach(self.output_file, 1, 3, 3, 4,
                      xoptions=Gtk.AttachOptions.FILL,
                      yoptions=Gtk.AttachOptions.SHRINK)
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
    dialog = SelectPagesRotateDialog('Test', 10, 'file')
    dialog.run()
