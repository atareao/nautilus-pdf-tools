#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of nautilus-pdf-tools
#
# Copyright (C) 2012-2015 Lorenzo Carbonell
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
#
#
#
if __file__.startswith('/usr/share/nautilus-python/extensions') or \
	os.getcwd().startswith('/usr/share/nautilus-python/extensions'):
	sys.path.insert(1, '/opt/extras.ubuntu.com/nautilus-pdf-tools/share/nautilus-pdf-tools')

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
import cairo

from comun import SEPARATOR, RESOLUTION, MMTOPIXEL, MMTOPDF, MMTOPNG, TOP, MIDLE, BOTTOM, LEFT, CENTER, RIGHT, ROTATE_000, ROTATE_090, ROTATE_180, ROTATE_270

def create_image_surface_from_file(filename):
	pixbuf = GdkPixbuf.Pixbuf.new_from_file(filename)
	return create_image_surface_from_pixbuf(pixbuf)

def create_image_surface_from_pixbuf(pixbuf):
	surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, pixbuf.get_width(),pixbuf.get_height())
	context = cairo.Context(surface)
	Gdk.cairo_set_source_pixbuf(context, pixbuf,0,0)
	context.paint()
	return surface

class MiniView(Gtk.DrawingArea):
	def __init__(self,width=400.0,height=420.00,margin=10.0,border=2.0,force=False):
		Gtk.DrawingArea.__init__(self)
		self.add_events(Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK)
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
		self.image = None
		self.text = None
		self.color = [0,0,0,1]
		self.font = 'Ubuntu'
		self.size = 12
		self.position_vertical = TOP
		self.position_horizontal = LEFT		
		self.connect('draw', self.on_expose, None)
		self.set_size_request(self.width, self.height)
		
	def on_expose(self, widget, cr, data):		
		if self.page:
			if self.rotation_angle == 0.0 or self.rotation_angle == 2.0:
				zw = (self.width-2.0*self.margin)/self.or_width
				zh = (self.height-2.0*self.margin)/self.or_height
				if zw < zh:
					self.zoom = zw
				else:
					self.zoom = zh
				self.page_width = self.or_width*self.zoom
				self.page_height = self.or_height*self.zoom
				self.margin_width = (self.width - self.page_width)/2.0
				self.margin_height = (self.height - self.page_height)/2.0
			else:
				zw = (self.width-2.0*self.margin)/self.or_height
				zh = (self.height-2.0*self.margin)/self.or_width
				if zw < zh:
					self.zoom = zw
				else:
					self.zoom = zh
				self.page_width = self.or_height*self.zoom
				self.page_height = self.or_width*self.zoom
				self.margin_width = (self.width - self.page_width)/2.0
				self.margin_height = (self.height - self.page_height)/2.0				
			self.image_surface = cairo.ImageSurface(cairo.FORMAT_RGB24,int(self.page_width),int(self.page_height)) 
			context = cairo.Context(self.image_surface)
			context.save()
			context.set_source_rgba(1.0, 1.0, 1.0, 1.0)
			context.paint()
			mtr = cairo.Matrix()
			mtr.rotate(self.rotation_angle*math.pi/2.0)
			mtr.scale(self.zoom*RESOLUTION,self.zoom*RESOLUTION)
			context.transform(mtr)
			if self.rotation_angle == 1.0:
					context.translate(0.0,-self.page_width/self.zoom/RESOLUTION)
			elif self.rotation_angle == 2.0:
					context.translate(-self.page_width/self.zoom/RESOLUTION,-self.page_height/self.zoom/RESOLUTION)
			elif self.rotation_angle == 3.0:
					context.translate(-self.page_height/self.zoom/RESOLUTION,0.0)
			self.page.render(context)		
			context.restore()
			if self.image:
				watermark_surface = create_image_surface_from_file(self.image)
				img_height = watermark_surface.get_height()
				img_width = watermark_surface.get_width()
				# scale image and add it
				context.save()				
				print(self.or_width,self.or_height)
				if self.position_vertical == TOP:
					y = 0
				elif self.position_vertical == MIDLE:
					y = (self.or_height - img_height/MMTOPIXEL)/2					
				elif self.position_vertical == BOTTOM:
					y = self.or_height - img_height/MMTOPIXEL
				if self.position_horizontal == LEFT:
					x = 0
				elif self.position_horizontal == CENTER:
					x = (self.or_width - img_width/MMTOPIXEL)/2
				elif self.position_horizontal == RIGHT:
					x = self.or_width - img_width/MMTOPIXEL	
				context.translate(x*self.zoom,y*self.zoom)
				context.scale(self.zoom/MMTOPIXEL,self.zoom/MMTOPIXEL)
				context.set_source_surface(watermark_surface)
				context.paint()
			if self.text:
				context.save()
				context.set_source_rgba(*self.color)
				context.select_font_face(self.font)
				context.set_font_size(self.size)
				xbearing, ybearing, font_width, font_height, xadvance, yadvance = context.text_extents(self.text)
				if self.position_vertical == TOP:
					y = font_height
				elif self.position_vertical == MIDLE:
					y = (self.or_height + font_height)/2					
				elif self.position_vertical == BOTTOM:
					y = self.or_height
				if self.position_horizontal == LEFT:
					x = 0
				elif self.position_horizontal == CENTER:
					x = (self.or_width - font_width)/2
				elif self.position_horizontal == RIGHT:
					x = self.or_width - font_width	+ xbearing
				context.move_to(x*self.zoom,y*self.zoom)
				context.translate(x*self.zoom,y*self.zoom)
				context.scale(self.zoom,self.zoom)
				context.show_text(self.text)
				context.restore()				
		cr.save()		
		cr.set_source_rgba(0.0, 0.0, 0.0, 0.5)
		cr.rectangle(self.margin_width-self.border, self.margin_height-self.border,
		self.page_width+2.0*self.border, self.page_height+2.0*self.border)
		cr.stroke()
		cr.restore()
		#
		if self.flip_vertical:
			cr.scale(1,-1)
			cr.translate(0,-(2*self.margin_height+self.page_height))
		if self.flip_horizontal:
			cr.scale(-1,1)
			cr.translate(-(2*self.margin_width+self.page_width),0)
		if self.page:
			cr.set_source_surface(self.image_surface,self.margin_width,self.margin_height)
			cr.paint()

	def set_page(self, page):
		self.page = page
		self.rotation_angle = 0.0
		self.drawings = []		
		self.or_width, self.or_height = self.page.get_size()
		self.or_width = int(self.or_width*RESOLUTION)
		self.or_height = int(self.or_height*RESOLUTION)
		self.queue_draw()
		
	def set_rotation_angle(self,rotation_angle):
		self.rotation_angle = rotation_angle
		self.queue_draw()
		
	def set_flip_horizontal(self,flip_horizontal):
		self.flip_horizontal = flip_horizontal
		self.queue_draw()
		
	def set_flip_vertical(self,flip_vertical):
		self.flip_vertical = flip_vertical
		self.queue_draw()
		
	def set_image_position_vertical(self,position_vertical):
		self.position_vertical = position_vertical
		self.queue_draw()
		
	def set_image_position_horizontal(self,position_horizontal):
		self.position_horizontal = position_horizontal
		self.queue_draw()
	
	def set_text(self,text):
		self.text = text
		self.queue_draw()

	def set_image(self,image):
		self.image = image
		self.queue_draw()

	def refresh(self):
		self.queue_draw()

