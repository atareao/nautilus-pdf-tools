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
    gi.require_version('GLib', '2.0')
    gi.require_version('GObject', '2.0')
except Exception as e:
    print(e)
    exit(1)
from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import GObject
import threading
from basicdialog import BasicDialog


class Progreso(BasicDialog, threading.Thread):
    __gsignals__ = {
        'i-want-stop': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
    }

    def __init__(self, title, parent, max_value, label=None):
        self.max_value = max_value
        self.text_label = label
        self.stop = False
        self.value = 0.0
        BasicDialog.__init__(self, title, parent)
        self.set_size_request(330, 30)

    def init_ui(self):
        BasicDialog.init_ui(self)


        self.label = Gtk.Label()
        self.grid.attach(self.label, 0, 0, 1, 1)
        if self.text_label is not None:
            self.label.set_label(self.text_label)

        self.progressbar = Gtk.ProgressBar()
        self.progressbar.set_size_request(300, 0)
        self.grid.attach(self.progressbar, 0, 1, 1, 1)

        button_stop = Gtk.Button()
        button_stop.set_size_request(40, 40)
        button_stop.set_image(
            Gtk.Image.new_from_stock(Gtk.STOCK_STOP, Gtk.IconSize.BUTTON))
        button_stop.connect('clicked', self.on_button_stop_clicked)
        self.grid.attach(button_stop, 1, 0, 1, 3)


    def set_max_value(self, widget, max_value):
        self.max_value = max_value

    def get_stop(self):
        return self.stop

    def on_button_stop_clicked(self, widget):
        self.stop = True
        self.emit('i-want-stop')

    def set_todo_label(self, widget, todo_label):
        if len(todo_label) > 35:
            text = '...' + todo_label[-32:]
        else:
            text = todo_label
        GLib.idle_add(self.label.set_label, text)

    def set_value(self, widget, value):
        if value >= 0 and value <= self.max_value:
            self.value = value
            fraction = self.value / self.max_value
            GLib.idle_add(self.progressbar.set_fraction, fraction)

    def set_fraction(self, widget, fraction):
        print('****', fraction)
        if fraction >= 0 and fraction <= 1.0:
            GLib.idle_add(self.progressbar.set_fraction, fraction)

    def close(self, widget=None):
        self.destroy()

    def increase(self, widget, label):
        self.value += 1.0
        fraction = self.value / self.max_value
        print('====', self.value, self.max_value, fraction, '====')
        GLib.idle_add(self.progressbar.set_fraction, fraction)
        if len(label) > 35:
            text = '...' + label[-32:]
        else:
            text = label
        GLib.idle_add(self.label.set_label, text)

    def decrease(self):
        self.value -= 1.0
        fraction = self.value / self.max_value
        GLib.idle_add(self.progressbar.set_fraction, fraction)


if __name__ == '__main__':
    import time
    from doitinbackground import DoitInBackground
    p = Progreso('Prueba', None, 5)

    def maker(element):
        print('==== %s ====' % (element))
        time.sleep(0.5)

    elements = range(0, 5)
    dib = DoitInBackground(maker, elements)
    p.connect('i-want-stop', dib.stop_it)
    dib.connect('done', p.increase)
    dib.start()
    p.run()
