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
    gi.require_version('GLib', '2.0')
except ValueError as e:
    print(e)
    exit(1)
from gi.repository import Gtk
import os
import cairoapi as pdfapi
import doitinbackground
import tools
from combinedialog import CombineDialog
from comun import _
from createpdffromImagesdialog import CreatePDFFromImagesDialog
from flipdialog import FlipDialog
from joinpdfsdialog import JoinPdfsDialog
from paginatedialog import PaginateDialog
from passworddialog import PasswordDialog
from progreso import Progreso
from reducedialog import ReduceDialog
from resizedialog import ResizeDialog
from selectpagesdialog import SelectPagesDialog
from signdialog import SignDialog
from textmarkdialog import TextmarkDialog
from watermarkdialog import WatermarkDialog


def resize_pdf_pages(selected, window):
    files = tools.get_files(selected)
    if files:
        cd = ResizeDialog(_('Resize PDF'), window)
        if cd.run() == Gtk.ResponseType.ACCEPT:
            size = cd.get_resize()
            if cd.is_vertical():
                width = size[0]
                height = size[1]
            else:
                width = size[1]
                height = size[0]
            extension = cd.get_extension()
            cd.hide()
            if extension:
                dialog = Progreso(_('Resize PDF'), window, 1)
                diboo = doitinbackground.DoItInBackgroundResizePages(
                    files, extension, width, height)
                dialog.connect('i-want-stop', diboo.stop_it)
                diboo.connect('start', dialog.set_max_value)
                diboo.connect('todo', dialog.set_todo_label)
                diboo.connect('donef', dialog.set_fraction)
                diboo.connect('finished', dialog.end_progress)
                diboo.connect('interrupted', dialog.end_progress)
                diboo.start()
                dialog.run()
        cd.destroy()

def encrypt_files(selected, window):
    if selected:
        files = tools.get_files(selected)
        pd = PasswordDialog(_('Encrypt files'), window)
        if pd.run() == Gtk.ResponseType.ACCEPT:
            password = pd.get_password()
            pd.hide()
            dialog = Progreso(_('Encrypt files'), window, len(files))
            diboo = doitinbackground.DoitInBackgroundEncrypt(files,
                                                                password)
            dialog.connect('i-want-stop', diboo.stop_it)
            diboo.connect('start', dialog.set_max_value)
            diboo.connect('todo', dialog.set_todo_label)
            diboo.connect('done', dialog.increase)
            diboo.connect('finished', dialog.end_progress)
            diboo.connect('interrupted', dialog.end_progress)
            diboo.start()
            dialog.run()
        pd.destroy()

def decrypt_files(selected, window):
    if selected:
        files = tools.get_files(selected)
        pd = PasswordDialog(_('Decrypt files'), window)
        if pd.run() == Gtk.ResponseType.ACCEPT:
            password = pd.get_password()
            pd.hide()
            dialog = Progreso(_('Dencrypt files'), window, len(files))
            diboo = doitinbackground.DoitInBackgroundDecrypt(files,
                                                                password)
            dialog.connect('i-want-stop', diboo.stop_it)
            diboo.connect('start', dialog.set_max_value)
            diboo.connect('todo', dialog.set_todo_label)
            diboo.connect('done', dialog.increase)
            diboo.connect('finished', dialog.end_progress)
            diboo.connect('interrupted', dialog.end_progress)
            diboo.start()
            dialog.run()
        pd.destroy()

def convert_pdf_file_to_png(selected, window):
    files = tools.get_files(selected)
    if files:
        dialog = Progreso(_('Convert PDF to PNG'), window, len(files))
        diboo = doitinbackground.DoItInBackgroundToPNG(files)
        dialog.connect('i-want-stop', diboo.stop_it)
        diboo.connect('start', dialog.set_max_value)
        diboo.connect('todo', dialog.set_todo_label)
        diboo.connect('donef', dialog.set_fraction)
        diboo.connect('finished', dialog.end_progress)
        diboo.connect('interrupted', dialog.end_progress)
        diboo.start()
        dialog.run()

def combine_pdf_pages(selected, window):
    files = tools.get_files(selected)
    if files:
        cd = CombineDialog(_('Combine PDF pages'), window)
        if cd.run() == Gtk.ResponseType.ACCEPT:
            size = cd.get_size()
            if cd.is_vertical():
                width = size[0]
                height = size[1]
            else:
                width = size[1]
                height = size[0]
            filas = cd.get_rows()
            columnas = cd.get_columns()
            byrows = cd.is_sort_by_rows()
            margen = cd.get_margin()
            extension = cd.get_extension()
            cd.hide()
            if extension:
                dialog = Progreso(_('Combine PDF pages'), window, 1)
                diboo = doitinbackground.DoItInBackgroundCombine(
                    files, extension, filas, columnas, width, height,
                    margen, byrows)
                dialog.connect('i-want-stop', diboo.stop_it)
                diboo.connect('start', dialog.set_max_value)
                diboo.connect('todo', dialog.set_todo_label)
                diboo.connect('donef', dialog.set_fraction)
                diboo.connect('finished', dialog.end_progress)
                diboo.connect('interrupted', dialog.end_progress)
                diboo.start()
                dialog.run()
        cd.destroy()

def create_pdf_from_images(selected, window):
    files = tools.get_files(selected)
    if files:
        file_in = files[0]
        filename = os.path.splitext(file_in)[0]
        file_out = filename + '_from_images.pdf'
        cpfi = CreatePDFFromImagesDialog(
            _('Create PDF from images'), files, file_out, window)
        if cpfi.run() == Gtk.ResponseType.ACCEPT:
            cpfi.hide()
            files = cpfi.get_png_files()
            if cpfi.is_vertical():
                width, height = cpfi.get_dimensions()
            else:
                height, width = cpfi.get_dimensions()
            margin = cpfi.get_margin()
            file_out = cpfi.get_file_out()
            cpfi.destroy()
            if file_out:
                dialog = Progreso(_('Create PDF from images'),
                                    window,
                                    len(files))
                diboo = doitinbackground\
                    .DoItInBackgroundCreatePDFFromImages(file_out,
                                                            files,
                                                            width,
                                                            height,
                                                            margin)
                dialog.connect('i-want-stop', diboo.stop_it)
                diboo.connect('start', dialog.set_max_value)
                diboo.connect('todo', dialog.set_todo_label)
                diboo.connect('done', dialog.increase)
                diboo.connect('finished', dialog.end_progress)
                diboo.connect('interrupted', dialog.end_progress)
                diboo.start()
                dialog.run()
        cpfi.destroy()

def join_pdf_files(selected, window):
    files = tools.get_files(selected)
    if files:
        file_in = files[0]
        filename = os.path.splitext(file_in)[0]
        file_out = filename + '_joined_files.pdf'
        jpd = JoinPdfsDialog(_('Join PDF files'), files, file_out, window)
        if jpd.run() == Gtk.ResponseType.ACCEPT:
            files = jpd.get_pdf_files()
            file_out = jpd.get_file_out()
            jpd.hide()
            if files and file_out:
                dialog = Progreso(_('Join PDF files'), window, len(files))
                diboo = doitinbackground.DoItInBackgroundJoinPdf(
                    files, file_out)
                dialog.connect('i-want-stop', diboo.stop_it)
                diboo.connect('todo', dialog.set_todo_label)
                diboo.connect('donef', dialog.set_fraction)
                diboo.connect('finished', dialog.end_progress)
                diboo.connect('interrupted', dialog.end_progress)
                diboo.start()
                dialog.run()
        jpd.destroy()

def reduce(selected, window):
    files = tools.get_files(selected)
    if files:
        rd = ReduceDialog(_('Reduce PDF'), window)
        if rd.run() == Gtk.ResponseType.ACCEPT:
            dpi = rd.get_dpi()
            append = rd.get_append()
            rd.hide()
            if dpi and dpi != '0' and dpi.isdigit() and append:
                dialog = Progreso(_('Reduce PDF size'), window, len(files))
                diboo = doitinbackground.DoitInBackgroundWithArgs(tools.reduce_pdf, files, dpi, append)

                diboo.connect('done', dialog.increase)
                diboo.connect('todo', dialog.set_todo_label)
                diboo.connect('finished', dialog.end_progress)
                diboo.connect('interrupted', dialog.end_progress)
                dialog.connect('i-want-stop', diboo.stop_it)
                diboo.start()
                dialog.run()
        rd.destroy()

def operate(operation, selected, window):
    dialog = None
    title = ''
    extension = ''
    files = tools.get_files(selected)
    file_in = files[0]
    if file_in and os.path.exists(file_in):
        if operation == 'rotate':
            dialog = FlipDialog(file_in, window)
            title = _('Rotate and flip PDF')
            extension = '_rotated'
        elif operation == 'watermark':
            dialog = WatermarkDialog(filename=file_in, window=window)
            title = _('Watermark PDF')
            extension = '_watermarked'
        elif operation == 'textmark':
            dialog = TextmarkDialog(filename=file_in, window=window)
            title = _('Textmark PDF')
            extension = '_textmarked'
        elif operation == 'paginate':
            dialog = PaginateDialog(filename=file_in, window=window)
            title = _('Paginate PDF')
            extension = '_paginated'
        elif operation == 'sign':
            dialog = SignDialog(filename=file_in, window=window)
            title = _('Sign PDF')
            extension = '_signed'
        if dialog is not None:
            if dialog.run() == Gtk.ResponseType.ACCEPT:
                dialog.hide()
                pageOptions = dialog.pages
                progress_dialog = Progreso(title, window, 1)
                diboo = doitinbackground.DoitInBackgroundPages(
                    extension, file_in, pageOptions)
                diboo.connect('todo', progress_dialog.set_todo_label)
                diboo.connect('donef', progress_dialog.set_fraction)
                diboo.connect('finished', progress_dialog.end_progress)
                diboo.connect('interrupted', progress_dialog.end_progress)
                progress_dialog.connect('i-want-stop', diboo.stop_it)
                diboo.start()
                progress_dialog.run()
            dialog.destroy()

def remove_some_pages(selected, window):
    files = tools.get_files(selected)
    if files:
        file0 = files[0]
        filename = os.path.splitext(file0)[0]
        file_out = filename + '_removed_pages.pdf'
        spd = SelectPagesDialog(_('Remove PDF'),
                                file_out, window)
        if spd.run() == Gtk.ResponseType.ACCEPT:
            ranges = tools.get_ranges(spd.entry1.get_text())
            file_out = spd.get_file_out()
            spd.hide()
            if ranges:
                dialog = Progreso(_('Remove PDF'), window, 1)
                diboo = doitinbackground.DoitInBackgroundRemoveSomePages(
                    file0, file_out, ranges)
                diboo.connect('start', dialog.set_max_value)
                diboo.connect('done', dialog.increase)
                diboo.connect('finished', dialog.end_progress)
                diboo.connect('interrupted', dialog.end_progress)
                dialog.connect('i-want-stop', diboo.stop_it)
                diboo.start()
                dialog.run()
        spd.destroy()

def split_pdf_files(selected, window):
    files = tools.get_files(selected)
    if files:
        dialog = Progreso(_('Split PDF'), window, len(files))
        diboo = doitinbackground.DoitInBackground(
            pdfapi.split_pdf, files)
        diboo.connect('done', dialog.increase)
        diboo.connect('todo', dialog.set_todo_label)
        diboo.connect('finished', dialog.end_progress)
        diboo.connect('interrupted', dialog.end_progress)
        dialog.connect('i-want-stop', diboo.stop_it)
        diboo.start()
        dialog.run()

def extract_some_pages(selected, window):
    files = tools.get_files(selected)
    if files:
        spd = SelectPagesDialog(_('Extract pages from PDF'),
                                None, window)
        if spd.run() == Gtk.ResponseType.ACCEPT:
            ranges = tools.get_ranges(spd.entry1.get_text())
            spd.hide()
            if ranges:
                dialog = Progreso(_('Extract pages from PDF'),
                                    window, 1)
                diboo = doitinbackground.DoitInBackgroundExtractSomePages(
                    files, ranges)
                diboo.connect('todo', dialog.set_todo_label)
                diboo.connect('donef', dialog.set_fraction)
                diboo.connect('finished', dialog.end_progress)
                diboo.connect('interrupted', dialog.end_progress)
                dialog.connect('i-want-stop', diboo.stop_it)
                diboo.start()
                dialog.run()
        spd.destroy()

def extract_text(selected, window):
    files = tools.get_files(selected)
    if files:
        file0 = files[0]
        filename = os.path.splitext(file0)[0]
        file_out = filename + '.txt'
        print(file_out)
        file_out = tools.dialog_save_as_text(
            _('Select file to save extracted text'), file_out, window)
        if file_out:
            pdfapi.extract_text(file0, file_out)

class FileTemp():
    def __init__(self, afile):
        self.afile = afile

    def get_uri(self):
        return self.afile


if __name__ == '__main__':
    file_in = FileTemp('file:///home/lorenzo/Escritorio/quijote.pdf')
    #operate('rotate', [file_in], None)
    reduce([file_in], None)
