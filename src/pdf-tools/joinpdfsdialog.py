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
except Exception as e:
    print(e)
    exit(1)
from gi.repository import Gtk
from gi.repository import Gdk
import os
import comun
import tools
import mimetypes
from comun import _
from comun import MIMETYPES_PDF
from urllib import unquote_plus


class JoinPdfsDialog(Gtk.Dialog):
    def __init__(self, title, files, afile):
        Gtk.Dialog.__init__(
            self,
            title,
            None,
            Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            (Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT,
             Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        self.set_size_request(450, 300)
        self.set_resizable(False)
        self.set_icon_from_file(comun.ICON)
        self.connect('destroy', self.close_application)
        #
        vbox0 = Gtk.VBox(spacing=5)
        vbox0.set_border_width(5)
        self.get_content_area().add(vbox0)
        #
        #
        frame1 = Gtk.Frame()
        vbox0.pack_start(frame1, True, True, 0)
        table1 = Gtk.Table(rows=1, columns=2, homogeneous=False)
        table1.set_border_width(5)
        table1.set_col_spacings(5)
        table1.set_row_spacings(5)
        frame1.add(table1)
        label1 = Gtk.Label(_('Output file') + ':')
        label1.set_tooltip_text(_('Select the output file'))
        label1.set_alignment(0, .5)
        table1.attach(label1, 0, 1, 0, 1,
                      xoptions=Gtk.AttachOptions.SHRINK,
                      yoptions=Gtk.AttachOptions.SHRINK)
        self.output_file = Gtk.Button.new_with_label(afile)
        self.output_file.connect('clicked', self.on_button_output_file_clicked)
        table1.attach(self.output_file, 1, 2, 0, 1,
                      xoptions=Gtk.AttachOptions.EXPAND,
                      yoptions=Gtk.AttachOptions.SHRINK)
        hbox = Gtk.HBox()
        vbox0.pack_start(hbox, True, True, 0)
        #
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolledwindow.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)
        scrolledwindow.set_size_request(450, 300)
        hbox.pack_start(scrolledwindow, True, True, 0)
        self.store = Gtk.ListStore(str)
        self.treeview = Gtk.TreeView(model=self.store)
        self.treeview.append_column(
            Gtk.TreeViewColumn(_('Pdf file'), Gtk.CellRendererText(), text=0))
        # set icon for drag operation
        self.treeview.connect('drag-begin', self.drag_begin)
        self.treeview.connect('drag-data-get', self.drag_data_get_data)
        self.treeview.connect('drag-data-received', self.drag_data_received)
        #
        dnd_list = [
            Gtk.TargetEntry.new('text/uri-list', 0, 100),
            Gtk.TargetEntry.new('text/plain', 0, 80)]
        self.treeview.drag_source_set(
            Gdk.ModifierType.BUTTON1_MASK, dnd_list, Gdk.DragAction.COPY)
        self.treeview.drag_source_add_uri_targets()
        dnd_list = Gtk.TargetEntry.new("text/uri-list", 0, 0)
        self.treeview.drag_dest_set(
            Gtk.DestDefaults.MOTION | Gtk.DestDefaults.HIGHLIGHT |
            Gtk.DestDefaults.DROP,
            [dnd_list],
            Gdk.DragAction.MOVE)
        self.treeview.drag_dest_add_uri_targets()
        #
        scrolledwindow.add(self.treeview)
        #
        vbox2 = Gtk.VBox(spacing=0)
        vbox2.set_border_width(5)
        hbox.pack_start(vbox2, False, False, 0)
        #
        self.button1 = Gtk.Button()
        self.button1.set_size_request(40, 40)
        self.button1.set_tooltip_text(_('Up'))
        self.button1.set_image(
            Gtk.Image.new_from_stock(Gtk.STOCK_GO_UP, Gtk.IconSize.BUTTON))
        self.button1.connect('clicked', self.on_button_up_clicked)
        vbox2.pack_start(self.button1, False, False, 0)
        #
        self.button2 = Gtk.Button()
        self.button2.set_size_request(40, 40)
        self.button2.set_tooltip_text(_('Down'))
        self.button2.set_image(Gtk.Image.new_from_stock(
            Gtk.STOCK_GO_DOWN, Gtk.IconSize.BUTTON))
        self.button2.connect('clicked', self.on_button_down_clicked)
        vbox2.pack_start(self.button2, False, False, 0)
        #
        self.button3 = Gtk.Button()
        self.button3.set_size_request(40, 40)
        self.button3.set_tooltip_text(_('Add'))
        self.button3.set_image(Gtk.Image.new_from_stock(
            Gtk.STOCK_ADD, Gtk.IconSize.BUTTON))
        self.button3.connect('clicked', self.on_button_add_clicked)
        vbox2.pack_start(self.button3, False, False, 0)
        #
        self.button4 = Gtk.Button()
        self.button4.set_size_request(40, 40)
        self.button4.set_tooltip_text(_('Remove'))
        self.button4.set_image(Gtk.Image.new_from_stock(
            Gtk.STOCK_REMOVE, Gtk.IconSize.BUTTON))
        self.button4.connect('clicked', self.on_button_remove_clicked)
        vbox2.pack_start(self.button4, False, False, 0)
        #
        for afile in files:
            self.store.append([afile])
        #
        self.show_all()

    def on_button_output_file_clicked(self, widget):
        file_out = tools.dialog_save_as(
            _('Select file to save new file'), self.output_file.get_label())
        if file_out:
            self.output_file.set_label(file_out)

    def get_file_out(self):
        return self.output_file.get_label()

    def drag_begin(self, widget, context):
        pass

    def drag_data_get_data(self, treeview, context, selection, target_id,
                           etime):
        pass

    def drag_data_received(self, widget, drag_context, x, y, selection_data,
                           info, timestamp):
        selection = self.treeview.get_selection()
        if selection.count_selected_rows() > 0:
            model, iter = selection.get_selected()
            treepath = model.get_path(iter)
            position = int(str(treepath))
        else:
            model = self.treeview.get_model()
            position = len(model)
        for filename in selection_data.get_uris():
            if len(filename) > 8:
                filename = unquote_plus(filename)
                filename = filename[7:]
                mime = mimetypes.guess_type(filename)
                if os.path.exists(filename):
                    mime = mimetypes.guess_type(filename)[0]
                    if mime in MIMETYPES_PDF:
                        model.insert(position + 1, [filename])
        return True

    def on_button_up_clicked(self, widget):
        selection = self.treeview.get_selection()
        if selection.count_selected_rows() > 0:
            model, iter = selection.get_selected()
            treepath = model.get_path(iter)
            path = int(str(treepath))
            if path > 0:
                previous_path = Gtk.TreePath.new_from_string(str(path - 1))
                previous_iter = model.get_iter(previous_path)
                model.swap(iter, previous_iter)

    def on_button_down_clicked(self, widget):
        selection = self.treeview.get_selection()
        if selection.count_selected_rows() > 0:
            model, iter = selection.get_selected()
            treepath = model.get_path(iter)
            path = int(str(treepath))
            if path < len(model) - 1:
                next_path = Gtk.TreePath.new_from_string(str(path + 1))
                next_iter = model.get_iter(next_path)
                model.swap(iter, next_iter)

    def on_button_add_clicked(self, widget):
        selection = self.treeview.get_selection()
        if selection.count_selected_rows() > 0:
            model, iter = selection.get_selected()
            treepath = model.get_path(iter)
            position = int(str(treepath))
        else:
            model = self.treeview.get_model()
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
        filter = Gtk.FileFilter()
        filter.set_name(_('Pdf files'))
        filter.add_mime_type('application/pdf')
        filter.add_pattern('*.pdf')
        dialog.add_filter(filter)
        preview = Gtk.Image()
        dialog.set_preview_widget(preview)
        dialog.connect('update-preview', self.update_preview_cb, preview)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filenames = dialog.get_filenames()
            if len(filenames) > 0:
                for i, filename in enumerate(filenames):
                    model.insert(position + i + 1, [filename])
        dialog.destroy()

    def update_preview_cb(self, file_chooser, preview):
        filename = file_chooser.get_preview_filename()
        try:
            print('---', filename, '---')
            pixbuf = tools.get_surface_from_pdf(filename, 512)
            if pixbuf is not None:
                preview.set_from_surface(pixbuf)
                has_preview = True
            else:
                has_preview = False
        except Exception as e:
            print(e)
            has_preview = False
        file_chooser.set_preview_widget_active(has_preview)
        return

    def on_button_remove_clicked(self, widget):
        selection = self.treeview.get_selection()
        if selection.count_selected_rows() > 0:
            model, iter = selection.get_selected()
            model.remove(iter)

    def close_application(self, widget):
        self.hide()

    def get_pdf_files(self):
        files = []
        iter = self.store.get_iter_first()
        while(iter):
            files.append(self.store.get_value(iter, 0))
            iter = self.store.iter_next(iter)
        return files


if __name__ == '__main__':
    dialog = JoinPdfsDialog('Test', [], 'File')
    dialog.run()
