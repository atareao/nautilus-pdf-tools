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
    gi.require_version('GdkPixbuf', '2.0')
except ValueError as e:
    print(e)
    exit(1)
from gi.repository import GdkPixbuf, Gtk
import os
import tools
from basicdialog import BasicDialog
from comun import _
from tools import update_preview_cb


class JoinPdfsDialog(BasicDialog):
    def __init__(self, title, files, afile, window):
        self.files = files
        self.afile = afile
        self.main_window = window
        BasicDialog.__init__(self, title, window)

    def init_ui(self):
        BasicDialog.init_ui(self)

        label1 = Gtk.Label(_('Output file') + ':')
        label1.set_tooltip_text(_('Select the output file'))
        label1.set_alignment(0, .5)
        self.grid.attach(label1, 0, 0, 1, 1)
        self.output_file = Gtk.Button.new_with_label(self.afile)
        self.output_file.connect('clicked',
                                 self.on_button_output_file_clicked,
                                 self.main_window)
        self.grid.attach(self.output_file, 1, 0, 3, 1)
        hbox = Gtk.HBox()
        self.grid.attach(hbox, 0, 1, 4, 2)

        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolledwindow.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)
        scrolledwindow.set_size_request(700, 500)
        hbox.pack_start(scrolledwindow, True, True, 0)

        liststore = Gtk.ListStore(GdkPixbuf.Pixbuf, str, str)
        self.iconview = Gtk.IconView.new()
        self.iconview.set_model(liststore)
        self.iconview.set_pixbuf_column(0)
        self.iconview.set_text_column(1)
        self.iconview.set_item_width(-1)
        self.iconview.set_reorderable(True)

        scrolledwindow.add(self.iconview)

        vbox2 = Gtk.VBox(spacing=0)
        vbox2.set_border_width(5)
        hbox.pack_start(vbox2, False, False, 0)

        button1 = Gtk.Button()
        button1.set_size_request(40, 40)
        button1.set_tooltip_text(_('Up'))
        button1.set_image(
            Gtk.Image.new_from_stock(Gtk.STOCK_GO_UP, Gtk.IconSize.BUTTON))
        button1.connect('clicked', self.on_button_up_clicked)
        vbox2.pack_start(button1, False, False, 0)

        button2 = Gtk.Button()
        button2.set_size_request(40, 40)
        button2.set_tooltip_text(_('Down'))
        button2.set_image(Gtk.Image.new_from_stock(
            Gtk.STOCK_GO_DOWN, Gtk.IconSize.BUTTON))
        button2.connect('clicked', self.on_button_down_clicked)
        vbox2.pack_start(button2, False, False, 0)

        button3 = Gtk.Button()
        button3.set_size_request(40, 40)
        button3.set_tooltip_text(_('Add'))
        button3.set_image(Gtk.Image.new_from_stock(
            Gtk.STOCK_ADD, Gtk.IconSize.BUTTON))
        button3.connect('clicked', self.on_button_add_clicked)
        vbox2.pack_start(button3, False, False, 0)

        button4 = Gtk.Button()
        button4.set_size_request(40, 40)
        button4.set_tooltip_text(_('Remove'))
        button4.set_image(Gtk.Image.new_from_stock(
            Gtk.STOCK_REMOVE, Gtk.IconSize.BUTTON))
        button4.connect('clicked', self.on_button_remove_clicked)
        vbox2.pack_start(button4, False, False, 0)

        if self.files:
            position = 0
            model = self.iconview.get_model()
            for filename in self.files:
                pixbuf = tools.get_pixbuf_from_pdf(filename, 200)
                if pixbuf is not None:
                    position += 1
                    if self.iconview.get_item_width() < pixbuf.get_width():
                        self.iconview.set_item_width(pixbuf.get_width())
                    model.insert(position,
                                 [pixbuf,
                                  os.path.basename(filename),
                                  filename])

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

    def on_button_up_clicked(self, widget):
        selection = self.iconview.get_selected_items()
        if selection:
            model = self.iconview.get_model()
            selected_iter = model.get_iter(selection[0])
            previous_iter = model.iter_previous(selected_iter)
            if previous_iter is not None:
                model.swap(selected_iter, previous_iter)

    def on_button_down_clicked(self, widget):
        selection = self.iconview.get_selected_items()
        if selection:
            model = self.iconview.get_model()
            selected_iter = model.get_iter(selection[0])
            next_iter = model.iter_next(selected_iter)
            if next_iter is not None:
                model.swap(selected_iter, next_iter)

    def on_button_add_clicked(self, widget):
        selection = self.iconview.get_selected_items()
        if selection:
            model = self.iconview.get_model()
            position = int(str(selection[0]))
        else:
            model = self.iconview.get_model()
            position = len(model)
        dialog = Gtk.FileChooserDialog(_('Select one or more pdf files'),
                                       self,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL,
                                        Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN,
                                        Gtk.ResponseType.OK))
        dialog.set_default_response(Gtk.ResponseType.OK)
        dialog.set_select_multiple(True)
        dialog.set_current_folder(os.getenv('HOME'))
        filtert = Gtk.FileFilter()
        filtert.set_name(_('Pdf files'))
        filtert.add_mime_type('application/pdf')
        filtert.add_pattern('*.pdf')
        dialog.add_filter(filtert)
        preview = Gtk.Image()
        dialog.set_preview_widget(preview)
        dialog.connect('update-preview', update_preview_cb, preview)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filenames = dialog.get_filenames()
            if filenames:
                model = self.iconview.get_model()
                for filename in filenames:
                    pixbuf = tools.get_pixbuf_from_pdf(filename, 200)
                    if pixbuf is not None:
                        position += 1
                        if self.iconview.get_item_width() < pixbuf.get_width():
                            self.iconview.set_item_width(pixbuf.get_width())
                        model.insert(position,
                                     [pixbuf,
                                      os.path.basename(filename),
                                      filename])
        dialog.destroy()

    def on_button_remove_clicked(self, _):
        selection = self.iconview.get_selected_items()
        if selection:
            model = self.iconview.get_model()
            for element in selection:
                model.remove(model.get_iter(element))

    def get_pdf_files(self):
        files = []
        model = self.iconview.get_model()
        itert = model.get_iter_first()
        while(itert):
            files.append(model.get_value(itert, 2))
            itert = model.iter_next(itert)
        return files


if __name__ == '__main__':
    dialog = JoinPdfsDialog('Test', [], 'File', None)
    dialog.run()
    print(dialog.get_pdf_files())
