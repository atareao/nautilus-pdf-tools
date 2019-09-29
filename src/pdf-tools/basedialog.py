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
    gi.require_version('Gio', '2.0')
except Exception as e:
    print(e)
    exit(1)
from gi.repository import Gtk
from gi.repository import Poppler
from gi.repository import Gio
import os
from miniview import MiniView
import comun
from comun import _
from tools import center_dialog
from tools import str2int

HEIGHT = 25

def generate_widget_row(text, widget=None):
    row = Gtk.ListBoxRow()
    hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
    row.add(hbox)
    label = Gtk.Label(text, xalign=0)
    label.set_size_request(0, HEIGHT)
    hbox.pack_start(label, True, True, 0)
    if widget is not None:
        hbox.pack_start(widget, False, True, 0)
    return row


def generate_simple_button_row(text, callback):
    row = Gtk.ListBoxRow()
    button = Gtk.Button.new_with_label(text)
    button.connect('clicked', callback)
    row.add(button)
    return button, row


def generate_separator_row():
    row = Gtk.ListBoxRow()
    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    vbox.pack_start(Gtk.Separator(), True, True, 0)
    vbox.set_margin_top(10)
    vbox.set_margin_bottom(10)
    row.add(vbox)
    return row

def generate_title_row(text, gray=False):
    if gray:
        label = Gtk.Label()
        label.set_markup(
            '<span foreground="gray">{}</span>'.format(text))
    else:
        label = Gtk.Label(text)
    label.set_size_request(0, HEIGHT)
    label.set_width_chars(10)
    label.set_alignment(0, 0.5)
    row = Gtk.ListBoxRow()
    hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
    row.add(hbox)
    hbox.pack_start(label, True, True, 0)
    return row


def generate_entry_row(text):
    textBox = Gtk.Entry()
    row = generate_widget_row(text, textBox)
    return textBox, row


def generate_check_row(text, parent=None, callback=None):
    check = Gtk.RadioButton.new_from_widget(parent)
    if callback is not None:
        check.connect("notify::active", callback, str(text))
    row = generate_widget_row(text, check)
    return check, row


def generate_check_entry_row(text, parent, callback=None):
    row = Gtk.ListBoxRow()
    hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
    row.add(hbox)
    label = Gtk.Label(text, xalign=0)
    label.set_size_request(0, HEIGHT)
    entry = Gtk.Entry()
    check = Gtk.RadioButton.new_from_widget(parent)
    if callback is not None:
        check.connect("notify::active", callback, str(text))
    hbox.pack_start(label, True, True, 0)
    hbox.pack_start(entry, True, True, 0)
    hbox.pack_start(check, False, True, 0)
    return check, entry, row


def generate_swith_row(text, callback=None):
    switch = Gtk.Switch()
    if callback is not None:
        switch.connect("notify::active", callback, str(text))
    row = generate_widget_row(text, switch)
    return switch, row

def generate_button_row(text, callback=None):
    button = Gtk.Button()
    if callback is not None:
        button.connect('clicked', callback)
    row = generate_widget_row(text, button)
    return button, row

def generate_spinbutton_row(text, callback=None):
    spinButton = Gtk.SpinButton()
    if callback is not None:
        spinButton.connect('change-value', callback, str(text))
    row = generate_widget_row(text, spinButton)
    return spinButton, row


def generate_button(icon, tooltip_text, callback):
    button = Gtk.Button()
    button.set_tooltip_text(tooltip_text)
    button.set_image(Gtk.Image.new_from_gicon(Gio.ThemedIcon(
        name=icon), Gtk.IconSize.BUTTON))
    button.connect('clicked', callback)
    return button


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

        button0 = generate_button('go-first-symbolic', _('First page'),
                                  self.first_page)
        self.hb.pack_start(button0)
        button1 = generate_button('go-previous-symbolic', _('Previous page'),
                                  self.previous_page)
        self.hb.pack_start(button1)

        self.show_title_page = Gtk.Entry()
        self.show_title_page.set_width_chars(5)
        self.show_title_page.set_alignment(0.5)
        self.show_title_page.set_tooltip_text(_('Current_page'))
        self.show_title_page.connect('activate', self.on_current_page_activate)
        self.hb.pack_start(self.show_title_page)

        button2 = generate_button('go-next-symbolic', _('Next page'),
                                  self.next_page)
        self.hb.pack_start(button2)

        button3 = generate_button('go-last-symbolic', _('Last page'),
                                  self.last_page)
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

        button0 = generate_button('go-first-symbolic', _('First page'),
                                  self.first_page)
        hbox.pack_start(button0, True, True, 0)

        button1 = generate_button('go-previous-symbolic', _('Previous page'),
                                  self.previous_page)
        hbox.pack_start(button1, True, True, 0)

        self.show_page = Gtk.Entry()
        self.show_page.set_alignment(0.5)
        self.show_page.set_tooltip_text(_('Current_page'))
        self.show_page.connect('activate', self.on_current_page_activate)
        hbox.pack_start(self.show_page, True, True, 0)

        button2 = generate_button('go-next-symbolic', _('Next page'),
                                  self.next_page)
        hbox.pack_start(button2, True, True, 0)

        button3 = generate_button('go-last-symbolic', _('Last page'),
                                  self.last_page)
        hbox.pack_start(button3, True, True, 0)
        self.popover_listbox.add(generate_separator_row())

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
