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
    gi.require_version('Poppler', '0.18')
    gi.require_version('GdkPixbuf', '2.0')
    gi.require_version('Gio', '2.0')
except Exception as e:
    print(e)
    exit(1)
from gi.repository import Gtk
from gi.repository import Poppler
from gi.repository import GdkPixbuf
from gi.repository import Gio
import os
from miniview import MiniView
import comun
from comun import _
from comun import ROTATE_000, ROTATE_090, ROTATE_180, ROTATE_270
from tools import center_dialog
from tools import get_ranges
from tools import get_pages_from_ranges
from tools import str2int


    def set_separator():
        row = Gtk.ListBoxRow()
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.pack_start(Gtk.Separator(), True, True, 0)
        vbox.set_margin_top(10)
        vbox.set_margin_bottom(10)
        row.add(vbox)
        return row

class BaseDialog(Gtk.Dialog):
    def __init__(self, title= '', filename=None, window=None):
        Gtk.Dialog.__init__(self, title, window)
        self.set_modal(True)
        self.set_destroy_with_parent(True)
        self.add_button(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT)
        self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        self.set_default_size(600, 600)
        self.set_resizable(True)
        self.set_icon_from_file(comun.ICON)
        self.connect('destroy', self.close)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        hbox.set_border_width(10)
        self.get_content_area().add(hbox)

        self.scrolledwindow1 = Gtk.ScrolledWindow()
        self.scrolledwindow1.set_size_request(630, 630)
        hbox.pack_start(self.scrolledwindow1, False, False, 0)

        self.viewport1 = MiniView()
        self.scrolledwindow1.add(self.viewport1)

        self.pages = {}

        self.scale = 100

        self.init_headerbar()

        if filename is not None:
            uri = "file://" + filename
            self.document = Poppler.Document.new_from_file(uri, None)
            self.hb.set_subtitle(os.path.basename(filename))
            self.set_page(0)

        self.show_all()
        center_dialog(self)

    def set_page(self, page):
        if self.document.get_n_pages() > 0 and \
                page < self.document.get_n_pages() and\
                page >= 0:
            self.no_page = page
            self.show_page.set_text(str(self.no_page + 1))
            self.show_title_page.set_text(str(self.no_page + 1))
            self.viewport1.set_page(self.document.get_page(self.no_page))

    def next_page(self, button):
        self.set_page(self.no_page + 1)

    def previous_page(self, button):
        self.set_page(self.no_page - 1)

    def first_page(self, button):
        self.set_page(0)

    def last_page(self, button):
        self.set_page(self.document.get_n_pages() - 1)


    def init_headerbar(self):
        self.hb = Gtk.HeaderBar()
        self.hb.set_show_close_button(True)
        self.hb.set_title(self.get_title())
        self.set_titlebar(self.hb)

        button0 = Gtk.Button()
        button0.set_tooltip_text(_('First page'))
        button0.set_image(Gtk.Image.new_from_gicon(Gio.ThemedIcon(
            name='go-first-symbolic'), Gtk.IconSize.BUTTON))
        button0.connect('clicked', self.first_page)
        self.hb.pack_start(button0)

        button1 = Gtk.Button()
        button1.set_tooltip_text(_('Previous page'))
        button1.set_image(Gtk.Image.new_from_gicon(Gio.ThemedIcon(
            name='go-previous-symbolic'), Gtk.IconSize.BUTTON))
        button1.connect('clicked', self.previous_page)
        self.hb.pack_start(button1)

        self.show_title_page = Gtk.Entry()
        self.show_title_page.set_width_chars(5)
        self.show_title_page.set_alignment(0.5)
        self.show_title_page.set_tooltip_text(_('Current_page'))
        self.show_title_page.connect('activate', self.on_current_page_activate)
        self.hb.pack_start(self.show_title_page)

        button2 = Gtk.Button()
        button2.set_tooltip_text(_('Next page'))
        button2.set_image(Gtk.Image.new_from_gicon(Gio.ThemedIcon(
            name='go-next-symbolic'), Gtk.IconSize.BUTTON))
        button2.connect('clicked', self.next_page)
        self.hb.pack_start(button2)

        button3 = Gtk.Button()
        button3.set_tooltip_text(_('Last page'))
        button3.set_image(Gtk.Image.new_from_gicon(Gio.ThemedIcon(
            name='go-last-symbolic'), Gtk.IconSize.BUTTON))
        button3.connect('clicked', self.last_page)
        self.hb.pack_start(button3)

        popover = self.create_popover()
        button4 = Gtk.MenuButton()
        button4.set_size_request(40, 40)
        button4.set_tooltip_text(_('Options'))
        button4.set_popover(popover)
        button4.set_image(Gtk.Image.new_from_gicon(Gio.ThemedIcon(
            name='pan-down-symbolic'), Gtk.IconSize.BUTTON))
        self.hb.pack_end(button4)

    def create_popover(self):
        popover = Gtk.Popover()
        self.popover_listbox = Gtk.ListBox()
        self.popover_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.popover_listbox.set_margin_start(10)
        self.popover_listbox.set_margin_end(10)
        self.popover_listbox.set_margin_top(10)
        self.popover_listbox.set_margin_bottom(10)
        popover.add(self.popover_listbox)

        row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        row.add(hbox)
        self.popover_listbox.add(row)

        button0 = Gtk.Button()
        button0.set_tooltip_text(_('First page'))
        button0.set_image(Gtk.Image.new_from_gicon(Gio.ThemedIcon(
            name='go-first-symbolic'), Gtk.IconSize.BUTTON))
        button0.connect('clicked', self.first_page)
        hbox.pack_start(button0, True, True, 0)

        button1 = Gtk.Button()
        button1.set_tooltip_text(_('Previous page'))
        button1.set_image(Gtk.Image.new_from_gicon(Gio.ThemedIcon(
            name='go-previous-symbolic'), Gtk.IconSize.BUTTON))
        button1.connect('clicked', self.previous_page)
        hbox.pack_start(button1, True, True, 0)

        self.show_page = Gtk.Entry()
        self.show_page.set_alignment(0.5)
        self.show_page.set_tooltip_text(_('Current_page'))
        self.show_page.connect('activate', self.on_current_page_activate)
        hbox.pack_start(self.show_page, True, True, 0)

        button2 = Gtk.Button()
        button2.set_tooltip_text(_('Next page'))
        button2.set_image(Gtk.Image.new_from_gicon(Gio.ThemedIcon(
            name='go-next-symbolic'), Gtk.IconSize.BUTTON))
        button2.connect('clicked', self.next_page)
        hbox.pack_start(button2, True, True, 0)

        button3 = Gtk.Button()
        button3.set_tooltip_text(_('Last page'))
        button3.set_image(Gtk.Image.new_from_gicon(Gio.ThemedIcon(
            name='go-last-symbolic'), Gtk.IconSize.BUTTON))
        button3.connect('clicked', self.last_page)
        hbox.pack_start(button3, True, True, 0)
        self.popover_listbox.add(set_separator())

        self.init_adicional_popover()

        popover.show_all()
        return popover

    def init_adicional_popover(self):
        pass

    def on_current_page_activate(self, widget):
        page = str2int(widget.get_text()) - 1
        if page > -1 and page < self.document.get_n_pages():
            self.set_page(page)
        else:
            self.show_page.set_text(str(self.no_page + 1))
            self.show_title_page.set_text(str(self.no_page + 1))


    def close(self, widget):
        self.destroy()


if __name__ == '__main__':
    dialog = BaseDialog('Ejemplo', comun.SAMPLE)
    dialog.run()
