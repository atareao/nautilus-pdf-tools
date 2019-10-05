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


class PageOptions():
    def __init__(self, rotation_angle=0.0, flip_horizontal=False,
                 flip_vertical=False, image_x=0, image_y=0, image_zoom=1.0,
                 image_file=None, text_text=None, text_color=None,
                 text_font='Ubuntu', text_size=12, text_x=0, text_y=0):
        self.rotation_angle = rotation_angle
        self.flip_horizontal = flip_horizontal
        self.flip_vertical = flip_vertical

        self.image_x = image_x
        self.image_y = image_y
        self.image_zoom = image_zoom
        self.image_file = image_file

        self.text_text = text_text
        self.text_color = text_color
        text_font = ' '.join(text_font.split(' ')[:-1])
        self.text_font = text_font
        self.text_size = text_size
        self.text_x = text_x
        self.text_y = text_y

    def __str__(self):
        text  = 'Rotation_angle: {}\n'
        text += 'Flip horizontal: {}\n'
        text += 'Flip vertical: {}\n'
        text += '--- Image ---\n'
        text += 'Image: {}\n'
        text += 'x: {}\n'
        text += 'y: {}\n'
        text += 'zoom: {}\n'
        text += '--- Text ---\n'
        text += 'Text: {}\n'
        text += 'x: {}\n'
        text += 'y: {}\n'
        text += 'font: {}\n'
        text += 'size: {}\n'
        text += 'color: {}\n'
        text = text.format(self.rotation_angle, self.flip_horizontal,
                    self.flip_vertical, self.image_file, self.image_x,
                    self.image_y, self.image_zoom, self.text_text, self.text_x,
                    self.text_y, self.text_font, self.text_size,
                     self.text_color)
        return text

