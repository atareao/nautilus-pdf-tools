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

from threading import Thread
from idleobject import IdleObject
from gi.repository import GObject


class DoitInBackground(IdleObject, Thread):
    __gsignals__ = {
        'todo': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (str,)),
        'done': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (str,)),
        'interrupted': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
        'finished': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
        }

    def __init__(self, maker, elements):
        IdleObject.__init__(self)
        Thread.__init__(self)
        self.maker = maker
        self.elements = elements
        self.daemon = True
        self.stop = False

    def stop_it(self, executor):
        self.stop = True

    def run(self):
        print(2)
        if len(self.elements) > 0:
            self.stop = False
            for an_element in self.elements:
                self.emit('todo', str(an_element))
                print(an_element)
                ret = self.maker(an_element)
                self.emit('done', str(an_element))
                if self.stop is True:
                    self.emit('interrupted')
                    break
        self.emit('finished')


class DoitInBackgroundWithArgs(IdleObject, Thread):
    __gsignals__ = {
        'todo': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (str,)),
        'done': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (str,)),
        'interrupted': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
        'finished': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
        }

    def __init__(self, maker, elements, *args):
        IdleObject.__init__(self)
        Thread.__init__(self)
        self.maker = maker
        self.elements = elements
        self.args = args
        self.daemon = True
        self.stop = False

    def stop_it(self, executor):
        self.stop = True

    def run(self):
        print(2)
        if len(self.elements) > 0:
            self.stop = False
            for an_element in self.elements:
                self.emit('todo', str(an_element))
                ret = self.maker(an_element, *self.args)
                self.emit('done', str(an_element))
                if self.stop is True:
                    self.emit('interrupted')
                    break
        self.emit('finished')


class DoitInBackgroundOnlyOne(IdleObject, Thread):
    __gsignals__ = {
        'todo': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (str,)),
        'done': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (str,)),
        'interrupted': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
        'finished': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
        }

    def __init__(self, maker, *args):
        IdleObject.__init__(self)
        Thread.__init__(self)
        self.maker = maker
        self.args = args
        print(args)
        self.daemon = True
        self.stop = False

    def stop_it(self, executor):
        self.stop = True

    def run(self):
        print(2)
        self.emit('todo', '')
        self.maker(*self.args)
        self.emit('done', '')
        self.emit('finished')


if __name__ == '__main__':
    import time

    def maker(element):
        print(element)
        return True

    elements = range(1, 100)
    dib = DoitInBackground(maker, elements)
    dib.start()
    time.sleep(2)
    exit(0)
