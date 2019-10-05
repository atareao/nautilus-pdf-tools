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
except Exception as e:
    print(e)
    exit(1)
from gi.repository import Gtk
from gi.repository import GdkPixbuf
import os
import comun
import tools
from comun import _
from comun import MIMETYPES_IMAGE
from tools import update_preview_cb, center_dialog


class CreatePDFFromImagesDialog(Gtk.Dialog):
    def __init__(self, title, files, afile, window):
        Gtk.Dialog.__init__(self, title, window)
        self.set_modal(True)
        self.set_destroy_with_parent(True)
        self.add_button(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT)
        self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)

        self.set_icon_from_file(comun.ICON)
        self.connect('destroy', self.close_application)

        vbox0 = Gtk.VBox(spacing=5)
        vbox0.set_border_width(5)
        self.get_content_area().add(vbox0)

        frame1 = Gtk.Frame()
        vbox0.add(frame1)
        table1 = Gtk.Table(rows=4, columns=2, homogeneous=False)
        table1.set_border_width(5)
        table1.set_col_spacings(5)
        table1.set_row_spacings(5)
        frame1.add(table1)
        label1 = Gtk.Label(_('Paper size') + ':')
        label1.set_tooltip_text(_('Select the size of the output file'))
        label1.set_alignment(0, .5)
        table1.attach(label1, 0, 1, 0, 1,
                      xoptions=Gtk.AttachOptions.FILL,
                      yoptions=Gtk.AttachOptions.SHRINK)
        label2 = Gtk.Label(_('Orientation') + ':')
        label2.set_tooltip_text(_('Select the orientation of the page'))
        label2.set_alignment(0, .5)
        table1.attach(label2, 0, 1, 1, 2,
                      xoptions=Gtk.AttachOptions.FILL,
                      yoptions=Gtk.AttachOptions.SHRINK)

        label3 = Gtk.Label(_('Margen') + ':')
        label3.set_tooltip_text(_('Select the size of the margin'))
        label3.set_alignment(0, .5)
        table1.attach(label3, 0, 1, 2, 3,
                      xoptions=Gtk.AttachOptions.FILL,
                      yoptions=Gtk.AttachOptions.SHRINK)
        label4 = Gtk.Label(_('Output file') + ':')
        label4.set_tooltip_text(_('Select the output file'))
        label4.set_alignment(0, .5)
        table1.attach(label4, 0, 1, 3, 4,
                      xoptions=Gtk.AttachOptions.FILL,
                      yoptions=Gtk.AttachOptions.SHRINK)

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
        renderer_text = Gtk.CellRendererText()
        self.entry1.pack_start(renderer_text, True)
        self.entry1.add_attribute(renderer_text, "text", 0)
        self.entry1.set_active(0)
        table1.attach(self.entry1, 1, 2, 0, 1,
                      xoptions=Gtk.AttachOptions.FILL,
                      yoptions=Gtk.AttachOptions.SHRINK)

        liststore = Gtk.ListStore(str)
        liststore.append([_('Vertical')])
        liststore.append([_('Horizontal')])
        self.entry2 = Gtk.ComboBox.new_with_model(model=liststore)
        renderer_text = Gtk.CellRendererText()
        self.entry2.pack_start(renderer_text, True)
        self.entry2.add_attribute(renderer_text, "text", 0)
        self.entry2.set_active(0)
        table1.attach(self.entry2, 1, 2, 1, 2,
                      xoptions=Gtk.AttachOptions.FILL,
                      yoptions=Gtk.AttachOptions.SHRINK)
        liststore = Gtk.ListStore(str)
        liststore.append([_('No margin')])
        liststore.append([_('small margin')])
        liststore.append([_('big margin')])
        self.entry3 = Gtk.ComboBox.new_with_model(model=liststore)
        renderer_text = Gtk.CellRendererText()
        self.entry3.pack_start(renderer_text, True)
        self.entry3.add_attribute(renderer_text, "text", 0)
        self.entry3.set_active(0)
        table1.attach(self.entry3, 1, 2, 2, 3,
                      xoptions=Gtk.AttachOptions.FILL,
                      yoptions=Gtk.AttachOptions.SHRINK)
        self.output_file = Gtk.Button.new_with_label(afile)
        self.output_file.connect('clicked',
                                 self.on_button_output_file_clicked,
                                 window)
        table1.attach(self.output_file, 1, 2, 3, 4,
                      xoptions=Gtk.AttachOptions.FILL,
                      yoptions=Gtk.AttachOptions.SHRINK)

        hbox = Gtk.HBox()
        vbox0.pack_start(hbox, True, True, 0)

        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolledwindow.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)
        scrolledwindow.set_size_request(450, 300)
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

        self.button1 = Gtk.Button()
        self.button1.set_size_request(40, 40)
        self.button1.set_tooltip_text(_('Up'))
        self.button1.set_image(
            Gtk.Image.new_from_stock(Gtk.STOCK_GO_UP, Gtk.IconSize.BUTTON))
        self.button1.connect('clicked', self.on_button_up_clicked)
        vbox2.pack_start(self.button1, False, False, 0)

        self.button2 = Gtk.Button()
        self.button2.set_size_request(40, 40)
        self.button2.set_tooltip_text(_('Down'))
        self.button2.set_image(
            Gtk.Image.new_from_stock(Gtk.STOCK_GO_DOWN, Gtk.IconSize.BUTTON))
        self.button2.connect('clicked', self.on_button_down_clicked)
        vbox2.pack_start(self.button2, False, False, 0)

        self.button3 = Gtk.Button()
        self.button3.set_size_request(40, 40)
        self.button3.set_tooltip_text(_('Add'))
        self.button3.set_image(
            Gtk.Image.new_from_stock(Gtk.STOCK_ADD, Gtk.IconSize.BUTTON))
        self.button3.connect('clicked', self.on_button_add_clicked)
        vbox2.pack_start(self.button3, False, False, 0)

        self.button4 = Gtk.Button()
        self.button4.set_size_request(40, 40)
        self.button4.set_tooltip_text(_('Remove'))
        self.button4.set_image(
            Gtk.Image.new_from_stock(Gtk.STOCK_REMOVE, Gtk.IconSize.BUTTON))
        self.button4.connect('clicked', self.on_button_remove_clicked)
        vbox2.pack_start(self.button4, False, False, 0)

        if files:
            position = 0
            model = self.iconview.get_model()
            for filename in files:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(filename,
                                                                200, 200)
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
            filenames = dialog.get_filenames()
            if filenames:
                model = self.iconview.get_model()
                for filename in filenames:
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(filename,
                                                                    200, 200)
                    if pixbuf is not None:
                        position += 1
                        if self.iconview.get_item_width() < pixbuf.get_width():
                            self.iconview.set_item_width(pixbuf.get_width())
                        model.insert(position,
                                     [pixbuf,
                                      os.path.basename(filename),
                                      filename])
        dialog.destroy()

    def on_button_remove_clicked(self, widget):
        selection = self.iconview.get_selected_items()
        if selection:
            model = self.iconview.get_model()
            for element in selection:
                model.remove(model.get_iter(element))

    def get_png_files(self):
        files = []
        model = self.iconview.get_model()
        itera = model.get_iter_first()
        while(itera):
            files.append(model.get_value(itera, 2))
            itera = model.iter_next(itera)
        return files

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

    def get_margin(self):
        tree_iter = self.entry3.get_active_iter()
        if tree_iter is not None:
            model = self.entry3.get_model()
            vertical = model[tree_iter][0]
            if vertical == _('small margin'):
                return 1
            elif vertical == _('big margin'):
                return 2
        return 0

    def close_application(self, widget):
        self.hide()


if __name__ == '__main__':
    dialog = CreatePDFFromImagesDialog('Create', [], 'output_file', None)
    dialog.run()
    print(dialog.get_png_files())
