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
    gi.require_version('Poppler', '0.18')
except Exception as e:
    print(e)
    exit(1)
from gi.repository import Poppler
import cairo
import os
import math
import shutil
import tools
from comun import ROTATE_000, ROTATE_090, ROTATE_180, ROTATE_270
from comun import TOP, MIDLE, BOTTOM, LEFT, CENTER, RIGHT
from comun import MMTOPIXEL


def get_num_of_pages(file_in):
    document = Poppler.Document.new_from_file('file://' + file_in, None)
    return document.get_n_pages()


def resize(file_in, file_out, width=1189, height=1682):
    document = Poppler.Document.new_from_file('file://' + file_in, None)
    number_of_pages = document.get_n_pages()
    width = float(width)
    height = float(height)
    horizontal = (width > height)
    pdfsurface = cairo.PDFSurface(file_out, width, height)
    context = cairo.Context(pdfsurface)
    for i in range(0, number_of_pages):
        current_page = document.get_page(i)
        widthi, heighti = current_page.get_size()
        horizontali = (widthi > heighti)
        if horizontal != horizontali:
            sw = width / heighti
            sh = height / widthi
            if sw < sh:
                scale = sw
            else:
                scale = sh
            context.save()
            mtr = cairo.Matrix()
            mtr.rotate(ROTATE_270 / 180.0 * math.pi)
            context.transform(mtr)
            context.scale(scale, scale)
            context.translate(-widthi, 0.0)
            current_page.render(context)
            context.restore()
        else:
            sw = width / widthi
            sh = height / heighti
            if sw < sh:
                scale = sw
            else:
                scale = sh
            context.save()
            context.scale(scale, scale)
            current_page.render(context)
            context.restore()
        context.show_page()
    pdfsurface.flush()
    pdfsurface.finish()


def remove_ranges(file_in, file_out, ranges):
    pages = tools.get_pages_from_ranges(ranges)
    document = Poppler.Document.new_from_file('file://' + file_in, None)
    number_of_pages = document.get_n_pages()
    temp_pdf = tools.create_temp_file()
    pdfsurface = cairo.PDFSurface(temp_pdf, 200, 200)
    context = cairo.Context(pdfsurface)
    for i in range(0, number_of_pages):
        if i + 1 not in pages:
            current_page = document.get_page(i)
            context.save()
            pdf_width, pdf_height = current_page.get_size()
            pdfsurface.set_size(pdf_width, pdf_height)
            current_page.render(context)
            context.restore()
            context.show_page()
    pdfsurface.flush()
    pdfsurface.finish()
    shutil.copy(temp_pdf, file_out)
    os.remove(temp_pdf)


def rotate_ranges_in_pdf(file_in, file_out, degrees, ranges,
                         flip_horizontal=False, flip_vertical=False):
    pages = tools.get_pages_from_ranges(ranges)
    document = Poppler.Document.new_from_file('file://' + file_in, None)
    if document.get_n_pages() > 0:
        temp_pdf = tools.create_temp_file()
        pdfsurface = cairo.PDFSurface(temp_pdf, 200, 200)
        context = cairo.Context(pdfsurface)
        for i in range(0, document.get_n_pages()):
            current_page = document.get_page(i)
            if i + 1 in pages:
                if degrees == ROTATE_000 or degrees == ROTATE_180:
                    pdf_width, pdf_height = current_page.get_size()
                else:
                    pdf_height, pdf_width = current_page.get_size()
                pdfsurface.set_size(pdf_width, pdf_height)
                context.save()
                mtr = cairo.Matrix()
                mtr.rotate(degrees / 180.0 * math.pi)
                context.transform(mtr)
                if degrees == ROTATE_090:
                        context.translate(0.0, -pdf_width)
                elif degrees == ROTATE_180:
                        context.translate(-pdf_width, -pdf_height)
                elif degrees == ROTATE_270:
                        context.translate(-pdf_height, 0.0)
                if flip_vertical:
                    context.scale(1, -1)
                    if degrees == ROTATE_000 or degrees == ROTATE_180:
                        context.translate(0, -pdf_height)
                    else:
                        context.translate(0, -pdf_width)
                if flip_horizontal:
                    context.scale(-1, 1)
                    if degrees == ROTATE_000 or degrees == ROTATE_180:
                        context.translate(-pdf_width, 0)
                    else:
                        context.translate(-pdf_height, 0)
                current_page.render(context)
                context.restore()
            else:
                context.save()
                pdf_width, pdf_height = current_page.get_size()
                pdfsurface.set_size(pdf_width, pdf_height)
                current_page.render(context)
                context.restore()
            context.show_page()
        pdfsurface.flush()
        pdfsurface.finish()
        shutil.copy(temp_pdf, file_out)
        os.remove(temp_pdf)


def split_pdf(file_in):
    document = Poppler.Document.new_from_file('file://' + file_in, None)
    number_of_pages = document.get_n_pages()
    if number_of_pages > 1:
        file_out, ext = os.path.splitext(file_in)
        for i in range(0, number_of_pages):
            file_out_i = '%s_%s%s' % (file_out, i + 1, ext)
            pdfsurface = cairo.PDFSurface(file_out_i, 200, 200)
            context = cairo.Context(pdfsurface)
            current_page = document.get_page(i)
            context.save()
            pdf_width, pdf_height = current_page.get_size()
            pdfsurface.set_size(pdf_width, pdf_height)
            current_page.render(context)
            context.restore()
            context.show_page()
            pdfsurface.flush()
            pdfsurface.finish()


def combine(file_in, file_out, filas=1, columnas=2, width=297,
            height=210, margen=0.0, byrows=True):
    document = Poppler.Document.new_from_file('file://' + file_in, None)
    number_of_pages = document.get_n_pages()
    filas = float(filas)
    columnas = float(columnas)
    width = float(width)
    height = float(height)
    margen = float(margen)
    pdfsurface = cairo.PDFSurface(file_out, width, height)
    context = cairo.Context(pdfsurface)
    for i in range(0, number_of_pages, int(filas * columnas)):
        page = i - 1
        for fila in range(0, int(filas)):
            for columna in range(0, int(columnas)):
                page += 1
                if byrows:
                    aux_combine(page, document, fila, columna, width, height,
                                filas, columnas, margen, context)
                else:
                    aux_combine(page, document, columna, fila, width, height,
                                filas, columnas, margen, context)
        context.show_page()
    pdfsurface.flush()
    pdfsurface.finish()


def aux_combine(page, document, fila, columna, width, height, filas,
                columnas, margen, context):
    if page < document.get_n_pages():
        current_page = document.get_page(page)
        pdf_width, pdf_height = current_page.get_size()
        sw = (width - (filas + 1.0) * margen) / pdf_width / columnas
        sh = (height - (columnas + 1.0) * margen) / pdf_height / filas
        if sw < sh:
            scale = sw
        else:
            scale = sh
        x = float(columna) * width / columnas + (float(columna) + 1.0) * margen
        y = ((filas - float(fila) - 1.0) * height / float(filas) +
             (float(fila) + 1.0) * margen)
        context.save()
        context.translate(x, y)
        context.scale(scale, scale)
        current_page.render(context)
        context.restore()
    else:
        return


def rotate_and_flip_pages(file_pdf_in, degrees=ROTATE_090, flip_vertical=False,
                          flip_horizontal=False, overwrite=False):
    document = Poppler.Document.new_from_file('file://' + file_pdf_in, None)
    if document.get_n_pages() > 0:
        temp_pdf = tools.create_temp_file()
        pdfsurface = cairo.PDFSurface(temp_pdf, 200, 200)
        context = cairo.Context(pdfsurface)
        for i in range(0, document.get_n_pages()):
            current_page = document.get_page(i)
            if degrees == ROTATE_000 or degrees == ROTATE_180:
                pdf_width, pdf_height = current_page.get_size()
            else:
                pdf_height, pdf_width = current_page.get_size()
            pdfsurface.set_size(pdf_width, pdf_height)
            context.save()
            if flip_vertical:
                context.scale(1, -1)
                if degrees == ROTATE_000 or degrees == ROTATE_180:
                    context.translate(0, -pdf_width)
                else:
                    context.translate(0, -pdf_height)
            if flip_horizontal:
                context.scale(-1, 1)
                if degrees == ROTATE_000 or degrees == ROTATE_180:
                    context.translate(-pdf_height, 0)
                else:
                    context.translate(-pdf_width, 0)
            mtr = cairo.Matrix()
            mtr.rotate(degrees / 180.0 * math.pi)
            context.transform(mtr)
            if degrees == ROTATE_090:
                    context.translate(0.0, -pdf_width)
            elif degrees == ROTATE_180:
                    context.translate(-pdf_width, -pdf_height)
            elif degrees == ROTATE_270:
                    context.translate(-pdf_height, 0.0)
            current_page.render(context)
            context.restore()
            context.show_page()
        pdfsurface.flush()
        pdfsurface.finish()
        if overwrite:
            shutil.copy(temp_pdf, file_pdf_in)
        else:
            shutil.copy(temp_pdf, tools.get_output_filename(
                file_pdf_in, 'rotated_' + str(int(degrees))))
        os.remove(temp_pdf)


def extract_ranges(file_in, file_out, ranges):
    pages = tools.get_pages_from_ranges(ranges)
    document = Poppler.Document.new_from_file('file://' + file_in, None)
    number_of_pages = document.get_n_pages()
    temp_pdf = tools.create_temp_file()
    pdfsurface = cairo.PDFSurface(temp_pdf, 200, 200)
    context = cairo.Context(pdfsurface)
    for i in range(0, number_of_pages):
        if i + 1 in pages:
            current_page = document.get_page(i)
            context.save()
            pdf_width, pdf_height = current_page.get_size()
            pdfsurface.set_size(pdf_width, pdf_height)
            current_page.render(context)
            context.restore()
            context.show_page()
    pdfsurface.flush()
    pdfsurface.finish()
    shutil.copy(temp_pdf, file_out)
    os.remove(temp_pdf)


def rotate_some_pages_in_pdf(file_in, file_out, degrees, first_page, last_page,
                             flip_vertical=False, flip_horizontal=False):
    document = Poppler.Document.new_from_file('file://' + file_in, None)
    if document.get_n_pages() > 0:
        temp_pdf = tools.create_temp_file()
        pdfsurface = cairo.PDFSurface(temp_pdf, 200, 200)
        context = cairo.Context(pdfsurface)
        for i in range(0, document.get_n_pages()):
            current_page = document.get_page(i)
            if i >= first_page and i <= last_page:
                if degrees == ROTATE_000 or degrees == ROTATE_180:
                    pdf_width, pdf_height = current_page.get_size()
                else:
                    pdf_height, pdf_width = current_page.get_size()
                pdfsurface.set_size(pdf_width, pdf_height)
                context.save()
                mtr = cairo.Matrix()
                mtr.rotate(degrees / 180.0 * math.pi)
                context.transform(mtr)
                if degrees == ROTATE_090:
                        context.translate(0.0, -pdf_width)
                elif degrees == ROTATE_180:
                        context.translate(-pdf_width, -pdf_height)
                elif degrees == ROTATE_270:
                        context.translate(-pdf_height, 0.0)
                if flip_vertical:
                    context.scale(1, -1)
                    if degrees == ROTATE_000 or degrees == ROTATE_180:
                        context.translate(0, -pdf_height)
                    else:
                        context.translate(0, -pdf_width)
                if flip_horizontal:
                    context.scale(-1, 1)
                    if degrees == ROTATE_000 or degrees == ROTATE_180:
                        context.translate(-pdf_width, 0)
                    else:
                        context.translate(-pdf_height, 0)
                current_page.render(context)
                context.restore()
            else:
                context.save()
                pdf_width, pdf_height = current_page.get_size()
                pdfsurface.set_size(pdf_width, pdf_height)
                current_page.render(context)
                context.restore()
            context.show_page()
        pdfsurface.flush()
        pdfsurface.finish()
        shutil.copy(temp_pdf, file_out)
        os.remove(temp_pdf)


def extract_pages(file_in, file_out, first_page, last_page):
    document = Poppler.Document.new_from_file('file://' + file_in, None)
    number_of_pages = document.get_n_pages()
    if first_page > number_of_pages - 1:
        first_page = number_of_pages - 1
    if last_page < first_page:
        last_page = first_page
    if last_page > number_of_pages - 1:
        last_page = number_of_pages - 1
    temp_pdf = tools.create_temp_file()
    pdfsurface = cairo.PDFSurface(temp_pdf, 200, 200)
    context = cairo.Context(pdfsurface)
    for i in range(first_page, last_page + 1):
        current_page = document.get_page(i)
        context.save()
        pdf_width, pdf_height = current_page.get_size()
        pdfsurface.set_size(pdf_width, pdf_height)
        current_page.render(context)
        context.restore()
        context.show_page()
    pdfsurface.flush()
    pdfsurface.finish()
    shutil.copy(temp_pdf, file_out)
    os.remove(temp_pdf)


def remove_pages(file_in, file_out, first_page, last_page):
    document = Poppler.Document.new_from_file('file://' + file_in, None)
    number_of_pages = document.get_n_pages()
    if first_page > number_of_pages - 1:
        first_page = number_of_pages - 1
    if last_page < first_page:
        last_page = first_page
    if last_page > number_of_pages - 1:
        last_page = number_of_pages - 1
    temp_pdf = tools.create_temp_file()
    pdfsurface = cairo.PDFSurface(temp_pdf, 200, 200)
    context = cairo.Context(pdfsurface)
    for i in range(0, number_of_pages):
        if i not in list(range(first_page, last_page + 1)):
            current_page = document.get_page(i)
            context.save()
            pdf_width, pdf_height = current_page.get_size()
            pdfsurface.set_size(pdf_width, pdf_height)
            current_page.render(context)
            context.restore()
            context.show_page()
    pdfsurface.flush()
    pdfsurface.finish()
    shutil.copy(temp_pdf, file_out)
    os.remove(temp_pdf)


def join_files(files, file_out):
    temp_pdf = tools.create_temp_file()
    pdfsurface = cairo.PDFSurface(temp_pdf, 200, 200)
    context = cairo.Context(pdfsurface)
    for file_in in files:
        document = Poppler.Document.new_from_file('file://' + file_in, None)
        number_of_pages = document.get_n_pages()
        for i in range(0, number_of_pages):
            current_page = document.get_page(i)
            context.save()
            pdf_width, pdf_height = current_page.get_size()
            pdfsurface.set_size(pdf_width, pdf_height)
            current_page.render(context)
            context.restore()
            context.show_page()
    pdfsurface.flush()
    pdfsurface.finish()
    shutil.copy(temp_pdf, file_out)
    os.remove(temp_pdf)


def add_paginate_all_pages(file_pdf_in, color, font, size, horizontal_position,
                           vertical_position, horizontal_margin,
                           vertical_margin, overwrite=False):
    document = Poppler.Document.new_from_file('file://' + file_pdf_in, None)
    number_of_pages = document.get_n_pages()
    if document.get_n_pages() > 0:
        temp_pdf = tools.create_temp_file()
        pdfsurface = cairo.PDFSurface(temp_pdf, 200, 200)
        context = cairo.Context(pdfsurface)
        for i in range(0, number_of_pages):
            current_page = document.get_page(i)
            text = '%s/%s' % (i + 1, number_of_pages)
            pdf_width, pdf_height = current_page.get_size()
            pdfsurface.set_size(pdf_width, pdf_height)
            context.save()
            current_page.render(context)
            context.restore()
            context.save()
            context.set_source_rgba(*color)
            context.select_font_face(font)
            context.set_font_size(size)
            xbearing, ybearing, font_width, font_height, xadvance, yadvance =\
                context.text_extents(text)
            if vertical_position == TOP:
                y = font_height + vertical_margin
            elif vertical_position == MIDLE:
                y = (pdf_height + font_height) / 2
            elif vertical_position == BOTTOM:
                y = pdf_height - vertical_margin
            if horizontal_position == LEFT:
                x = horizontal_margin
            elif horizontal_position == CENTER:
                x = (pdf_width - font_width) / 2
            elif horizontal_position == RIGHT:
                x = pdf_width - font_width + xbearing - horizontal_margin
            context.move_to(x, y)
            context.translate(x, y)
            context.show_text(text)
            context.restore()
            context.show_page()
        pdfsurface.flush()
        pdfsurface.finish()
        if overwrite:
            shutil.copy(temp_pdf, file_pdf_in)
        else:
            shutil.copy(temp_pdf, tools.get_output_filename(
                file_pdf_in, 'paginated'))
        os.remove(temp_pdf)


def add_textmark_to_all_pages(file_pdf_in, text, color, font, size,
                              horizontal_position, vertical_position,
                              horizontal_margin, vertical_margin,
                              overwrite=False):
    document = Poppler.Document.new_from_file('file://' + file_pdf_in, None)
    if document.get_n_pages() > 0:
        temp_pdf = tools.create_temp_file()
        pdfsurface = cairo.PDFSurface(temp_pdf, 200, 200)
        context = cairo.Context(pdfsurface)
        for i in range(0, document.get_n_pages()):
            current_page = document.get_page(i)
            pdf_width, pdf_height = current_page.get_size()
            pdfsurface.set_size(pdf_width, pdf_height)
            context.save()
            current_page.render(context)
            context.restore()
            context.save()
            context.set_source_rgba(*color)
            context.select_font_face(font)
            context.set_font_size(size)
            xbearing, ybearing, font_width, font_height, xadvance, yadvance =\
                context.text_extents(text)
            if vertical_position == TOP:
                y = font_height + vertical_margin
            elif vertical_position == MIDLE:
                y = (pdf_height + font_height) / 2
            elif vertical_position == BOTTOM:
                y = pdf_height - vertical_margin
            if horizontal_position == LEFT:
                x = horizontal_margin
            elif horizontal_position == CENTER:
                x = (pdf_width - font_width) / 2
            elif horizontal_position == RIGHT:
                x = pdf_width - font_width + xbearing - horizontal_margin
            context.move_to(x, y)
            context.translate(x, y)
            context.show_text(text)
            context.restore()
            context.show_page()
        pdfsurface.flush()
        pdfsurface.finish()
        if overwrite:
            shutil.copy(temp_pdf, file_pdf_in)
        else:
            shutil.copy(temp_pdf, tools.get_output_filename(
                file_pdf_in, 'textmarked'))
        os.remove(temp_pdf)


def add_watermark_to_all_pages(file_pdf_in, file_image_in, horizontal_position,
                               vertical_position, horizontal_margin,
                               vertical_margin, zoom, overwrite=False):
    document = Poppler.Document.new_from_file('file://' + file_pdf_in, None)
    if document.get_n_pages() > 0:
        temp_pdf = tools.create_temp_file()
        watermark_surface = tools.create_image_surface_from_file(
            file_image_in, zoom)
        watermark_width = watermark_surface.get_width()
        watermark_height = watermark_surface.get_height()
        pdfsurface = cairo.PDFSurface(temp_pdf, 200, 200)
        context = cairo.Context(pdfsurface)
        for i in range(0, document.get_n_pages()):
            current_page = document.get_page(i)
            pdf_width, pdf_height = current_page.get_size()
            pdfsurface.set_size(pdf_width, pdf_height)
            context.save()
            current_page.render(context)
            context.restore()
            context.save()
            if vertical_position == TOP:
                y = vertical_margin
            elif vertical_position == MIDLE:
                y = (pdf_height - watermark_height / MMTOPIXEL) / 2
            elif vertical_position == BOTTOM:
                y = pdf_height - watermark_height / MMTOPIXEL - vertical_margin
            if horizontal_position == LEFT:
                x = horizontal_margin
            elif horizontal_position == CENTER:
                x = (pdf_width - watermark_width / MMTOPIXEL) / 2
            elif horizontal_position == RIGHT:
                x = pdf_width - watermark_width / MMTOPIXEL - horizontal_margin
            context.translate(x, y)
            context.scale(1.0 / MMTOPIXEL, 1.0 / MMTOPIXEL)
            context.set_source_surface(watermark_surface)
            context.paint()
            context.restore()
            context.show_page()
        pdfsurface.flush()
        pdfsurface.finish()
        if overwrite:
            shutil.copy(temp_pdf, file_pdf_in)
        else:
            shutil.copy(temp_pdf, tools.get_output_filename(
                file_pdf_in, 'watermarked'))
        os.remove(temp_pdf)


if __name__ == '__main__':
    ranges = []
    range1 = [1, 5]
    range2 = [10, 10]
    ranges.append(range1)
    ranges.append(range2)
    resize('/home/lorenzo/Escritorio/sample.pdf',
           '/home/lorenzo/Escritorio/out3.pdf')
    remove_ranges('/home/lorenzo/Escritorio/sample.pdf',
                  '/home/lorenzo/Escritorio/out.pdf',
                  ranges)
    rotate_ranges_in_pdf('/home/lorenzo/Escritorio/sample.pdf',
                         '/home/lorenzo/Escritorio/out2.pdf',
                         90,
                         ranges,
                         True,
                         False)
    split_pdf('/home/lorenzo/Escritorio/sample.pdf')
    combine('/home/lorenzo/Escritorio/sample.pdf',
            '/home/lorenzo/Escritorio/out5.pdf')
