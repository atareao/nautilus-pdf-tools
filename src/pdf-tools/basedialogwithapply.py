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
from basedialog import (BaseDialog, generate_check_entry_row,
                        generate_check_row,
                        generate_separator_row,
                        generate_title_row)
from comun import _


class BaseDialogWithApply(BaseDialog):
    def __init__(self, title= '', filename=None, window=None):
        BaseDialog.__init__(self, title, filename, window)

    def set_page(self, page):
        if self.document.get_n_pages() > 0 and \
                page < self.document.get_n_pages() and\
                page >= 0:
            self.no_page = page
            self.show_page.set_text(str(self.no_page + 1))
            self.show_title_page.set_text(str(self.no_page + 1))

    def init_adicional_popover(self):
        self.popover_listbox.add(generate_title_row(_('Clear or apply to'), True))

        self.check_this, row = generate_check_row(_('This page'), None, None)
        self.popover_listbox.add(row)
        self.check_all, row = generate_check_row(_('All'), self.check_this,
                                                  None)
        self.popover_listbox.add(row)

        self.check_range, self.range, row = generate_check_entry_row(
            _('Range'), self.check_this, None)
        self.popover_listbox.add(row)

        self.popover_listbox.add(generate_separator_row())

        row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        row.add(hbox)
        clear_button = Gtk.Button.new_with_label(_('Clear'))
        clear_button.connect('clicked', self.on_apply_clicked, True)
        hbox.pack_start(clear_button, True, True, 0)
        apply_button = Gtk.Button.new_with_label(_('Apply'))
        apply_button.connect('clicked', self.on_apply_clicked)
        hbox.pack_start(apply_button, True, True, 0)
        self.popover_listbox.add(row)

        self.popover_listbox.add(generate_separator_row())

    def on_apply_clicked(self, widget, clear=False):
        pass

if __name__ == '__main__':
    dialog = BaseDialogWithApply(comun.SAMPLE)
    dialog.run()
