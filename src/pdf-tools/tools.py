#!/usr/bin/env python3
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
    gi.require_version('Gtk', '3.0')
    gi.require_version('Gdk', '3.0')
    gi.require_version('GdkPixbuf', '2.0')
    gi.require_version('Poppler', '0.18')
except ValueError as e:
    print(e)
    exit(1)
from gi.repository import Gdk, GdkPixbuf, Gtk, Poppler
import mimetypes
import os
import shutil
import sh
import tempfile
try:
    from urllib.parse import unquote_plus
except:
    # Python2
    from urllib import unquote_plus
import cairo
from comun import (ALL_MIMETYPES_IMAGE, EXTENSIONS_FROM, MIMETYPES_IMAGE,
                   MIMETYPES_PDF, MIMETYPES_PNG, MMTOPIXEL, MMTOPNG, _)



mimetypes.init()


def update_preview_cb(file_chooser, preview):
    filename = file_chooser.get_preview_filename()
    try:
        if os.path.isfile(filename) and \
                mimetypes.guess_type(filename)[0] in MIMETYPES_PDF:
            pixbuf = get_pixbuf_from_pdf(filename, 250)
            file_chooser.set_preview_widget(Gtk.Image.new_from_pixbuf(pixbuf))
            has_preview = True
        elif os.path.isfile(filename) and\
                mimetypes.guess_type(filename)[0] in ALL_MIMETYPES_IMAGE:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(filename, 250, 250)
            file_chooser.set_preview_widget(Gtk.Image.new_from_pixbuf(pixbuf))
            has_preview = True
        else:
            has_preview = False
    except Exception as e:
        print(e)
        has_preview = False
    file_chooser.set_preview_widget_active(has_preview)
    return


def get_pages_from_ranges(ranges):
    pages = []
    for rang in ranges:
        if len(rang) > 1:
            for i in range(rang[0], rang[1]):
                if i not in pages:
                    pages.append(i)
        else:
            if not rang[0] in pages:
                pages.append(rang[0])
    return pages


def create_temp_file():
    return tempfile.mkstemp(prefix='tmp_filemanager_pdf_tools_')[1]


def dialog_save_as_image(title, original_file, window):
    dialog = Gtk.FileChooserDialog(title,
                                   window,
                                   Gtk.FileChooserAction.SAVE,
                                   (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                    Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
    dialog.set_default_response(Gtk.ResponseType.OK)
    dialog.set_current_folder(os.path.dirname(original_file))
    dialog.set_filename(original_file)
    for aMimetype in MIMETYPES_IMAGE.keys():
        filtert = Gtk.FileFilter()
        filtert.set_name(aMimetype)
        for mime_type in MIMETYPES_IMAGE[aMimetype]['mimetypes']:
            filtert.add_mime_type(mime_type)
        for pattern in MIMETYPES_IMAGE[aMimetype]['patterns']:
            filtert.add_pattern(pattern)
        dialog.add_filter(filtert)
    if dialog.run() == Gtk.ResponseType.OK:
        filename = dialog.get_filename()
    else:
        filename = None
    dialog.destroy()
    return filename


def dialog_save_as(title, original_file, window):
    dialog = Gtk.FileChooserDialog(title,
                                   window,
                                   Gtk.FileChooserAction.SAVE,
                                   (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                    Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
    dialog.set_default_response(Gtk.ResponseType.OK)
    dialog.set_current_folder(os.path.dirname(original_file))
    dialog.set_filename(original_file)
    for mimetype in MIMETYPES_PDF:
        filtert = Gtk.FileFilter()
        filtert.set_name(_('Pdf files'))
        filtert.add_mime_type(mimetype)
        for pattern in mimetypes.guess_all_extensions(mimetype):
            filtert.add_pattern('*' + pattern)
        dialog.add_filter(filtert)
    if dialog.run() == Gtk.ResponseType.OK:
        filename = dialog.get_filename()
        if not filename.endswith('.pdf'):
            filename += '.pdf'
    else:
        filename = None
    dialog.destroy()
    return filename


def dialog_save_as_text(title, original_file, window):
    dialog = Gtk.FileChooserDialog(title,
                                   window,
                                   Gtk.FileChooserAction.SAVE,
                                   (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                    Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
    dialog.set_default_response(Gtk.ResponseType.OK)
    dialog.set_current_folder(os.path.dirname(original_file))
    dialog.set_filename(original_file)
    filtert = Gtk.FileFilter()
    filtert.set_name(_('Text file'))
    filtert.add_mime_type('text/plain')
    filtert.add_pattern('*.txt')
    dialog.add_filter(filtert)
    dialog.set_filter(filtert)
    if dialog.run() == Gtk.ResponseType.OK:
        filename = dialog.get_filename()
        if not filename.endswith('.txt'):
            filename += '.txt'
    else:
        filename = None
    dialog.destroy()
    return filename


def create_image_surface_from_file(filename, zoom=1.0):
    pixbuf = GdkPixbuf.Pixbuf.new_from_file(filename)
    return create_image_surface_from_pixbuf(pixbuf, zoom)


def create_image_surface_from_pixbuf(pixbuf, zoom=1.0):
    surface = cairo.ImageSurface(
        cairo.FORMAT_ARGB32,
        int(pixbuf.get_width() * zoom),
        int(pixbuf.get_height() * zoom))
    context = cairo.Context(surface)
    context.save()
    context.scale(zoom, zoom)
    Gdk.cairo_set_source_pixbuf(context, pixbuf, 0, 0)
    context.paint()
    context.restore()
    return surface


def get_pixbuf_from_pdf(file_in, height):
    surface = get_surface_from_pdf(file_in, height)
    if surface is not None:
            print(surface.get_width(), surface.get_height())
            return Gdk.pixbuf_get_from_surface(surface, 0, 0,
                                               surface.get_width(),
                                               surface.get_height())
    return None


def get_surface_from_pdf(file_in, height):
    if os.path.isfile(file_in):
        document = Poppler.Document.new_from_file('file://' + file_in, None)
        number_of_pages = document.get_n_pages()
        if number_of_pages > 0:
            current_page = document.get_page(0)
            page_width, page_height = current_page.get_size()
            if page_width > page_height:
                zoom = height / page_width
            else:
                zoom = height / page_height
            print(int(page_width * zoom), int(page_height * zoom))
            image_surface = cairo.ImageSurface(cairo.FORMAT_RGB24,
                                               int(page_width * zoom),
                                               int(page_height * zoom))
            context = cairo.Context(image_surface)
            context.save()
            context.set_source_rgba(1.0, 1.0, 1.0, 1.0)
            context.paint()
            mtr = cairo.Matrix()
            mtr.scale(zoom, zoom)
            context.transform(mtr)
            current_page.render(context)
            context.restore()
            return image_surface
    return None


def convert_pdf_to_png(file_in):
    document = Poppler.Document.new_from_file('file://' + file_in, None)
    number_of_pages = document.get_n_pages()
    if number_of_pages > 0:
        file_out = os.path.splitext(file_in)[0]
        for i in range(0, number_of_pages):
            current_page = document.get_page(i)
            pdf_width, pdf_height = current_page.get_size()
            file_out_i = '%s_%s%s' % (file_out, i + 1, '.png')
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


def create_from_images(file_out, images, width=1189, height=1682, margin=0):
    temp_pdf = create_temp_file()
    pdfsurface = cairo.PDFSurface(temp_pdf, width, height)
    context = cairo.Context(pdfsurface)
    for image in images:
        if mimetypes.guess_type(image)[0] in MIMETYPES_PNG:
            imagesurface = cairo.ImageSurface.create_from_png(image)
        else:
            imagesurface = create_image_surface_from_file(image)
        imagesurface_width = imagesurface.get_width()
        imagesurface_height = imagesurface.get_height()
        scale_x = (imagesurface_width / MMTOPIXEL) / width
        scale_y = (imagesurface_height / MMTOPIXEL) / height
        if scale_x > scale_y:
            scale = scale_x
        else:
            scale = scale_y
        if margin == 1:
            scale = scale * 1.05
        elif margin == 2:
            scale = scale * 1.15
        x = (width - imagesurface_width / MMTOPIXEL / scale) / 2
        y = (height - imagesurface_height / MMTOPIXEL / scale) / 2
        context.save()
        context.translate(x, y)
        context.scale(1.0 / MMTOPIXEL / scale, 1.0 / MMTOPIXEL / scale)
        context.set_source_surface(imagesurface)
        context.paint()
        context.restore()
        context.show_page()
    pdfsurface.flush()
    pdfsurface.finish()
    shutil.copy(temp_pdf, file_out)
    os.remove(temp_pdf)


def reduce_pdf(file_in, dpi, append):
    try:
        file_out = get_output_filename(file_in, append)
        options = ['-q','-dNOPAUSE','-dBATCH','-dSAFER','-sDEVICE=pdfwrite',
                   '-dCompatibilityLevel=1.4','-dPDFSETTINGS=/screen',
                   '-dEmbedAllFonts=true','-dSubsetFonts=true',
                   '-dDownsampleColorImages=true','-dColorImageResolution=100',
                   '-dColorImageDownsampleType=/Bicubic',
                   '-dColorImageResolution="{}"'.format(dpi),
                   '-dGrayImageDownsampleType=/Bicubic',
                   '-dGrayImageResolution="{}"'.format(dpi),
                   '-dMonoImageDownsampleType=/Bicubic',
                   '-dMonoImageResolution="{}"'.format(dpi),
                   '-sOutputFile="{}"'.format(file_out),
                   '"{}"'.format(file_in)]
        sh.ghostscript(options)
    except Exception as e:
        print(e)


def convert2png(file_in, file_out):
    im = Image.open(file_in)
    im.save(file_out)


def get_output_filename(file_in, modificator):
    if os.path.exists(file_in) and os.path.isfile(file_in):
        head, tail = os.path.split(file_in)
        root, ext = os.path.splitext(tail)
        file_out = os.path.join(head, root + modificator + ext)
        return file_out
    return None


def get_files(files_in):
    files = []
    for file_in in files_in:
        file_in = unquote_plus(file_in.get_uri()[7:])
        if os.path.isfile(file_in):
            files.append(file_in)
    if files:
        return files
    return None


def get_num(chain):
    try:
        chain = chain.strip()  # removing spaces
        return int(float(chain))
    except Exception as e:
        print(e)
    return None


def str2int(string):
    try:
        valor = int(string)
    except ValueError:
        valor = 0
    except Exception:
        valor = 0
    return valor

def get_ranges(chain):
    ranges = []
    if chain.find(',') > -1:
        for part in chain.split(','):
            if part.find('-') > -1:
                parts = part.split('-')
                if len(parts) > 1:
                    f = get_num(parts[0])
                    t = get_num(parts[1])
                    if f is not None and t is not None:
                        ranges.append([f, t])
            else:
                el = get_num(part)
                if el:
                    ranges.append([el])
    elif chain.find('-') > -1:
        parts = chain.split('-')
        if len(parts) > 1:
            f = get_num(parts[0])
            t = get_num(parts[1])
            if f is not None and t is not None:
                ranges.append([f, t])
    else:
        el = get_num(chain)
        if el:
            ranges.append([el])
    return ranges


def all_files_are_pdf(items):
    for item in items:
        _, fileExtension = os.path.splitext(
            unquote_plus(item.get_uri()[7:]))
        if fileExtension.lower() != '.pdf':
            return False
    return True


def all_files_are_images(items):
    for item in items:
        _, fileExtension = os.path.splitext(
            unquote_plus(item.get_uri()[7:]))
        if fileExtension.lower() in EXTENSIONS_FROM:
            return True
    return False
