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

import PyPDF2
import os
from comun import ROTATE_090
import tools
import shutil


def get_num_of_pages(file_in):
    file_in = open(file_in, 'rb')
    reader = PyPDF2.PdfFileReader(file_in)
    ans = reader.getNumPages()
    file_in.close()
    return ans


def resize(file_in_name, file_out_name, width=1189, height=1682):
    file_in = open(file_in_name, 'rb')
    file_out = open(file_out_name, 'wb')
    reader = PyPDF2.PdfFileReader(file_in)
    writer = PyPDF2.PdfFileWriter()
    for i in range(0, reader.getNumPages()):
        page = reader.getPage(i)
        page.scaleTo(width, height)
        writer.addPage(page)
    writer.write(file_out)
    file_out.close()
    file_in.close()


def remove_ranges(file_in_name, file_out_name, ranges):
    file_in = open(file_in_name, 'rb')
    pages = tools.get_pages_from_ranges(ranges)
    reader = PyPDF2.PdfFileReader(file_in)
    writer = PyPDF2.PdfFileWriter()
    for i in range(0, reader.getNumPages()):
        if i+1 not in pages:
            page = reader.getPage(i)
            writer.addPage(page)
    file_out = open(file_out_name, 'wb')
    writer.write(file_out)
    file_out.close()
    file_in.close()


def rotate_ranges_in_pdf(file_in_name, file_out_name, degrees, ranges,
                         flip_horizontal=False, flip_vertical=False):
    file_in = open(file_in_name, 'rb')
    pages = tools.get_pages_from_ranges(ranges)
    reader = PyPDF2.PdfFileReader(file_in)
    writer = PyPDF2.PdfFileWriter()
    for i in range(0, reader.getNumPages()):
        page = reader.getPage(i)
        if i+1 in pages:
            page.rotateClockwise(degrees)
            if flip_horizontal is True:
                page.scale(-1, 1)
            if flip_vertical is True:
                page.scale(1, -1)
        writer.addPage(page)
    file_out = open(file_out_name, 'wb')
    writer.write(file_out)
    file_out.close()
    file_in.close()


def split_pdf(file_in_name):
    file_in = open(file_in_name, 'rb')
    reader = PyPDF2.PdfFileReader(file_in)
    for i in range(0, reader.getNumPages()):
        file_out_name, ext = os.path.splitext(file_in_name)
        chn = '%s_%0' + str(len(str(reader.getNumPages()))) + 'd%s'
        file_out_name_i = chn % (file_out_name, i+1, ext)
        file_out_i = open(file_out_name_i, 'wb')
        writer = PyPDF2.PdfFileWriter()
        page = reader.getPage(i)
        writer.addPage(page)
        writer.write(file_out_i)
        file_out_i.close()
    file_in.close()


def combine(file_in_name, file_out_name, filas=1, columnas=2, width=297,
            height=210, margen=0.0, byrows=True):
    file_in = open(file_in_name, 'rb')
    file_out = open(file_out_name, 'wb')
    reader = PyPDF2.PdfFileReader(file_in)
    writer = PyPDF2.PdfFileWriter()
    number_of_pages = reader.getNumPages()
    filas = float(filas)
    columnas = float(columnas)
    width = float(width)
    height = float(height)
    margen = float(margen)
    for i in range(0, number_of_pages, int(filas*columnas)):
        page = i-1
        new_page = PyPDF2.pdf.PageObject.createBlankPage(
            pdf=None, width=width, height=height)
        for fila in range(0, int(filas)):
            for columna in range(0, int(columnas)):
                page += 1
                if byrows:
                    aux_combine(page, reader, fila, columna, width, height,
                                filas, columnas, margen, new_page)
                else:
                    aux_combine(page, reader, columna, fila, width, height,
                                filas, columnas, margen, new_page)
        writer.addPage(new_page)
    writer.write(file_out)
    file_out.close()
    file_in.close()


def aux_combine(page, document, fila, columna, width, height, filas,
                columnas, margen, new_page):
    if page < document.getNumPages():
        current_page = document.getPage(page)
        x0, y0, pdf_width, pdf_height = current_page.artBox
        pdf_width = float(pdf_width)
        pdf_height = float(pdf_height)
        sw = (width-(filas+1.0)*margen)/pdf_width/columnas
        sh = (height-(columnas+1.0)*margen)/pdf_height/filas
        if sw < sh:
            scale = sw
        else:
            scale = sh
        x = float(columna) * width / columnas + (float(columna)+1.0)*margen
        y = ((filas - float(fila) - 1.0) * height / float(filas) +
             (float(fila)+1.0)*margen)
        new_page.mergeScaledTranslatedPage(current_page, scale, x, y)
    else:
        return


def compress(file_in_name, file_out_name):
    file_in = open(file_in_name, 'rb')
    file_out = open(file_out_name, 'wb')
    reader = PyPDF2.PdfFileReader(file_in)
    writer = PyPDF2.PdfFileWriter()
    for i in range(0, reader.getNumPages()):
        page = reader.getPage(i)
        page.compressContentStreams()
        writer.addPage(page)
    writer.write(file_out)
    file_out.close()
    file_in.close()


def rotate_and_flip_pages(file_pdf_in, degrees=ROTATE_090, flip_vertical=False,
                          flip_horizontal=False, overwrite=False):
    temp_pdf = tools.create_temp_file()
    file_in = open(file_pdf_in, 'rb')
    file_out = open(temp_pdf, 'wb')
    reader = PyPDF2.PdfFileReader(file_in)
    writer = PyPDF2.PdfFileWriter()
    for i in range(0, reader.getNumPages()):
        page = reader.getPage(i)
        page.rotateClockwise(degrees)
        if flip_horizontal is True:
            page.scale(-1, 1)
        if flip_vertical is True:
            page.scale(1, -1)
        writer.addPage(page)
    writer.write(file_out)
    file_out.close()
    file_in.close()
    if overwrite:
        shutil.copy(temp_pdf, file_pdf_in)
    else:
        shutil.copy(temp_pdf, tools.get_output_filename(
            file_pdf_in, 'rotated_' + str(int(degrees))))
    os.remove(temp_pdf)


def extract_ranges(file_in_name, file_out_name, ranges):
    pages = tools.get_pages_from_ranges(ranges)
    file_in = open(file_in_name, 'rb')
    file_out = open(file_out_name, 'wb')
    reader = PyPDF2.PdfFileReader(file_in)
    writer = PyPDF2.PdfFileWriter()
    for i in range(0, reader.getNumPages()):
        if i+1 in pages:
            page = reader.getPage(i)
            writer.addPage(page)
    writer.write(file_out)
    file_out.close()
    file_in.close()


def rotate_some_pages_in_pdf(file_in, file_out, degrees, first_page,
                             last_page):
    file_in = open(file_in_name, 'rb')
    file_out = open(file_out_name, 'wb')
    reader = PyPDF2.PdfFileReader(file_in)
    writer = PyPDF2.PdfFileWriter()
    for i in range(0, reader.getNumPages()):
        if i >= first_page and i <= last_page:
            page = reader.getPage(i)
            page.rotateClockwise(degrees)
            writer.addPage(page)
    writer.write(file_out)
    file_out.close()
    file_in.close()


def extract_pages(file_in, file_out, first_page, last_page):
    file_in = open(file_in_name, 'rb')
    file_out = open(file_out_name, 'wb')
    reader = PyPDF2.PdfFileReader(file_in)
    writer = PyPDF2.PdfFileWriter()
    number_of_pages = reader.getNumPages()
    if first_page > number_of_pages-1:
        first_page = number_of_pages-1
    if last_page < first_page:
        last_page = first_page
    if last_page > number_of_pages-1:
        last_page = number_of_pages-1
    for i in range(first_page, last_page+1):
        page = reader.getPage(i)
        writer.addPage(page)
    writer.write(file_out)
    file_out.close()
    file_in.close()


def remove_pages(file_in, file_out, first_page, last_page):
    file_in = open(file_in_name, 'rb')
    file_out = open(file_out_name, 'wb')
    reader = PyPDF2.PdfFileReader(file_in)
    writer = PyPDF2.PdfFileWriter()
    number_of_pages = reader.getNumPages()
    if first_page > number_of_pages-1:
        first_page = number_of_pages-1
    if last_page < first_page:
        last_page = first_page
    if last_page > number_of_pages-1:
        last_page = number_of_pages-1
    for i in range(0, number_of_pages):
        if i not in list(range(first_page, last_page+1)):
            current_page = reader.getPage(i)
            writer.addPage(current_page)
    writer.write(file_out)
    file_out.close()
    file_in.close()


def join_files(files, file_out):
    merger = PyPDF2.PdfFileMerger()
    for afile in files:
        file_in = open(afile, 'rb')
        reader = PyPDF2.PdfFileReader(file_in)
        pages = (0, reader.getNumPages())
        merger.append(file_in,
                      bookmark=afile,
                      pages=pages,
                      import_bookmarks=True)
        file_in.close()
    merger.write(file_out)


def extract_text(file_in, file_out):
    pdf_file = open(file_in, 'rb')
    txt_file = open(file_out, 'w')
    read_pdf = PyPDF2.PdfFileReader(pdf_file)
    number_of_pages = read_pdf.getNumPages()
    for npage in range(0, number_of_pages):
        page = read_pdf.getPage(npage)
        page_content = page.extractText().encode('utf-8')
        txt_file.write(page_content)
    pdf_file.close()
    txt_file.close()

if __name__ == '__main__':
    ranges = []
    range1 = [1, 5]
    range2 = [10, 10]
    ranges.append(range1)
    ranges.append(range2)
    remove_ranges('/home/lorenzo/Escritorio/sample.pdf',
                  '/home/lorenzo/Escritorio/out.pdf',
                  ranges)
    rotate_ranges_in_pdf('/home/lorenzo/Escritorio/sample.pdf',
                         '/home/lorenzo/Escritorio/out2.pdf',
                         90,
                         ranges,
                         True,
                         False)
    resize('/home/lorenzo/Escritorio/sample.pdf',
           '/home/lorenzo/Escritorio/out3.pdf')
    compress('/home/lorenzo/Escritorio/sample.pdf',
             '/home/lorenzo/Escritorio/out4.pdf')
    split_pdf('/home/lorenzo/Escritorio/sample.pdf')
    combine('/home/lorenzo/Escritorio/sample.pdf',
            '/home/lorenzo/Escritorio/out5.pdf')
