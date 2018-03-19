#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of pdf-tools
#
# Copyright (C) 2012-2016 Lorenzo Carbonell
# lorenzo.carbonell.cerezo@gmail.com
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


from gi.repository import Gtk
from gi.repository import GObject
import threading


class Progreso(Gtk.Dialog, threading.Thread):
    __gsignals__ = {
        'i-want-stop': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
    }

    def __init__(self, title, parent, max_value, label=None):
        Gtk.Dialog.__init__(self, title, parent)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_size_request(330, 30)
        self.set_resizable(False)
        self.connect('destroy', self.close)
        # self.set_modal(True)
        vbox = Gtk.VBox(spacing=5)
        vbox.set_border_width(5)
        self.get_content_area().add(vbox)
        #
        frame1 = Gtk.Frame()
        vbox.pack_start(frame1, True, True, 0)
        table = Gtk.Table(2, 2, False)
        frame1.add(table)
        #
        self.label = Gtk.Label()
        table.attach(self.label, 0, 2, 0, 1,
                     xpadding=5,
                     ypadding=5,
                     xoptions=Gtk.AttachOptions.SHRINK,
                     yoptions=Gtk.AttachOptions.EXPAND)
        if label is not None:
            self.label.set_label(label)
        #
        self.progressbar = Gtk.ProgressBar()
        self.progressbar.set_size_request(300, 0)
        table.attach(self.progressbar, 0, 1, 1, 2,
                     xpadding=5,
                     ypadding=5,
                     xoptions=Gtk.AttachOptions.SHRINK,
                     yoptions=Gtk.AttachOptions.EXPAND)
        button_stop = Gtk.Button()
        button_stop.set_size_request(40, 40)
        button_stop.set_image(
            Gtk.Image.new_from_stock(Gtk.STOCK_STOP, Gtk.IconSize.BUTTON))
        button_stop.connect('clicked', self.on_button_stop_clicked)
        table.attach(button_stop, 1, 2, 1, 2,
                     xpadding=5,
                     ypadding=5,
                     xoptions=Gtk.AttachOptions.SHRINK)
        self.stop = False
        self.show_all()
        self.max_value = max_value
        self.value = 0.0

    def get_stop(self):
        return self.stop

    def on_button_stop_clicked(self, widget):
        self.stop = True
        self.emit('i-want-stop')

    def set_todo_label(self, widget, todo_label):
        if len(todo_label) > 35:
            text = '...'+todo_label[-32:]
        else:
            text = todo_label
        self.label.set_label(text)

    def set_value(self, value):
        if value >= 0 and value <= self.max_value:
            self.value = value
            fraction = self.value/self.max_value
            self.progressbar.set_fraction(fraction)
            if self.value == self.max_value:
                self.hide()

    def close(self, widget=None):
        self.destroy()

    def increase(self, *args):
        self.value += 1.0
        fraction = self.value/self.max_value
        self.progressbar.set_fraction(fraction)
        if self.value == self.max_value:
            self.hide()

    def decrease(self):
        self.value -= 1.0
        fraction = self.value/self.max_value
        self.progressbar.set_fraction(fraction)

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
