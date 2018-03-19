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
    gi.require_version('Nautilus', '3.0')
    gi.require_version('GObject', '2.0')
    gi.require_version('Gtk', '3.0')
    gi.require_version('GdkPixbuf', '2.0')
except Exception as e:
    print(e)
    exit(1)
from gi.repository import Nautilus as FileManager
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import GdkPixbuf
import os
import sys
try:
    sys.path.insert(0, '/opt/extras.ubuntu.com/pdf-tools/share/pdf-tools')
    from pdfmanager import PDFManager
    from comun import APPNAME, ICON, VERSION
    from comun import _
    import tools
except Exception as e:
    print(e)
    exit(-1)

SEPARATOR = u'\u2015' * 10

"""
Tools to manipulate pdf
"""


class PdfToolsMenuProvider(GObject.GObject, FileManager.MenuProvider):
    """Implements the 'Replace in Filenames' extension to the File Manager
    right-click menu"""

    def __init__(self):
        """File Manager crashes if a plugin doesn't implement the __init__
        method"""
        self.pdfmanager = PDFManager()

    def doit(self, menu, option, selected):
        if option == 'rotate':
            self.pdfmanager.rotate_or_flip(selected)
        elif option == 'watermark':
            self.pdfmanager.watermark(selected)
        elif option == 'textmark':
            self.pdfmanager.textmark(selected)
        elif option == 'paginate':
            self.pdfmanager.paginate(selected)
        elif option == 'rotate pages':
            self.pdfmanager.rotate_some_pages(selected)
        elif option == 'remove pages':
            self.pdfmanager.remove_some_pages(selected)
        elif option == 'extract pages':
            self.pdfmanager.extract_some_pages(selected)
        elif option == 'join':
            self.pdfmanager.join_pdf_files(selected)
        elif option == 'split':
            self.pdfmanager.split_pdf_files(selected)
        elif option == 'combine':
            self.pdfmanager.combine_pdf_pages(selected)
        elif option == 'reduce':
            self.pdfmanager.reduce(selected)
        elif option == 'resize':
            self.pdfmanager.resize_pdf_pages(selected)
        elif option == 'convert2png':
            self.pdfmanager.convert_pdf_file_to_png(selected)
        elif option == 'convert2pdf':
            self.pdfmanager.create_pdf_from_images(selected)

    def get_file_items(self, window, sel_items):
        """Adds the 'Replace in Filenames' menu item to the File Manager
        right-click menu, connects its 'activate' signal to the 'run' method
        passing the selected Directory/File"""
        if tools.all_files_are_pdf(sel_items):
            top_menuitem = FileManager.MenuItem(
                name='PdfToolsMenuProvider::Gtk-pdf-tools',
                label=_('Pdf Tools'),
                tip=_('Tools to manipulate pdf files'),
                icon='Gtk-find-and-replace')
            #
            submenu = FileManager.Menu()
            top_menuitem.set_submenu(submenu)
            sub_menus = []
            items = [
                ('01', _('Rotate and flip'), _('rotate_and_flip pdf files'),
                 'rotate'),
                ('02', _('Watermark'), _('Watermark pdffiles'),
                 'watermark'),
                ('03', _('Textmark'), _('Textmark pdf files'),
                 'textmark'),
                ('04', _('Paginate'), _('Paginate pdf files'),
                 'paginate'),
                ('05', _('Rotate pages'),
                 _('Rotate pages of the document files'),
                 'rotate pages'),
                ('06', _('Remove pages'),
                 _('Remove pages of the document files'),
                 'remove pages'),
                ('07', _('Extract pages'),
                 _('Extract pages of the document files'),
                 'extract pages'),
                ('08', _('Join pdf files'),
                 _('Join pdf files in one document'),
                 'join'),
                ('09', _('Split pdf files'),
                 _('Split a pdf in several documents'),
                 'split'),
                ('10', _('Combine pdf pages'),
                 _('Combine pdf pages in one page'),
                 'combine'),
                ('11', _('Reduce pdf size'), _('Reduce pdf size'),
                 'reduce'),
                ('12', _('Resize pdf pages'), _('Resize pdf pages'),
                 'resize'),
                ('13', _('Convert pdf to png'),
                 _('Convert pdf file to png image'),
                 'convert2png'),
            ]
            for item in items:
                sub_menuitem = FileManager.MenuItem(
                    name='PdfToolsMenuProvider::Gtk-pdf-tools-' + item[0],
                    label=item[1],
                    tip=item[2])
                sub_menuitem.connect('activate', self.doit, item[3], sel_items)
                submenu.append_item(sub_menuitem)
            #
            sub_menuitem_98 = FileManager.MenuItem(
                name='PdfToolsMenuProvider::Gtk-None',
                label=SEPARATOR)
            submenu.append_item(sub_menuitem_98)
            #
            sub_menuitem_99 = FileManager.MenuItem(
                name='PdfToolsMenuProvider::Gtk-pdf-tools-99',
                label=_('About'),
                tip=_('About'),
                icon='Gtk-find-and-replace')
            sub_menuitem_99.connect('activate', self.about)
            submenu.append_item(sub_menuitem_99)
            #
            return top_menuitem,
        elif tools.all_files_are_images(sel_items):
            top_menuitem = FileManager.MenuItem(
                name='PdfToolsMenuProvider::Gtk-pdf-tools',
                label=_('Pdf Tools'),
                tip=_('Tools to manipulate pdf files'),
                icon='Gtk-find-and-replace')
            submenu = FileManager.Menu()
            top_menuitem.set_submenu(submenu)
            items = [
                ('51', _('Convert to pdf'),
                 _('Convert images to pdf'),
                 'convert2pdf')
            ]
            for item in items:
                sub_menuitem = FileManager.MenuItem(
                    name='PdfToolsMenuProvider::Gtk-pdf-tools-' + item[0],
                    label=item[1],
                    tip=item[2])
                sub_menuitem.connect('activate', self.doit, item[3], sel_items)
                submenu.append_item(sub_menuitem)
            #
            sub_menuitem_98 = FileManager.MenuItem(
                name='PdfToolsMenuProvider::Gtk-None',
                label=SEPARATOR)
            submenu.append_item(sub_menuitem_98)
            #
            sub_menuitem_99 = FileManager.MenuItem(
                name='PdfToolsMenuProvider::Gtk-pdf-tools-99',
                label=_('About'),
                tip=_('About'),
                icon='Gtk-find-and-replace')
            sub_menuitem_99.connect('activate', self.about)
            submenu.append_item(sub_menuitem_99)
            #
            return top_menuitem,
        return

    def about(self, widget):
        ad = Gtk.AboutDialog()
        ad.set_name(APPNAME)
        ad.set_version(VERSION)
        ad.set_copyright('Copyrignt (c) 2011-2018\nLorenzo Carbonell')
        ad.set_comments(_('Nautilus Pdf Tools'))
        ad.set_license('''
This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
''')
        ad.set_website('http://www.atareao.es')
        ad.set_website_label('http://www.atareao.es')
        ad.set_authors([
            'Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>'])
        ad.set_documenters([
            'Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>'])
        ad.set_logo(GdkPixbuf.Pixbuf.new_from_file(ICON))
        ad.set_icon(GdkPixbuf.Pixbuf.new_from_file(ICON))
        ad.set_program_name(APPNAME)
        ad.run()
        ad.destroy()

if __name__ == '__main__':
    '''
    cd = CreatePDFFromImagesDialog('Test')
    cd.run()
    '''
