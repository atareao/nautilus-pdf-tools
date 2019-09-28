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
    gi.require_version('Gdk', '3.0')
except Exception as e:
    print(e)
    exit(1)
from gi.repository import Gtk
from gi.repository import Gdk
import cairo
import math
import tools

from comun import RESOLUTION, MMTOPIXEL, TOP,\
    MIDLE, BOTTOM, LEFT, CENTER, RIGHT


class MiniView(Gtk.DrawingArea):

    def __init__(self, width=600.0, height=630.00, margin=10.0, border=1.0,
                 force=False):
        Gtk.DrawingArea.__init__(self)
        self.add_events(
            Gdk.EventMask.POINTER_MOTION_MASK |
            Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.BUTTON_RELEASE_MASK)
        self.height = height
        self.width = width
        self.image_surface = None
        self.margin = margin
        self.border = border
        self.page = None
        self.zoom = 1
        self.rotation_angle = 0.0
        self.flip_horizontal = False
        self.flip_vertical = False
        self.page_width = -1
        self.page_height = -1
        self.margin_width = -1
        self.margin_height = -1
        self.text_margin_width = 0
        self.text_margin_height = 0
        self.image_margin_width = 0
        self.image_margin_height = 0
        self.image_width = 0
        self.image_height = 0
        self.image_zoom = 1.0
        self.image = None
        self.text = None
        self.color = [0, 0, 0, 1]
        self.font = 'Ubuntu'
        self.size = 12
        self.position_vertical = TOP
        self.position_horizontal = LEFT
        self.connect('draw', self.on_expose, None)
        self.set_size_request(self.width, self.height)

    def on_expose(self, widget, cr, data):
        if self.page:
            if self.rotation_angle == 0.0 or self.rotation_angle == 2.0:
                zw = (self.width - 2.0 * self.margin) / self.or_width
                zh = (self.height - 2.0 * self.margin) / self.or_height
                if zw < zh:
                    self.zoom = zw
                else:
                    self.zoom = zh
                self.page_width = self.or_width * self.zoom
                self.page_height = self.or_height * self.zoom
                self.margin_width = (self.width - self.page_width) / 2.0
                self.margin_height = (self.height - self.page_height) / 2.0
            else:
                zw = (self.width - 2.0 * self.margin) / self.or_height
                zh = (self.height - 2.0 * self.margin) / self.or_width
                if zw < zh:
                    self.zoom = zw
                else:
                    self.zoom = zh
                self.page_width = self.or_height * self.zoom
                self.page_height = self.or_width * self.zoom
                self.margin_width = (self.width - self.page_width) / 2.0
                self.margin_height = (self.height - self.page_height) / 2.0
            self.image_surface = cairo.ImageSurface(
                cairo.FORMAT_RGB24,
                int(self.page_width),
                int(self.page_height))
            context = cairo.Context(self.image_surface)
            context.save()
            context.set_source_rgba(1.0, 1.0, 1.0, 1.0)
            context.paint()
            mtr = cairo.Matrix()
            mtr.rotate(self.rotation_angle * math.pi / 2.0)
            mtr.scale(self.zoom * RESOLUTION, self.zoom * RESOLUTION)
            context.transform(mtr)
            if self.rotation_angle == 1.0:
                    context.translate(
                        0.0, -self.page_width / self.zoom / RESOLUTION)
            elif self.rotation_angle == 2.0:
                    context.translate(
                        -self.page_width / self.zoom / RESOLUTION,
                        -self.page_height / self.zoom / RESOLUTION)
            elif self.rotation_angle == 3.0:
                    context.translate(
                        -self.page_height / self.zoom / RESOLUTION, 0.0)
            self.page.render(context)
            context.restore()
            if self.image:
                context.save()
                watermark_surface = tools.create_image_surface_from_file(
                    self.image, self.image_zoom)
                self.image_height = watermark_surface.get_height()
                self.image_width = watermark_surface.get_width()
                print(self.or_width, self.or_height)
                if self.position_vertical == TOP:
                    y = self.image_margin_height
                elif self.position_vertical == MIDLE:
                    y = (self.or_height - self.image_height / MMTOPIXEL) / 2
                elif self.position_vertical == BOTTOM:
                    y = (self.or_height - self.image_height / MMTOPIXEL -
                         self.image_margin_height)
                if self.position_horizontal == LEFT:
                    x = self.image_margin_width
                elif self.position_horizontal == CENTER:
                    x = (self.or_width - self.image_width / MMTOPIXEL) / 2
                elif self.position_horizontal == RIGHT:
                    x = (self.or_width - self.image_width / MMTOPIXEL -
                         self.image_margin_width)
                context.translate(x * self.zoom, y * self.zoom)
                context.scale(self.zoom / MMTOPIXEL, self.zoom / MMTOPIXEL)
                context.set_source_surface(watermark_surface)
                context.paint()
                context.restore()
            if self.text:
                context.save()
                context.set_source_rgba(*self.color)
                context.select_font_face(self.font)
                context.set_font_size(self.size)
                xbearing, _, font_width, font_height, _,\
                    _ = context.text_extents(self.text)
                if self.position_vertical == TOP:
                    y = self.text_margin_height + font_height
                elif self.position_vertical == MIDLE:
                    y = (self.or_height + font_height) / 2
                elif self.position_vertical == BOTTOM:
                    y = self.or_height - self.text_margin_height
                if self.position_horizontal == LEFT:
                    x = self.text_margin_width
                elif self.position_horizontal == CENTER:
                    x = (self.or_width - font_width) / 2
                elif self.position_horizontal == RIGHT:
                    x = (self.or_width - font_width + xbearing -
                         self.text_margin_width)
                context.move_to(x * self.zoom, y * self.zoom)
                context.translate(x * self.zoom, y * self.zoom)
                context.scale(self.zoom, self.zoom)
                context.show_text(self.text)
                context.restore()
        cr.save()
        cr.set_source_rgba(0.0, 0.0, 0.0, 0.5)
        cr.rectangle(self.margin_width - self.border,
                     self.margin_height - self.border,
                     self.page_width + 2.0 * self.border,
                     self.page_height + 2.0 * self.border)
        cr.stroke()
        cr.restore()

        if self.flip_vertical:
            cr.scale(1, -1)
            cr.translate(0, -(2 * self.margin_height + self.page_height))
        if self.flip_horizontal:
            cr.scale(-1, 1)
            cr.translate(-(2 * self.margin_width + self.page_width), 0)
        if self.page:
            cr.set_source_surface(self.image_surface,
                                  self.margin_width,
                                  self.margin_height)
            cr.paint()

    def set_page(self, page, rotation_angle=0, flip_horizontal=False,
            flip_vertical=False):
        self.page = page
        self.drawings = []
        self.or_width, self.or_height = self.page.get_size()
        self.or_width = int(self.or_width * RESOLUTION)
        self.or_height = int(self.or_height * RESOLUTION)
        self.rotation_angle = rotation_angle
        self.flip_horizontal = flip_horizontal
        self.flip_vertical = flip_vertical
        self.queue_draw()

    def set_rotation_angle(self, rotation_angle):
        self.rotation_angle = rotation_angle
        self.queue_draw()

    def set_flip_horizontal(self, flip_horizontal):
        self.flip_horizontal = flip_horizontal
        self.queue_draw()

    def set_flip_vertical(self, flip_vertical):
        self.flip_vertical = flip_vertical
        self.queue_draw()

    def set_image_position_vertical(self, position_vertical):
        self.position_vertical = position_vertical
        self.queue_draw()

    def set_image_position_horizontal(self, position_horizontal):
        self.position_horizontal = position_horizontal
        self.queue_draw()

    def set_text(self, text):
        self.text = text
        self.queue_draw()

    def set_image(self, image):
        self.image = image
        self.queue_draw()

    def refresh(self):
        self.queue_draw()
