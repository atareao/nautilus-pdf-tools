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
    gi.require_version('GObject', '2.0')
    gi.require_version('GLib', '2.0')
    gi.require_version('Poppler', '0.18')
except Exception as e:
    print(e)
    exit(1)
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Poppler
from threading import Thread
import tools
import cairo
import math
import os
import shutil
import mimetypes
from comun import MMTOPNG, MMTOPIXEL, MMTOPDF
from comun import MIMETYPES_PNG, RESOLUTION
from comun import TOP, MIDLE, BOTTOM, LEFT, CENTER, RIGHT
from comun import ROTATE_000, ROTATE_090, ROTATE_180, ROTATE_270
import cairoapi

mimetypes.init()


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


class DoitInBackgroundBase(GObject.GObject, Thread):
    __gsignals__ = {
        'start': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (int,)),
        'todo': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (str,)),
        'done': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (str,)),
        'donef': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (float,)),
        'interrupted': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
        'finished': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
    }

    def __init__(self):
        GObject.GObject.__init__(self)
        Thread.__init__(self)
        self.daemon = True
        self.stop = False

    def emit(self, *args):
        GLib.idle_add(GObject.GObject.emit, self, *args)

    def stop_it(self, executor):
        self.stop = True


class DoitInBackground(DoitInBackgroundBase):

    def __init__(self, maker, elements):
        DoitInBackgroundBase.__init__(self)
        Thread.__init__(self)
        self.maker = maker
        self.elements = elements

    def run(self):
        print(2)
        if self.elements:
            self.stop = False
            for an_element in self.elements:
                self.emit('todo', str(an_element))
                print(an_element)
                self.maker(an_element)
                self.emit('done', str(an_element))
                if self.stop is True:
                    self.emit('interrupted')
                    break
        self.emit('finished')


class DoItInBackgroundResizePages(DoitInBackgroundBase):
    def __init__(self, files_in, extension, width, height):
        DoitInBackgroundBase.__init__(self)
        self.files_in = files_in
        self.extension = extension
        self.width = width
        self.height = height

    def run(self):
        total_documents = len(self.files_in)
        self.emit('start', total_documents)
        for index, file_in in enumerate(self.files_in):
            self.emit('todo', file_in)
            document = Poppler.Document.new_from_file('file://' + file_in,
                                                      None)
            number_of_pages = document.get_n_pages()
            width = float(self.width)
            height = float(self.height)
            horizontal = (width > height)
            filename, filext = os.path.splitext(file_in)
            file_out = filename + self.extension + filext
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
                if self.stop is True:
                    break
                self.emit('donef', (float(index) + float(i) / float(
                    number_of_pages)) / float(total_documents))
            if self.stop is True:
                break
            pdfsurface.flush()
            pdfsurface.finish()
        if self.stop is True:
            self.emit('interrupted')
        else:
            self.emit('finished')


class DoItInBackgroundToPNG(DoitInBackgroundBase):
    def __init__(self, files):
        DoitInBackgroundBase.__init__(self)
        self.files = files

    def run(self):
        total_documents = len(self.files)
        self.emit('start', total_documents)
        for index, file_in in enumerate(self.files):
            self.emit('todo', file_in)
            document = Poppler.Document.new_from_file('file://' + file_in,
                                                      None)
            number_of_pages = document.get_n_pages()
            if number_of_pages > 0:
                file_out, ext = os.path.splitext(file_in)
                zeros = len(str(number_of_pages))
                for i in range(0, number_of_pages):
                    current_page = document.get_page(i)
                    pdf_width, pdf_height = current_page.get_size()
                    file_out_i = '%s_%s%s' % (file_out,
                                              str(i + 1).zfill(zeros),
                                              '.png')
                    self.emit('todo', file_out_i)
                    pngsurface = cairo.ImageSurface(
                        cairo.FORMAT_ARGB32,
                        int(pdf_width * MMTOPNG),
                        int(pdf_height * MMTOPNG))
                    context = cairo.Context(pngsurface)
                    context.save()
                    context.scale(1.0 * MMTOPNG, 1.0 * MMTOPNG)
                    current_page.render(context)
                    context.restore()
                    pngsurface.flush()
                    pngsurface.write_to_png(file_out_i)
                    pngsurface.finish()
                    if self.stop is True:
                        break
                    self.emit('donef', (float(index) + float(i) / float(
                        number_of_pages)) / float(total_documents))
            if self.stop is True:
                break
        if self.stop is True:
            self.emit('interrupted')
        else:
            self.emit('finished')


class DoItInBackgroundCombine(DoitInBackgroundBase):
    def __init__(self, files, extension, filas, columnas, width, height,
                 margen, byrows):
        DoitInBackgroundBase.__init__(self)
        self.files = files
        self.extension = extension
        self.filas = filas
        self.columnas = columnas
        self.width = width
        self.height = height
        self.margen = margen
        self.byrows = byrows

    def run(self):
        total_documents = len(self.files)
        self.emit('start', total_documents)
        for index, file_in in enumerate(self.files):
            self.emit('todo', file_in)
            document = Poppler.Document.new_from_file('file://' + file_in,
                                                      None)
            number_of_pages = document.get_n_pages()
            filas = float(self.filas)
            columnas = float(self.columnas)
            width = float(self.width)
            height = float(self.height)
            margen = float(self.margen)

            filename, filext = os.path.splitext(file_in)
            file_out = filename + self.extension + filext
            pdfsurface = cairo.PDFSurface(file_out, width, height)
            context = cairo.Context(pdfsurface)
            for i in range(0, number_of_pages, int(filas * columnas)):
                page = i - 1
                for fila in range(0, int(filas)):
                    for columna in range(0, int(columnas)):
                        page += 1
                        if self.byrows:
                            aux_combine(page, document, fila, columna, width,
                                        height, filas, columnas, margen,
                                        context)
                        else:
                            aux_combine(page, document, columna, fila, width,
                                        height, filas, columnas, margen,
                                        context)
                        if self.stop is True:
                            break
                    if self.stop is True:
                        break
                context.show_page()
                if self.stop is True:
                    break
                self.emit('donef', (float(index) + float(i) / float(
                    number_of_pages)) / float(total_documents))
            pdfsurface.flush()
            pdfsurface.finish()
            if self.stop is True:
                break
        if self.stop is True:
            self.emit('interrupted')
        else:
            self.emit('finished')


class DoItInBackgroundCreatePDFFromImages(DoitInBackgroundBase):
    def __init__(self, file_out, files, width, height, margin):
        DoitInBackgroundBase.__init__(self)
        self.file_out = file_out
        self.files = files
        self.width = width
        self.height = height
        self.margin = margin

    def run(self):
        temp_pdf = tools.create_temp_file()
        pdfsurface = cairo.PDFSurface(temp_pdf, self.width, self.height)
        context = cairo.Context(pdfsurface)
        self.emit('start', self.files)
        for image in self.files:
            self.emit('todo', image)
            basename, extension = os.path.splitext(image)
            if mimetypes.guess_type(image)[0] in MIMETYPES_PNG:
                imagesurface = cairo.ImageSurface.create_from_png(image)
            else:
                imagesurface = tools.create_image_surface_from_file(image)
            imagesurface_width = imagesurface.get_width()
            imagesurface_height = imagesurface.get_height()
            scale_x = (imagesurface_width / MMTOPIXEL) / self.width
            scale_y = (imagesurface_height / MMTOPIXEL) / self.height
            if scale_x > scale_y:
                scale = scale_x
            else:
                scale = scale_y
            if self.margin == 1:
                scale = scale * 1.05
            elif self.margin == 2:
                scale = scale * 1.15
            x = (self.width - imagesurface_width / MMTOPIXEL / scale) / 2
            y = (self.height - imagesurface_height / MMTOPIXEL / scale) / 2
            context.save()
            context.translate(x, y)
            context.scale(1.0 / MMTOPIXEL / scale, 1.0 / MMTOPIXEL / scale)
            context.set_source_surface(imagesurface)
            context.paint()
            context.restore()
            context.show_page()
            self.emit('done', image)
            if self.stop is True:
                break
        pdfsurface.flush()
        pdfsurface.finish()
        shutil.copy(temp_pdf, self.file_out)
        os.remove(temp_pdf)
        if self.stop is True:
            self.emit('interrupted')
        else:
            self.emit('finished')


class DoItInBackgroundJoinPdf(DoitInBackgroundBase):

    def __init__(self, pdfs_in, pdf_out):
        DoitInBackgroundBase.__init__(self)
        self.pdfs_in = pdfs_in
        self.pdf_out = pdf_out

    def run(self):
        total_documents = len(self.pdfs_in)
        temp_pdf = tools.create_temp_file()
        pdfsurface = cairo.PDFSurface(temp_pdf, 200, 200)
        context = cairo.Context(pdfsurface)
        for index, file_in in enumerate(self.pdfs_in):
            self.emit('todo', file_in)
            document = Poppler.Document.new_from_file('file://' + file_in,
                                                      None)
            number_of_pages = document.get_n_pages()
            for i in range(0, number_of_pages):
                current_page = document.get_page(i)
                context.save()
                pdf_width, pdf_height = current_page.get_size()
                pdfsurface.set_size(pdf_width, pdf_height)
                current_page.render(context)
                context.restore()
                context.show_page()
                self.emit('donef', (float(index) + float(i) / float(
                    number_of_pages)) / float(total_documents))
                if self.stop is True:
                        break
            if self.stop is True:
                    break
        pdfsurface.flush()
        pdfsurface.finish()
        if os.path.exists(self.pdf_out):
            os.remove(self.pdf_out)
        shutil.copy(temp_pdf, self.pdf_out)
        os.remove(temp_pdf)
        if self.stop is True:
            self.emit('interrupted')
        else:
            self.emit('finished')


class DoitInBackgroundPaginage(DoitInBackgroundBase):
    def __init__(self, files, color, font, size, hoption, voption,
                 horizontal_margin, vertical_margin, extension):
        DoitInBackgroundBase.__init__(self)
        self.files = files
        self.color = color
        self.font = font
        self.size = size
        self.horizontal_position = hoption
        self.vertical_position = voption
        self.horizontal_margin = horizontal_margin
        self.vertical_margin = vertical_margin
        self.extension = extension

    def run(self):
        total_documents = len(self.files)
        for index, file_in in enumerate(self.files):
            self.emit('todo', file_in)
            document = Poppler.Document.new_from_file('file://' + file_in,
                                                      None)
            number_of_pages = document.get_n_pages()
            if document.get_n_pages() > 0:
                temp_pdf = tools.create_temp_file()
                filename, filext = os.path.splitext(file_in)
                file_out = filename + self.extension + filext
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
                    context.set_source_rgba(*self.color)
                    context.select_font_face(self.font)
                    context.set_font_size(self.size)
                    xbearing, ybearing, font_width, font_height,\
                        xadvance, yadvance = context.text_extents(text)
                    if self.vertical_position == TOP:
                        y = font_height + self.vertical_margin
                    elif self.vertical_position == MIDLE:
                        y = (pdf_height + font_height) / 2
                    elif self.vertical_position == BOTTOM:
                        y = pdf_height - self.vertical_margin
                    if self.horizontal_position == LEFT:
                        x = self.horizontal_margin
                    elif self.horizontal_position == CENTER:
                        x = (pdf_width - font_width) / 2
                    elif self.horizontal_position == RIGHT:
                        x = pdf_width - font_width + xbearing\
                            - self.horizontal_margin
                    context.move_to(x, y)
                    context.translate(x, y)
                    context.show_text(text)
                    context.restore()
                    context.show_page()
                    self.emit('donef', (float(index) + float(i) / float(
                        number_of_pages)) / float(total_documents))
                    if self.stop is True:
                            break
                pdfsurface.flush()
                pdfsurface.finish()
                shutil.copy(temp_pdf, file_out)
                os.remove(temp_pdf)
            if self.stop is True:
                    break
        if self.stop is True:
            self.emit('interrupted')
        else:
            self.emit('finished')


class DoitInBackgroundTextMark(DoitInBackgroundBase):
    def __init__(self, files, text, color, font, size, hoption, voption,
                 horizontal_margin, vertical_margin, extension):
        DoitInBackgroundBase.__init__(self)
        self.files = files
        self.text = text
        self.color = color
        self.font = font
        self.size = size
        self.horizontal_position = hoption
        self.vertical_position = voption
        self.horizontal_margin = horizontal_margin
        self.vertical_margin = vertical_margin
        self.extension = extension

    def run(self):
        total_documents = len(self.files)
        for index, file_in in enumerate(self.files):
            self.emit('todo', file_in)
            document = Poppler.Document.new_from_file('file://' + file_in,
                                                      None)
            number_of_pages = document.get_n_pages()
            if document.get_n_pages() > 0:
                temp_pdf = tools.create_temp_file()
                filename, filext = os.path.splitext(file_in)
                file_out = filename + self.extension + filext
                pdfsurface = cairo.PDFSurface(temp_pdf, 200, 200)
                context = cairo.Context(pdfsurface)
                for i in range(0, number_of_pages):
                    current_page = document.get_page(i)
                    pdf_width, pdf_height = current_page.get_size()
                    pdfsurface.set_size(pdf_width, pdf_height)
                    context.save()
                    current_page.render(context)
                    context.restore()
                    context.save()
                    context.set_source_rgba(*self.color)
                    context.select_font_face(self.font)
                    context.set_font_size(self.size)
                    xbearing, ybearing, font_width, font_height,\
                        xadvance, yadvance = context.text_extents(self.text)
                    if self.vertical_position == TOP:
                        y = font_height + self.vertical_margin
                    elif self.vertical_position == MIDLE:
                        y = (pdf_height + font_height) / 2
                    elif self.vertical_position == BOTTOM:
                        y = pdf_height - self.vertical_margin
                    if self.horizontal_position == LEFT:
                        x = self.horizontal_margin
                    elif self.horizontal_position == CENTER:
                        x = (pdf_width - font_width) / 2
                    elif self.horizontal_position == RIGHT:
                        x = pdf_width - font_width + xbearing\
                            - self.horizontal_margin
                    context.move_to(x, y)
                    context.translate(x, y)
                    context.show_text(self.text)
                    context.restore()
                    context.show_page()
                    self.emit('donef', (float(index) + float(i) / float(
                        number_of_pages)) / float(total_documents))
                    if self.stop is True:
                            break
                pdfsurface.flush()
                pdfsurface.finish()
                shutil.copy(temp_pdf, file_out)
                os.remove(temp_pdf)
            if self.stop is True:
                    break
        if self.stop is True:
            self.emit('interrupted')
        else:
            self.emit('finished')


class DoitInBackgroundEncrypt(DoitInBackgroundBase):
    def __init__(self, files, password):
        DoitInBackgroundBase.__init__(self)
        self.files = files
        self.password = password

    def run(self):
        self.emit('start', len(self.files))
        for file_in in self.files:
            self.emit('todo', file_in)
            cairoapi.encrypt(file_in, self.password)
            self.emit('done', file_in)
            if self.stop is True:
                break
        if self.stop is True:
            self.emit('interrupted')
        else:
            self.emit('finished')


class DoitInBackgroundDecrypt(DoitInBackgroundBase):
    def __init__(self, files, password):
        DoitInBackgroundBase.__init__(self)
        self.files = files
        self.password = password

    def run(self):
        self.emit('start', len(self.files))
        for file_in in self.files:
            self.emit('todo', file_in)
            cairoapi.decrypt(file_in, self.password)
            self.emit('done', file_in)
            if self.stop is True:
                break
        if self.stop is True:
            self.emit('interrupted')
        else:
            self.emit('finished')


class DoitInBackgroundSign(DoitInBackgroundBase):
    def __init__(self, files, image, x, y, zoom, extension):
        DoitInBackgroundBase.__init__(self)
        self.files = files
        self.image = image
        self.x = x
        self.y = y
        self.zoom = float(zoom / 100.0)
        self.extension = extension

    def run(self):
        total_documents = len(self.files)
        for index, file_in in enumerate(self.files):
            self.emit('todo', file_in)
            document = Poppler.Document.new_from_file('file://' + file_in,
                                                      None)
            number_of_pages = document.get_n_pages()
            if number_of_pages > 0:
                temp_pdf = tools.create_temp_file()
                filename, filext = os.path.splitext(file_in)
                file_out = filename + self.extension + filext
                watermark_surface = tools.create_image_surface_from_file(
                    self.image, self.zoom)
                watermark_width = watermark_surface.get_width()
                watermark_height = watermark_surface.get_height()
                pdfsurface = cairo.PDFSurface(temp_pdf, 200, 200)
                context = cairo.Context(pdfsurface)
                for i in range(0, number_of_pages):
                    current_page = document.get_page(i)
                    pdf_width, pdf_height = current_page.get_size()
                    pdfsurface.set_size(pdf_width, pdf_height)
                    print('*-*-', self.x, self.y, self.zoom)
                    print('-*-*', pdf_width, pdf_height)

                    context.save()
                    current_page.render(context)
                    context.restore()
                    context.save()
                    context.translate(self.x * 0.50,
                                      self.y * 0.55)
                    context.scale(1 / RESOLUTION / MMTOPIXEL,
                                  1 / RESOLUTION / MMTOPIXEL)
                    context.set_source_surface(watermark_surface)
                    context.paint()
                    context.restore()
                    context.show_page()
                    self.emit('donef', (float(index) + float(i) / float(
                        number_of_pages)) / float(total_documents))
                    if self.stop is True:
                            break
                pdfsurface.flush()
                pdfsurface.finish()
                shutil.copy(temp_pdf, file_out)
                os.remove(temp_pdf)
            if self.stop is True:
                    break
        if self.stop is True:
            self.emit('interrupted')
        else:
            self.emit('finished')


class DoitInBackgroundWaterMark(DoitInBackgroundBase):
    def __init__(self, files, image, hoption, voption, horizontal_margin,
                 vertical_margin, zoom, extension):
        DoitInBackgroundBase.__init__(self)
        self.files = files
        self.image = image
        self.horizontal_position = hoption
        self.vertical_position = voption
        self.horizontal_margin = horizontal_margin
        self.vertical_margin = vertical_margin
        self.zoom = zoom
        self.extension = extension

    def run(self):
        total_documents = len(self.files)
        for index, file_in in enumerate(self.files):
            self.emit('todo', file_in)
            document = Poppler.Document.new_from_file('file://' + file_in,
                                                      None)
            number_of_pages = document.get_n_pages()
            if number_of_pages > 0:
                temp_pdf = tools.create_temp_file()
                filename, filext = os.path.splitext(file_in)
                file_out = filename + self.extension + filext
                watermark_surface = tools.create_image_surface_from_file(
                    self.image, self.zoom)
                watermark_width = watermark_surface.get_width()
                watermark_height = watermark_surface.get_height()
                pdfsurface = cairo.PDFSurface(temp_pdf, 200, 200)
                context = cairo.Context(pdfsurface)
                for i in range(0, number_of_pages):
                    current_page = document.get_page(i)
                    pdf_width, pdf_height = current_page.get_size()
                    pdfsurface.set_size(pdf_width, pdf_height)
                    context.save()
                    current_page.render(context)
                    context.restore()
                    context.save()
                    if self.vertical_position == TOP:
                        y = self.vertical_margin
                    elif self.vertical_position == MIDLE:
                        y = (pdf_height - watermark_height / MMTOPIXEL) / 2
                    elif self.vertical_position == BOTTOM:
                        y = pdf_height - watermark_height / MMTOPIXEL\
                            - self.vertical_margin
                    if self.horizontal_position == LEFT:
                        x = self.horizontal_margin
                    elif self.horizontal_position == CENTER:
                        x = (pdf_width - watermark_width / MMTOPIXEL) / 2
                    elif self.horizontal_position == RIGHT:
                        x = pdf_width - watermark_width / MMTOPIXEL\
                            - self.horizontal_margin
                    context.translate(x, y)
                    context.scale(1.0 / MMTOPIXEL, 1.0 / MMTOPIXEL)
                    context.set_source_surface(watermark_surface)
                    context.paint()
                    context.restore()
                    context.show_page()
                    self.emit('donef', (float(index) + float(i) / float(
                        number_of_pages)) / float(total_documents))
                    if self.stop is True:
                            break
                pdfsurface.flush()
                pdfsurface.finish()
                shutil.copy(temp_pdf, file_out)
                os.remove(temp_pdf)
            if self.stop is True:
                    break
        if self.stop is True:
            self.emit('interrupted')
        else:
            self.emit('finished')


class DoitInBackgroundRotateAndFlip(DoitInBackgroundBase):
    def __init__(self, files, rotate, flip_vertical, flip_horizontal,
                 extension):
        DoitInBackgroundBase.__init__(self)
        self.files = files
        self.rotate = rotate
        self.flip_vertical = flip_vertical
        self.flip_horizontal = flip_horizontal
        self.extension = extension

    def run(self):
        total_documents = len(self.files)
        for index, file_in in enumerate(self.files):
            self.emit('todo', file_in)
            document = Poppler.Document.new_from_file('file://' + file_in,
                                                      None)
            number_of_pages = document.get_n_pages()
            if number_of_pages > 0:
                temp_pdf = tools.create_temp_file()
                filename, filext = os.path.splitext(file_in)
                file_out = filename + self.extension + filext
                pdfsurface = cairo.PDFSurface(temp_pdf, 200, 200)
                context = cairo.Context(pdfsurface)
                for i in range(0, document.get_n_pages()):
                    current_page = document.get_page(i)
                    if self.rotate == ROTATE_000 or self.rotate == ROTATE_180:
                        pdf_width, pdf_height = current_page.get_size()
                    else:
                        pdf_height, pdf_width = current_page.get_size()
                    pdfsurface.set_size(pdf_width, pdf_height)
                    context.save()
                    if self.flip_vertical:
                        context.scale(1, -1)
                        if self.rotate == ROTATE_000 or\
                                self.rotate == ROTATE_180:
                            context.translate(0, -pdf_width)
                        else:
                            context.translate(0, -pdf_height)
                    if self.flip_horizontal:
                        context.scale(-1, 1)
                        if self.rotate == ROTATE_000 or\
                                self.rotate == ROTATE_180:
                            context.translate(-pdf_height, 0)
                        else:
                            context.translate(-pdf_width, 0)
                    mtr = cairo.Matrix()
                    mtr.rotate(self.rotate / 180.0 * math.pi)
                    context.transform(mtr)
                    if self.rotate == ROTATE_090:
                            context.translate(0.0, -pdf_width)
                    elif self.rotate == ROTATE_180:
                            context.translate(-pdf_width, -pdf_height)
                    elif self.rotate == ROTATE_270:
                            context.translate(-pdf_height, 0.0)
                    current_page.render(context)
                    context.restore()
                    context.show_page()
                    self.emit('donef', (float(index) + float(i) / float(
                        number_of_pages)) / float(total_documents))
                    if self.stop is True:
                            break
                pdfsurface.flush()
                pdfsurface.finish()
                shutil.copy(temp_pdf, file_out)
                os.remove(temp_pdf)
            if self.stop is True:
                    break
        if self.stop is True:
            self.emit('interrupted')
        else:
            self.emit('finished')


class DoitInBackgroundSplitFiles(DoitInBackgroundBase):
    def __init__(self, files):
        DoitInBackgroundBase.__init__(self)
        self.files = files

    def run(self):
        total_documents = len(self.files)
        if total_documents > 0:
            for index, file_in in enumerate(self.files):
                self.emit('todo', file_in)
                document = Poppler.Document.new_from_file('file://' + file_in,
                                                          None)
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
                        self.emit('donef', (float(index) + float(i) / float(
                            number_of_pages)) / float(total_documents))
                        if self.stop is True:
                                break
                if self.stop is True:
                        break
        if self.stop is True:
            self.emit('interrupted')
        else:
            self.emit('finished')


class DoitInBackgroundRemoveSomePages(DoitInBackgroundBase):
    def __init__(self, file_in, file_out, ranges):
        DoitInBackgroundBase.__init__(self)
        self.file_in = file_in
        self.file_out = file_out
        self.ranges = ranges

    def run(self):
        pages = tools.get_pages_from_ranges(self.ranges)
        document = Poppler.Document.new_from_file('file://' + self.file_in,
                                                  None)
        number_of_pages = document.get_n_pages()
        self.emit('start', number_of_pages)
        if number_of_pages > 0:
            temp_pdf = tools.create_temp_file()
            pdfsurface = cairo.PDFSurface(temp_pdf, 200, 200)
            context = cairo.Context(pdfsurface)
            self.emit('start', number_of_pages)
            for i in range(0, number_of_pages):
                self.emit('todo', '{0}/{1}'.format(i, number_of_pages))
                if i + 1 not in pages:
                    current_page = document.get_page(i)
                    context.save()
                    pdf_width, pdf_height = current_page.get_size()
                    pdfsurface.set_size(pdf_width, pdf_height)
                    current_page.render(context)
                    context.restore()
                    context.show_page()
                if self.stop is True:
                    break
                self.emit('done', '{0}/{1}'.format(i, number_of_pages))
            pdfsurface.flush()
            pdfsurface.finish()
            shutil.copy(temp_pdf, self.file_out)
            os.remove(temp_pdf)
        if self.stop is True:
            self.emit('interrupted')
        else:
            self.emit('finished')


class DoitInBackgroundRotateSomePages(DoitInBackgroundBase):
    def __init__(self, file_in, file_out, degrees, ranges):
        DoitInBackgroundBase.__init__(self)
        self.file_in = file_in
        self.file_out = file_out
        self.degrees = degrees
        self.ranges = ranges
        self.flip_vertical = False
        self.flip_horizontal = False

    def run(self):
        pages = tools.get_pages_from_ranges(self.ranges)
        document = Poppler.Document.new_from_file('file://' + self.file_in,
                                                  None)
        number_of_pages = document.get_n_pages()
        self.emit('start', number_of_pages)
        if number_of_pages > 0:
            temp_pdf = tools.create_temp_file()
            pdfsurface = cairo.PDFSurface(temp_pdf, 200, 200)
            context = cairo.Context(pdfsurface)
            for i in range(0, number_of_pages):
                self.emit('todo', '{0}/{1}'.format(i, number_of_pages))
                current_page = document.get_page(i)
                if i + 1 in pages:
                    if self.degrees == ROTATE_000 or\
                            self.degrees == ROTATE_180:
                        pdf_width, pdf_height = current_page.get_size()
                    else:
                        pdf_height, pdf_width = current_page.get_size()
                    pdfsurface.set_size(pdf_width, pdf_height)
                    context.save()
                    mtr = cairo.Matrix()
                    mtr.rotate(self.degrees / 180.0 * math.pi)
                    context.transform(mtr)
                    if self.degrees == ROTATE_090:
                            context.translate(0.0, -pdf_width)
                    elif self.degrees == ROTATE_180:
                            context.translate(-pdf_width, -pdf_height)
                    elif self.degrees == ROTATE_270:
                            context.translate(-pdf_height, 0.0)
                    if self.flip_vertical:
                        context.scale(1, -1)
                        if self.degrees == ROTATE_000 or\
                                self.degrees == ROTATE_180:
                            context.translate(0, -pdf_height)
                        else:
                            context.translate(0, -pdf_width)
                    if self.flip_horizontal:
                        context.scale(-1, 1)
                        if self.degrees == ROTATE_000 or\
                                self.degrees == ROTATE_180:
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
                if self.stop is True:
                    break
                self.emit('done', '{0}/{1}'.format(i, number_of_pages))
            pdfsurface.flush()
            pdfsurface.finish()
            shutil.copy(temp_pdf, self.file_out)
            os.remove(temp_pdf)
        if self.stop is True:
            self.emit('interrupted')
        else:
            self.emit('finished')


class DoitInBackgroundExtractSomePages(DoitInBackgroundBase):
    def __init__(self, files, ranges):
        DoitInBackgroundBase.__init__(self)
        self.files = files
        self.ranges = ranges

    def run(self):
        total_documents = len(self.files)
        pages = tools.get_pages_from_ranges(self.ranges)
        if total_documents > 0 and pages:
            for index, file_in in enumerate(self.files):
                self.emit('todo', file_in)
                document = Poppler.Document.new_from_file('file://' + file_in,
                                                          None)
                number_of_pages = document.get_n_pages()
                if number_of_pages > 1:
                    filename, filext = os.path.splitext(file_in)
                    file_out = filename + '_extracted_pages.pdf'
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
                        self.emit('donef', (float(index) + float(i) / float(
                            number_of_pages)) / float(total_documents))
                        if self.stop is True:
                                break
                    pdfsurface.flush()
                    pdfsurface.finish()
                    shutil.copy(temp_pdf, file_out)
                    os.remove(temp_pdf)
                if self.stop is True:
                        break
        if self.stop is True:
            self.emit('interrupted')
        else:
            self.emit('finished')


class DoitInBackgroundWithArgs(DoitInBackgroundBase):

    def __init__(self, maker, elements, *args):
        DoitInBackgroundBase.__init__(self)
        self.maker = maker
        self.elements = elements
        self.args = args

    def run(self):
        print(2)
        if self.elements:
            self.stop = False
            for an_element in self.elements:
                self.emit('todo', str(an_element))
                self.maker(an_element, *self.args)
                self.emit('done', str(an_element))
                if self.stop is True:
                    self.emit('interrupted')
                    break
        self.emit('finished')


class DoitInBackgroundOnlyOne(DoitInBackgroundBase):

    def __init__(self, maker, *args):
        DoitInBackgroundBase.__init__(self)
        self.maker = maker
        self.args = args

    def run(self):
        print(2)
        self.emit('todo', '')
        self.maker(*self.args)
        self.emit('done', '')
        self.emit('finished')


if __name__ == '__main__':
    import time

    def maker(element):
        print(element)
        return True

    elements = range(1, 100)
    dib = DoitInBackground(maker, elements)
    dib.start()
    time.sleep(2)
    exit(0)
