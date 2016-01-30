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
from PIL import Image
import os
import comun
from comun import _
from comun import TOP, MIDLE, BOTTOM, LEFT, CENTER, RIGHT, MIMETYPES_IMAGE

class WatermarkDialog(Gtk.Dialog):
	def __init__(self,filename=None):
		Gtk.Dialog.__init__(self,_('Watermark'),None,Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT,Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL))
		self.set_size_request(500, 140)
		self.set_resizable(False)
		self.set_icon_from_file(comun.ICON)
		self.connect('destroy', self.close_application)
		#
		vbox0 = Gtk.VBox(spacing = 5)
		vbox0.set_border_width(5)
		self.get_content_area().add(vbox0)
		#
		notebook = Gtk.Notebook()
		vbox0.add(notebook)
		#
		frame = Gtk.Frame()
		notebook.append_page(frame,tab_label = Gtk.Label(_('Watermark')))
		#
		table = Gtk.Table(rows = 6, columns = 2, homogeneous = False)
		table.set_border_width(5)
		table.set_col_spacings(5)
		table.set_row_spacings(5)
		frame.add(table)
		#
		frame1 = Gtk.Frame()
		table.attach(frame1,0,1,0,1, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
		self.scrolledwindow1 = Gtk.ScrolledWindow()
		self.scrolledwindow1.set_size_request(320,320)
		frame1.add(self.scrolledwindow1)
		#
		self.viewport1 = MiniView()
		self.scrolledwindow1.add(self.viewport1)
		#
		frame2 = Gtk.Frame()
		table.attach(frame2,1,2,0,1, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
		scrolledwindow2 = Gtk.ScrolledWindow()
		scrolledwindow2.set_size_request(320,320)
		frame2.add(scrolledwindow2)
		#
		self.viewport2 = MiniView()
		scrolledwindow2.add(self.viewport2)
		#
		self.scale=100
		
		#
		vertical_options = Gtk.ListStore(str,int)
		vertical_options.append([_('Top'),TOP])
		vertical_options.append([_('Middle'),MIDLE])
		vertical_options.append([_('Bottom'),BOTTOM])
		#
		horizontal_options = Gtk.ListStore(str,int)
		horizontal_options.append([_('Left'),LEFT])
		horizontal_options.append([_('Center'),CENTER])
		horizontal_options.append([_('Right'),RIGHT])
		#
		self.rbutton0  = Gtk.CheckButton(_('Overwrite original file?'))
		table.attach(self.rbutton0,0,2,1,2, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		vbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
		table.attach(vbox,0,2,2,3, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		label = Gtk.Label(_('Watermark')+':')
		label.set_alignment(0, 0.5)
		vbox.pack_start(label,False,False,0)
		self.entry = Gtk.Entry()
		self.entry.set_width_chars(10)
		self.entry.set_sensitive(False)
		vbox.pack_start(self.entry,True,True,0)
		button = Gtk.Button(_('Choose File'))
		button.connect('clicked',self.on_button_clicked)
		vbox.pack_start(button,False,False,0)
		#
		label = Gtk.Label(_('Horizontal position')+':')
		label.set_alignment(0, 0.5)
		table.attach(label,0,1,3,4, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.horizontal = Gtk.ComboBox.new_with_model_and_entry(horizontal_options)
		self.horizontal.set_entry_text_column(0)
		self.horizontal.set_active(0)
		self.horizontal.connect('changed', self.on_value_changed)
		table.attach(self.horizontal,1,2,3,4, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		label = Gtk.Label(_('Vertical position')+':')
		label.set_alignment(0, 0.5)
		table.attach(label,0,1,4,5, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.vertical = Gtk.ComboBox.new_with_model_and_entry(vertical_options)
		self.vertical.set_entry_text_column(0)
		self.vertical.set_active(0)
		self.vertical.connect('changed', self.on_value_changed)
		table.attach(self.vertical,1,2,4,5, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)		
		#
		label = Gtk.Label(_('Horizontal margin')+':')
		label.set_alignment(0, 0.5)
		table.attach(label,0,1,5,6, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.horizontal_margin = Gtk.Entry()
		self.horizontal_margin.set_text('0')
		table.attach(self.horizontal_margin,1,2,5,6, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		label = Gtk.Label(_('Vertical margin')+':')
		label.set_alignment(0, 0.5)
		table.attach(label,0,1,6,7, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.vertical_margin = Gtk.Entry()
		self.vertical_margin.set_text('0')
		table.attach(self.vertical_margin,1,2,6,7, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		label = Gtk.Label(_('Watermark width')+':')
		label.set_alignment(0, 0.5)
		table.attach(label,0,1,7,8, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.watermark_height = Gtk.Entry()
		self.watermark_height.set_text('0')
		table.attach(self.watermark_height,1,2,7,8, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		label = Gtk.Label(_('Watermark height')+':')
		label.set_alignment(0, 0.5)
		table.attach(label,0,1,8,9, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.watermark_width = Gtk.Entry()
		self.watermark_width.set_text('0')
		table.attach(self.watermark_width,1,2,8,9, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)

		
		self.show_all()
		if filename != None:
			uri = "file://" + filename
			document = Poppler.Document.new_from_file(uri, None)
			if document.get_n_pages() > 0:
				self.viewport1.set_page(document.get_page(0))
				self.viewport2.set_page(document.get_page(0))
	
	def on_value_changed(self,widget):
		self.update_watermark()
		
	def get_image_filename(self):
		return self.entry.get_text()
		
	def get_horizontal_option(self):
		tree_iter = self.horizontal.get_active_iter()
		if tree_iter != None:
			model = self.horizontal.get_model()
			return model[tree_iter][1]
		return 0

	def get_vertical_option(self):
		tree_iter = self.vertical.get_active_iter()
		if tree_iter != None:
			model = self.vertical.get_model()
			return model[tree_iter][1]
		return 0
		
	def update_preview_cb(self,file_chooser, preview):
		filename = file_chooser.get_preview_filename()
		try:
			pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(filename, 128, 128)
			preview.set_from_pixbuf(pixbuf)
			have_preview = True
		except:
			have_preview = False
		file_chooser.set_preview_widget_active(have_preview)
		return
		
	def on_button_clicked(self,button):
		dialog = Gtk.FileChooserDialog(_('Select one image'),
										self,
									   Gtk.FileChooserAction.OPEN,
									   (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
										Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
		dialog.set_default_response(Gtk.ResponseType.OK)
		dialog.set_select_multiple(False)
		dialog.set_current_folder(os.getenv('HOME'))		
		for aMimetype in MIMETYPES_IMAGE.keys():
			filter = Gtk.FileFilter()
			filter.set_name(aMimetype)
			for mime_type in MIMETYPES_IMAGE[aMimetype]['mimetypes']:
				filter.add_mime_type(mime_type)
			for pattern in MIMETYPES_IMAGE[aMimetype]['patterns']:
				filter.add_pattern(pattern)
			dialog.add_filter(filter)		
		preview = Gtk.Image()
		response = dialog.run()
		if response == Gtk.ResponseType.OK:			
			self.entry.set_text(dialog.get_filename())
		dialog.destroy()
		####
		self.update_watermark()

	def update_watermark(self):
		file_watermark = self.entry.get_text()
		im = Image.open(file_watermark)
		width,height = im.size
		self.watermark_height.set_text(str(height))
		self.watermark_width.set_text(str(width))
		print(im.size) # (width,height) tuple
		if file_watermark and os.path.exists(file_watermark):
			self.viewport2.set_image(file_watermark)
			self.viewport2.set_image_position_vertical(self.get_vertical_option())
			self.viewport2.set_image_position_horizontal(self.get_horizontal_option())

	def close_application(self,widget):
		self.hide()			

if __name__ == '__main__':
	dialog = WatermarkDialog()
	dialog.run()
