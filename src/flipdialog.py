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
from gi.repository import Gtk
from gi.repository import Poppler
from miniview import MiniView
import math
import comun
from comun import _

class FlipDialog(Gtk.Dialog):
	def __init__(self,title,filename=None):
		Gtk.Dialog.__init__(self,title,None,Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT,Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL))
		self.set_default_size(800,400)
		self.set_resizable(True)
		self.set_icon_from_file(comun.ICON)
		self.connect('destroy', self.close)
		#
		vbox = Gtk.VBox(spacing = 5)
		vbox.set_border_width(5)
		self.get_content_area().add(vbox)
		#
		frame = Gtk.Frame()
		vbox.pack_start(frame,True,True,0)
		#
		table = Gtk.Table(rows = 2, columns = 3, homogeneous = False)
		table.set_border_width(5)
		table.set_col_spacings(5)
		table.set_row_spacings(5)
		frame.add(table)		
		#
		frame1 = Gtk.Frame()
		table.attach(frame1,0,1,0,1, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
		self.scrolledwindow1 = Gtk.ScrolledWindow()
		self.scrolledwindow1.set_size_request(420,420)
		self.connect('key-release-event',self.on_key_release_event)		
		frame1.add(self.scrolledwindow1)
		#
		self.viewport1 = MiniView()
		self.scrolledwindow1.add(self.viewport1)
		#
		frame2 = Gtk.Frame()
		table.attach(frame2,1,2,0,1, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
		scrolledwindow2 = Gtk.ScrolledWindow()
		scrolledwindow2.set_size_request(420,420)
		self.connect('key-release-event',self.on_key_release_event)
		frame2.add(scrolledwindow2)
		#
		self.viewport2 = MiniView()
		scrolledwindow2.add(self.viewport2)
		#
		self.scale=100
		#
		#
		self.rbutton0  = Gtk.CheckButton(_('Overwrite original file?'))
		table.attach(self.rbutton0,0,2,1,2, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)		
		#
		table.attach(Gtk.Label(_('Flip vertical')),0,1,2,3, xoptions = Gtk.AttachOptions.SHRINK, yoptions = Gtk.AttachOptions.SHRINK)		
		self.switch1 = Gtk.Switch()
		self.switch1.set_name('switch1')
		self.switch1.connect("notify::active", self.slider_on_value_changed)		
		hbox1 = Gtk.HBox()
		hbox1.pack_start(self.switch1,0,0,0)
		table.attach(hbox1,1,2,2,3, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)		
		#
		table.attach(Gtk.Label(_('Flip horizontal')),0,1,3,4, xoptions = Gtk.AttachOptions.SHRINK, yoptions = Gtk.AttachOptions.SHRINK)		
		self.switch2 = Gtk.Switch()
		self.switch2.set_name('switch2')
		self.switch2.connect("notify::active", self.slider_on_value_changed)
		hbox2 = Gtk.HBox()
		hbox2.pack_start(self.switch2,0,0,0)
		table.attach(hbox2,1,2,3,4, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)		
		#
		table.attach(Gtk.Label(_('Rotate')),0,1,4,5, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)		
		table1 = Gtk.Table(rows = 1, columns = 4, homogeneous = False)
		table1.set_border_width(5)
		table1.set_col_spacings(5)
		table1.set_row_spacings(5)
		table.attach(table1,1,2,4,5, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)		
		self.rbutton1 = Gtk.RadioButton.new_with_label_from_widget(None,'0')
		self.rbutton1.set_name('0')
		self.rbutton1.connect("notify::active", self.slider_on_value_changed)
		table1.attach(self.rbutton1,0,1,0,1, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
		self.rbutton2 = Gtk.RadioButton.new_with_label_from_widget(self.rbutton1,'90')		
		self.rbutton2.set_name('90')
		self.rbutton2.connect("notify::active", self.slider_on_value_changed)
		table1.attach(self.rbutton2,1,2,0,1, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
		self.rbutton3 = Gtk.RadioButton.new_with_label_from_widget(self.rbutton1,'180')
		self.rbutton3.set_name('180')
		self.rbutton3.connect("notify::active", self.slider_on_value_changed)
		table1.attach(self.rbutton3,2,3,0,1, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
		self.rbutton4 = Gtk.RadioButton.new_with_label_from_widget(self.rbutton1,'270')
		self.rbutton4.set_name('270')
		self.rbutton4.connect("notify::active", self.slider_on_value_changed)
		table1.attach(self.rbutton4,3,4,0,1, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
		#
		if filename != None:
			uri = "file://" + filename
			document = Poppler.Document.new_from_file(uri, None)
			if document.get_n_pages() > 0:
				self.viewport1.set_page(document.get_page(0))
				self.viewport2.set_page(document.get_page(0))
		#
		print(1)
		self.show_all()
		#
	def slider_on_value_changed(self,widget,calue):
		print(widget.get_name())
		if widget.get_name() == 'switch1':
			self.viewport2.set_flip_vertical(self.switch1.get_active())
		elif widget.get_name() == 'switch2':
			self.viewport2.set_flip_horizontal(self.switch2.get_active())
		elif widget.get_name() == '0':
			self.viewport2.set_rotation_angle(0.0)
		elif widget.get_name() == '90':
			self.viewport2.set_rotation_angle(1.0)
		elif widget.get_name() == '180':
			self.viewport2.set_rotation_angle(2.0)
		elif widget.get_name() == '270':
			self.viewport2.set_rotation_angle(3.0)
		
	def on_key_release_event(self,widget,event):
		print((event.keyval))
		if event.keyval == 65451 or event.keyval == 43:
			self.scale=self.scale*1.1
		elif event.keyval == 65453 or event.keyval == 45:
			self.scale=self.scale*.9
		elif event.keyval == 65456 or event.keyval == 48:
			factor_w = float(self.scrolledwindow1.get_allocation().width)/float(self.pixbuf1.get_width())
			factor_h = float(self.scrolledwindow1.get_allocation().height)/float(self.pixbuf1.get_height())
			if factor_w < factor_h:
				factor = factor_w
			else:
				factor = factor_h
			self.scale = int(factor*100)
			w=int(self.pixbuf1.get_width()*factor)
			h=int(self.pixbuf1.get_height()*factor)
			#
			self.image1.set_from_pixbuf(self.pixbuf1.scale_simple(w,h,GdkPixbuf.InterpType.BILINEAR))
			self.image2.set_from_pixbuf(self.pixbuf2.scale_simple(w,h,GdkPixbuf.InterpType.BILINEAR))		
		elif event.keyval == 65457 or event.keyval == 49:
			self.scale = 100
		if self.image1:
			w=int(self.pixbuf1.get_width()*self.scale/100)
			h=int(self.pixbuf1.get_height()*self.scale/100)
			#
			self.image1.set_from_pixbuf(self.pixbuf1.scale_simple(w,h,GdkPixbuf.InterpType.BILINEAR))
			self.image2.set_from_pixbuf(self.pixbuf2.scale_simple(w,h,GdkPixbuf.InterpType.BILINEAR))

	def close(self,widget):
		self.destroy()
		
if __name__ == '__main__':
	dialog = FlipDialog('Test')
	dialog.run()
