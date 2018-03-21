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
    gi.require_version('GObject', '2.0')
    gi.require_version('GLib', '2.0')
except Exception as e:
    print(e)
    exit(1)
from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import GLib
import cairoapi as pdfapi
from resizedialog import ResizeDialog
from combinedialog import CombineDialog
from createpdffromImagesdialog import CreatePDFFromImagesDialog
from joinpdfsdialog import JoinPdfsDialog
from paginatedialog import PaginateDialog
from textmarkdialog import TextmarkDialog
from watermarkdialog import WatermarkDialog
from flipdialog import FlipDialog
from selectpagesrotatedialog import SelectPagesRotateDialog
from selectpagesdialog import SelectPagesDialog
from doitinbackground import DoitInBackground, DoitInBackgroundOnlyOne,\
    DoitInBackgroundWithArgs, DoItInBackgroundJoinPdf,\
    DoItInBackgroundResizePages, DoItInBackgroundToPNG,\
    DoItInBackgroundCreatePDFFromImages, DoItInBackgroundCombine,\
    DoitInBackgroundPaginage, DoitInBackgroundTextMark,\
    DoitInBackgroundWaterMark
from progreso import Progreso
import cairoapi
import tools
from comun import _
from comun import ROTATE_000, ROTATE_090, ROTATE_180, ROTATE_270
import os


class PDFManager(GObject.GObject):

    def __init__(self):
        GObject.GObject.__init__(self)

    def emit(self, *args):
        GLib.idle_add(GObject.GObject.emit, self, *args)

    def resize_pdf_pages(self, selected, window):
        files = tools.get_files(selected)
        if files:
            cd = ResizeDialog(_('Resize PDF'), window)
            if cd.run() == Gtk.ResponseType.ACCEPT:
                size = cd.get_size()
                if cd.is_vertical():
                    width = size[0]
                    height = size[1]
                else:
                    width = size[1]
                    height = size[0]
                extension = cd.get_extension()
                cd.destroy()
                if len(extension) > 0:
                    dialog = Progreso(_('Resize PDF'), window, 1)
                    diboo = DoItInBackgroundResizePages(files, extension,
                                                        width, height)
                    dialog.connect('i-want-stop', diboo.stop_it)
                    diboo.connect('start', dialog.set_max_value)
                    diboo.connect('todo', dialog.set_todo_label)
                    diboo.connect('donef', dialog.set_fraction)
                    diboo.connect('finished', dialog.close)
                    diboo.connect('interrupted', dialog.close)
                    diboo.start()
                    dialog.run()
            cd.destroy()

    def convert_pdf_file_to_png(self, selected, window):
        files = tools.get_files(selected)
        if len(files):
            dialog = Progreso(_('Convert PDF to PNG'), window, len(files))
            diboo = DoItInBackgroundToPNG(files)
            dialog.connect('i-want-stop', diboo.stop_it)
            diboo.connect('start', dialog.set_max_value)
            diboo.connect('todo', dialog.set_todo_label)
            diboo.connect('donef', dialog.set_fraction)
            diboo.connect('finished', dialog.close)
            diboo.connect('interrupted', dialog.close)
            diboo.start()
            dialog.run()

    def combine_pdf_pages(self, selected, window):
        files = tools.get_files(selected)
        if files and len(files):
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
                cd.destroy()
                if len(extension) > 0:
                    dialog = Progreso(_('Combine PDF pages'), window, 1)
                    diboo = DoItInBackgroundCombine(files, extension, filas,
                                                    columnas, width, height,
                                                    margen, byrows)
                    dialog.connect('i-want-stop', diboo.stop_it)
                    diboo.connect('start', dialog.set_max_value)
                    diboo.connect('todo', dialog.set_todo_label)
                    diboo.connect('donef', dialog.set_fraction)
                    diboo.connect('finished', dialog.close)
                    diboo.connect('interrupted', dialog.close)
                    diboo.start()
                    dialog.run()

    def create_pdf_from_images(self, selected, window):
        files = tools.get_files(selected)
        if files:
            file_in = files[0]
            filename, filext = os.path.splitext(file_in)
            file_out = filename + '_from_images.pdf'
            cpfi = CreatePDFFromImagesDialog(
                _('Create PDF from images'), files, file_out, window)
            if cpfi.run() == Gtk.ResponseType.ACCEPT:
                cpfi.hide()
                files = cpfi.get_png_files()
                if cpfi.is_vertical():
                    width, height = cpfi.get_size()
                else:
                    height, width = cpfi.get_size()
                margin = cpfi.get_margin()
                file_out = cpfi.get_file_out()
                cpfi.destroy()
                if file_out:
                    dialog = Progreso(_('Create PDF from images'),
                                      window,
                                      len(files))
                    diboo = DoItInBackgroundCreatePDFFromImages(file_out,
                                                                files,
                                                                width,
                                                                height,
                                                                margin)
                    dialog.connect('i-want-stop', diboo.stop_it)
                    diboo.connect('start', dialog.set_max_value)
                    diboo.connect('todo', dialog.set_todo_label)
                    diboo.connect('done', dialog.increase)
                    diboo.connect('finished', dialog.close)
                    diboo.connect('interrupted', dialog.close)
                    diboo.start()
                    dialog.run()
            cpfi.destroy()

    def join_pdf_files(self, selected, window):
        files = tools.get_files(selected)
        if files:
            file_in = files[0]
            filename, filext = os.path.splitext(file_in)
            file_out = filename + '_joined_files.pdf'
            jpd = JoinPdfsDialog(_('Join PDF files'), files, file_out, window)
            if jpd.run() == Gtk.ResponseType.ACCEPT:
                files = jpd.get_pdf_files()
                file_out = jpd.get_file_out()
                jpd.destroy()
                if len(files) > 0 and file_out:
                    dialog = Progreso(_('Join PDF files'), window, len(files))
                    diboo = DoItInBackgroundJoinPdf(files, file_out)
                    dialog.connect('i-want-stop', diboo.stop_it)
                    diboo.connect('todo', dialog.set_todo_label)
                    diboo.connect('donef', dialog.set_fraction)
                    diboo.connect('finished', dialog.close)
                    diboo.connect('interrupted', dialog.close)
                    diboo.start()
                    dialog.run()
            jpd.destroy()

    def paginate(self, selected, window):
        files = tools.get_files(selected)
        if len(files) > 0:
            file0 = files[0]
            wd = PaginateDialog(file0, window)
            if wd.run() == Gtk.ResponseType.ACCEPT:
                wd.hide()
                color = wd.get_color()
                font = wd.get_font()
                size = wd.get_size()
                hoption = wd.get_horizontal_option()
                voption = wd.get_vertical_option()
                horizontal_margin = wd.get_horizontal_margin()
                vertical_margin = wd.get_vertical_margin()
                extension = wd.get_extension()
                dialog = Progreso(_('Paginate PDF'), window, len(files))
                diboo = DoitInBackgroundPaginage(files, color, font, size,
                                                 hoption, voption,
                                                 horizontal_margin,
                                                 vertical_margin,
                                                 extension)
                dialog.connect('i-want-stop', diboo.stop_it)
                diboo.connect('todo', dialog.set_todo_label)
                diboo.connect('donef', dialog.set_fraction)
                diboo.connect('finished', dialog.close)
                diboo.connect('interrupted', dialog.close)
                diboo.start()
                dialog.run()
            wd.destroy()

    def reduce(self, selected, window):
        files = tools.get_files(selected)
        dialog = Progreso(_('Reduce PDF size'), window, len(files))
        diboo = DoitInBackground(
            tools.reduce_pdf, files)
        diboo.connect('done', dialog.increase)
        diboo.connect('todo', dialog.set_todo_label)
        diboo.connect('finished', dialog.close)
        diboo.connect('interrupted', dialog.close)
        dialog.connect('i-want-stop', diboo.stop_it)
        diboo.start()
        dialog.run()

    def textmark(self, selected, window):
        files = tools.get_files(selected)
        if len(files) > 0:
            file0 = files[0]
            wd = TextmarkDialog(file0, window)
            if wd.run() == Gtk.ResponseType.ACCEPT:
                wd.hide()
                text = wd.get_text()
                color = wd.get_color()
                font = wd.get_font()
                size = wd.get_size()
                hoption = wd.get_horizontal_option()
                voption = wd.get_vertical_option()
                horizontal_margin = wd.get_horizontal_margin()
                vertical_margin = wd.get_vertical_margin()
                extension = wd.get_extension()
                dialog = Progreso(_('Textmark PDF'), window, len(files))
                diboo = DoitInBackgroundTextMark(files, text, color, font,
                                                 size, hoption, voption,
                                                 horizontal_margin,
                                                 vertical_margin, extension)
                diboo.connect('todo', dialog.set_todo_label)
                diboo.connect('donef', dialog.set_fraction)
                diboo.connect('finished', dialog.close)
                diboo.connect('interrupted', dialog.close)
                dialog.connect('i-want-stop', diboo.stop_it)
                diboo.start()
                dialog.run()
            wd.destroy()

    def watermark(self, selected, window):
        files = tools.get_files(selected)
        if len(files) > 0:
            file0 = files[0]
            wd = WatermarkDialog(file0, window)
            if wd.run() == Gtk.ResponseType.ACCEPT:
                wd.hide()
                hoption = wd.get_horizontal_option()
                voption = wd.get_vertical_option()
                horizontal_margin = wd.get_horizontal_margin()
                vertical_margin = wd.get_vertical_margin()
                zoom = float(wd.get_watermark_zoom() / 100.0)
                image = wd.get_image_filename()
                extension = wd.get_extension()
                dialog = Progreso(_('Watermark PDF'), window, len(files))
                diboo = DoitInBackgroundWaterMark(files, image, hoption,
                                                  voption, horizontal_margin,
                                                  vertical_margin, zoom,
                                                  extension)
                diboo.connect('todo', dialog.set_todo_label)
                diboo.connect('donef', dialog.set_fraction)
                diboo.connect('finished', dialog.close)
                diboo.connect('interrupted', dialog.close)
                dialog.connect('i-want-stop', diboo.stop_it)
                diboo.start()
                dialog.run()
            wd.destroy()

    def rotate_or_flip(self, selected, window):
        files = tools.get_files(selected)
        if len(files) > 0:
            file0 = files[0]
            fd = FlipDialog(_('Rotate PDF'), file0, window)
            if fd.run() == Gtk.ResponseType.ACCEPT:
                fd.hide()
                if fd.rbutton1.get_active():
                    rotate = ROTATE_000
                elif fd.rbutton2.get_active():
                    rotate = ROTATE_090
                elif fd.rbutton3.get_active():
                    rotate = ROTATE_180
                elif fd.rbutton4.get_active():
                    rotate = ROTATE_270
                flip_vertical = fd.switch1.get_active()
                flip_horizontal = fd.switch2.get_active()
                overwrite = fd.rbutton0.get_active()
                dialog = Progreso(_('Rotate PDF'), window, len(files))
                diboo = DoitInBackgroundWithArgs(
                    cairoapi.rotate_and_flip_pages, files, rotate,
                    flip_vertical, flip_horizontal, overwrite)
                diboo.connect('done', dialog.increase)
                diboo.connect('todo', dialog.set_todo_label)
                diboo.connect('finished', dialog.close)
                diboo.connect('interrupted', dialog.close)
                dialog.connect('i-want-stop', diboo.stop_it)
                diboo.start()
                dialog.run()
            fd.destroy()

    def rotate_some_pages(self, selected, window):
        files = tools.get_files(selected, window)
        if files:
            file0 = files[0]
            filename, filext = os.path.splitext(file0)
            file_out = filename + '_rotated.pdf'
            last_page = cairoapi.get_num_of_pages(file0)
            spd = SelectPagesRotateDialog(_('Rotate PDF'), last_page,
                                          file_out, window)
            if spd.run() == Gtk.ResponseType.ACCEPT:
                ranges = tools.get_ranges(spd.entry1.get_text())
                if spd.rbutton1.get_active():
                    degrees = 270
                elif spd.rbutton2.get_active():
                    degrees = 90
                else:
                    degrees = 180
                spd.destroy()
                if len(ranges) > 0:
                    dialog = Progreso(_('Rotate PDF'), window, 1)
                    diboo = DoitInBackgroundOnlyOne(
                        pdfapi.rotate_ranges_in_pdf, file0, file_out,
                        degrees, ranges)
                    diboo.connect('done', dialog.increase)
                    diboo.connect('finished', dialog.close)
                    diboo.connect('interrupted', dialog.close)
                    diboo.start()
                    dialog.run()
            else:
                spd.destroy()

    def remove_some_pages(self, selected, window):
        files = tools.get_files(selected)
        if files:
            file0 = files[0]
            filename, filext = os.path.splitext(file0)
            file_out = filename + '_removed_pages.pdf'
            last_page = cairoapi.get_num_of_pages(file0)
            spd = SelectPagesDialog(_('Remove PDF'), last_page,
                                    file_out, window)
            if spd.run() == Gtk.ResponseType.ACCEPT:
                ranges = tools.get_ranges(spd.entry1.get_text())
                file_out = spd.get_file_out()
                spd.destroy()
                if len(ranges) > 0:
                    dialog = Progreso(_('Remove PDF'), window, 1)
                    diboo = DoitInBackgroundOnlyOne(
                        pdfapi.remove_ranges, file0, file_out, ranges)
                    diboo.connect('done', dialog.increase)
                    diboo.connect('finished', dialog.close)
                    diboo.connect('interrupted', dialog.close)
                    diboo.start()
                    dialog.run()

            else:
                spd.destroy()

    def split_pdf_files(self, selected, window):
        files = tools.get_files(selected)
        if files:
            dialog = Progreso(_('Split PDF'), window, len(files))
            diboo = DoitInBackground(cairoapi.split_pdf, files)
            diboo.connect('done', dialog.increase)
            diboo.connect('todo', dialog.set_todo_label)
            diboo.connect('finished', dialog.close)
            diboo.connect('interrupted', dialog.close)
            dialog.connect('i-want-stop', diboo.stop_it)
            diboo.start()
            dialog.run()

    def extract_some_pages(self, selected, window):
        files = tools.get_files(selected)
        if files:
            file0 = files[0]
            filename, filext = os.path.splitext(file0)
            file_out = filename + '_extracted_pages.pdf'
            last_page = cairoapi.get_num_of_pages(file0)
            spd = SelectPagesDialog(_('Extract pages from PDF'), last_page,
                                    file_out, window)
            if spd.run() == Gtk.ResponseType.ACCEPT:
                ranges = tools.get_ranges(spd.entry1.get_text())
                file_out = spd.get_file_out()
                spd.destroy()
                if len(ranges) > 0:
                    dialog = Progreso(_('Extract pages from PDF'),
                                      window, 1)
                    diboo = DoitInBackgroundOnlyOne(
                        pdfapi.extract_ranges, file0, file_out, ranges)
                    diboo.connect('done', dialog.increase)
                    diboo.connect('finished', dialog.close)
                    diboo.connect('interrupted', dialog.close)
                    diboo.start()
                    dialog.run()
            else:
                spd.destroy()

    def extract_text(self, selected, window):
        files = tools.get_files(selected)
        if files:
            file0 = files[0]
            filename, filext = os.path.splitext(file0)
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
    files = [
        FileTemp('file:///home/lorenzo/Escritorio/pdfs/otros/2016_prysmiancatalogobt_ 2016.pdf'),
        FileTemp('file:///home/lorenzo/Escritorio/pdfs/otros/capitulo-g-proteccion-circuitos.pdf'),
        FileTemp('file:///home/lorenzo/Escritorio/pdfs/otros/guia_bt_anexo_2_sep03R1.pdf')
        # FileTemp('file:///home/lorenzo/Escritorio/pdfs/otros/guia_bt_anexo_2_sep03R1_01.png'),
        # FileTemp('file:///home/lorenzo/Escritorio/pdfs/otros/guia_bt_anexo_2_sep03R1_02.png'),
        # FileTemp('file:///home/lorenzo/Escritorio/pdfs/otros/guia_bt_anexo_2_sep03R1_03.png'),
        # FileTemp('file:///home/lorenzo/Escritorio/pdfs/otros/guia_bt_anexo_2_sep03R1_04.png'),
        # FileTemp('file:///home/lorenzo/Escritorio/pdfs/otros/guia_bt_anexo_2_sep03R1_05.png'),
    ]
    pdfmanager = PDFManager()
    # pdfmanager.create_pdf_from_images(files, None)
    # pdfmanager.join_pdf_files(files, None)
    # pdfmanager.resize_pdf_pages(files, None)
    # pdfmanager.convert_pdf_file_to_png(files, None)
    # pdfmanager.combine_pdf_pages(files, None)
    # pdfmanager.paginate(files, None)
    # pdfmanager.reduce(files, None)
    # pdfmanager.textmark(files, None)
    pdfmanager.watermark(files, None)