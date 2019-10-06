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
    gi.require_version('Poppler', '0.18')
except Exception as e:
    print(e)
    exit(1)
from gi.repository import Poppler
import os
import shutil
import cairo
from PyPDF2 import PdfFileReader, PdfFileWriter
import tools


def get_num_of_pages(file_in):
    document = Poppler.Document.new_from_file('file://' + file_in, None)
    return document.get_n_pages()


def extractText(file_in):
    text = ''
    document_in = PdfFileReader(open(file_in, 'rb'))
    for i in range(0, document_in.getNumPages()):
        page = document_in.getPage(i)
        text += '\n' + page.extractText()
    return text


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


def encrypt(file_in, password):
    document_in = PdfFileReader(open(file_in, 'rb'))
    document_out = PdfFileWriter()
    document_out.cloneReaderDocumentRoot(document_in)
    document_out.encrypt(password)
    tmp_file = tools.create_temp_file()
    document_out.write(open(tmp_file, 'wb'))
    shutil.copy(tmp_file, file_in)
    os.remove(tmp_file)


def decrypt(file_in, password):
    document_in = PdfFileReader(open(file_in, 'rb'))
    if document_in.isEncrypted:
        while True:
            matched = document_in.decrypt(password)
            if matched:
                document_out = PdfFileWriter()
                document_out.cloneReaderDocumentRoot(document_in)
                tmp_file = tools.create_temp_file()
                document_out.write(open(tmp_file, 'wb'))
                shutil.copy(tmp_file, file_in)
                os.remove(tmp_file)
                return True
    return False

if __name__ == '__main__':
