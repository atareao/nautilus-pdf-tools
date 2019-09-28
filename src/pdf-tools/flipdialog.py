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
except Exception as e:
    print(e)
    exit(1)
from gi.repository import Gtk
import comun
from comun import _
from tools import get_ranges
from tools import get_pages_from_ranges
from basedialog import BaseDialog
class PageOptions():
    def __init__(self, rotation_angle, flip_horizontal, flip_vertical):
        self.rotation_angle = rotation_angle
        self.flip_horizontal= flip_horizontal
        self.flip_vertical = flip_vertical

class FlipDialog(BaseDialog):
    def __init__(self, filename=None, window=None):
        BaseDialog.__init__(self, _('Rotate and flid PDF'), filename, window)
    
    def set_page(self, page):
        if self.document.get_n_pages() > 0 and \
                page < self.document.get_n_pages() and\
                page >= 0:
            self.no_page = page
            self.show_page.set_text(str(self.no_page + 1))
            self.show_title_page.set_text(str(self.no_page + 1))
            if str(self.no_page) in self.pages.keys():
                rotation_angle = self.pages[str(self.no_page)].rotation_angle
                flip_horizontal = self.pages[str(self.no_page)].flip_horizontal
                flip_vertical = self.pages[str(self.no_page)].flip_vertical
            else:
                rotation_angle = 0
                flip_horizontal = False
                flip_vertical = False
            self.viewport1.set_page(self.document.get_page(self.no_page),
                                    rotation_angle, flip_horizontal,
                                    flip_vertical)

    def init_adicional_popover(self):

        def set_title_row(texto, gray=False):
            if gray:
                label = Gtk.Label()
                label.set_markup(
                    '<span foreground="gray">{}</span>'.format(texto))
            else:
                label = Gtk.Label(texto)
            label.set_width_chars(10)
            label.set_alignment(0, 0.5)
            row = Gtk.ListBoxRow()
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
            row.add(hbox)
            hbox.pack_start(label, True, True, 0)
            return row

        self.popover_listbox.add(set_title_row(_('Apply'), True))

        def set_option_rotate_apply(texto, check=None,
                                    parent=None, entry=False):
            row = Gtk.ListBoxRow()
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
            row.add(hbox)
            label = Gtk.Label(texto, xalign=0)
            if check is None:
                check = Gtk.RadioButton.new_from_widget(parent)
                check.connect("notify::active", self.slider_on_value_changed,
                              str(texto))
            hbox.pack_start(label, True, True, 0)
            
            if entry:
                textBox = Gtk.Entry()
                hbox.pack_start(textBox, True, True, 0)
            else:
                textBox = None
            hbox.pack_start(check, False, True, 0)
            return check, row, textBox

        self.check_this = Gtk.RadioButton.new_from_widget(None)
        self.check_this.connect("notify::active", self.slider_on_value_changed,
                                'This page')
        check, row, _ = set_option_rotate_apply('This page',
                                                      self.check_this)
        self.popover_listbox.add(row)
        self.check_all, row, textBox = set_option_rotate_apply(
            _('All'), None, self.check_this)
        self.popover_listbox.add(row)
        self.check_range, row, self.range = set_option_rotate_apply(
            _('Range'), None, self.check_this, True)
        self.popover_listbox.add(row)

        self.popover_listbox.add(self.set_separator())

        self.popover_listbox.add(set_title_row(_('Rotate'), True))

        def set_option_rotate_row(texto, check=None, parent=None):
            row = Gtk.ListBoxRow()
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
            row.add(hbox)
            label = Gtk.Label(texto, xalign=0)
            if check is None:
                check = Gtk.RadioButton.new_from_widget(parent)
                check.connect("notify::active", self.slider_on_value_changed,
                              str(texto))
            hbox.pack_start(label, True, True, 0)
            hbox.pack_start(check, False, True, 0)
            return check, row

        self.rotate_0 = Gtk.RadioButton.new_from_widget(None)
        self.rotate_0.connect("notify::active", self.slider_on_value_changed,
                              '0')
        check, row =set_option_rotate_row('0', self.rotate_0)
        self.popover_listbox.add(row)

        self.rotate_90, row = set_option_rotate_row('90', None, self.rotate_0)
        self.popover_listbox.add(row)

        self.rotate_180, row = set_option_rotate_row('180', None,
                                                     self.rotate_0)
        self.popover_listbox.add(row)

        self.rotate_270, row = set_option_rotate_row('270', None,
                                                     self.rotate_0)
        self.popover_listbox.add(row)

        self.popover_listbox.add(self.set_separator())
        self.popover_listbox.add(set_title_row(_('Flip'), True))

        def set_option_flip_row(texto):
            row = Gtk.ListBoxRow()
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
            row.add(hbox)
            label = Gtk.Label(texto, xalign=0)
            check = Gtk.Switch()
            check.connect("notify::active", self.slider_on_value_changed,
                          texto)
            hbox.pack_start(label, True, True, 0)
            hbox.pack_start(check, False, True, 0)
            return check, row

        self.check_vertical, row = set_option_flip_row(_('Vertical'))
        self.popover_listbox.add(row)
        self.check_horizontal, row = set_option_flip_row(_('Horizontal'))
        self.popover_listbox.add(row)

        self.popover_listbox.add(self.set_separator())
        self.popover_listbox.add(set_title_row(_('File name'), True))

        row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        row.add(hbox)
        label = Gtk.Label(_('Add to file'), xalign=0)
        text = Gtk.Entry()
        hbox.pack_start(label, True, True, 0)
        hbox.pack_start(text, False, True, 0)
        self.popover_listbox.add(row)

    def slider_on_value_changed(self, widget, value, name):
        flip_horizontal = self.check_horizontal.get_active()
        flip_vertical = self.check_vertical.get_active()
        if name == '90':
            rotation_angle = 1.0
        elif name == '180':
            rotation_angle = 2.0
        elif name == '270':
            rotation_angle = 3.0
        else:
            rotation_angle = 0.0
        update = False
        if self.check_this.get_active():
            update = True
            self.pages[str(self.no_page)] = PageOptions(rotation_angle,
                                                        flip_horizontal,
                                                        flip_vertical)
        elif self.check_all.get_active():
            update = True
            for i in range(0, self.document.get_n_pages()):
                self.pages[str(i)] = PageOptions(rotation_angle,
                                                 flip_horizontal,
                                                 flip_vertical)
        elif self.check_range.get_active():
            text = self.range.get_text()
            if text:
                ranges = get_ranges(text)
                pages = get_pages_from_ranges(ranges)
                update = (str(self.no_page) in self.pages.keys())
                for i in pages:
                    self.pages[str(i)] = PageOptions(rotation_angle,
                                                     flip_horizontal,
                                                     flip_vertical)
        if update:
            self.viewport1.rotation_angle = rotation_angle
            self.viewport1.flip_horizontal = flip_horizontal
            self.viewport1.flip_vertical = flip_vertical
            self.viewport1.queue_draw()

if __name__ == '__main__':
    dialog = FlipDialog(comun.SAMPLE)
    dialog.run()
