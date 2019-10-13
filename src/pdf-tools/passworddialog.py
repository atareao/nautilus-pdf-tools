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
except ValueError as e:
    print(e)
    exit(1)
from gi.repository import Gtk
import os
import comun
from basicdialog import BasicDialog
from comun import _


class PasswordDialog(BasicDialog):
    def __init__(self, title, window):
        BasicDialog.__init__(self, title, window)

    def init_ui(self):
        BasicDialog.init_ui(self)

        label1 = Gtk.Label(_('Password') + ':')
        label1.set_alignment(0, .5)
        self.grid.attach(label1, 0, 0, 1, 1)

        self.entry = Gtk.Entry()
        self.entry.set_tooltip_text(_(
            'Set password'))
        self.grid.attach(self.entry, 1, 0, 1, 1)

        self.image = Gtk.Image()
        if comun.is_package():
            self.image = Gtk.Image.new_from_icon_name(
                'pdf-tools-password-hide', Gtk.IconSize.BUTTON)
        else:
            self.image = Gtk.Image.new_from_file(
                os.path.join(comun.ICONDIR, 'pdf-tools-password-hide.svg'))
        self.entry.set_visibility(False)
        button_visibility = Gtk.Button()
        button_visibility.add(self.image)
        button_visibility.connect('clicked',
                                  self.on_button_visibility_clicked)
        self.grid.attach(button_visibility, 2, 0, 1, 1)

        self.show_all()

    def on_button_visibility_clicked(self, widget):
        if comun.is_package():
            if self.entry.get_visibility():
                self.image.set_from_icon_name('pdf-tools-password-hide',
                                              Gtk.IconSize.BUTTON)
            else:
                self.image.set_from_icon_name('pdf-tools-password-show',
                                              Gtk.IconSize.BUTTON)
        else:
            if self.entry.get_visibility():
                self.image.set_from_file(os.path.join(comun.ICONDIR,
                                         'pdf-tools-password-hide.svg'))
            else:
                self.image.set_from_file(os.path.join(comun.ICONDIR,
                                         'pdf-tools-password-show.svg'))
        self.entry.set_visibility(not self.entry.get_visibility())

    def get_password(self):
        return self.entry.get_text()


if __name__ == '__main__':
    dialog = PasswordDialog('Encrypt', None)
    dialog.run()
