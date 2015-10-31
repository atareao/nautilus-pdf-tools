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
from gi.repository import Nautilus as FileManager
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import Poppler
import tempfile
import cairo
import math
import shutil
import os
import sys
import subprocess
import shlex
from urllib import unquote_plus
from PIL import Image
import mimetypes

if __file__.startswith('/usr/share/nautilus-python/extensions') or \
	os.getcwd().startswith('/usr/share/nautilus-python/extensions'):
	sys.path.insert(1, '/opt/extras.ubuntu.com/nautilus-pdf-tools/share/nautilus-pdf-tools')

from miniview import MiniView
from paginatedialog import PaginateDialog
from textmarkdialog import TextmarkDialog
from watermarkdialog import WatermarkDialog
from flipdialog import FlipDialog
from joinpdfsdialog import JoinPdfsDialog
from selectpagesrotatedialog import SelectPagesRotateDialog
from combinedialog import CombineDialog
from resizedialog import ResizeDialog
from createpdffromImagesdialog import CreatePDFFromImagesDialog
from selectpagesdialog import SelectPagesDialog
from convertdialog import ConvertDialog
import comun
from comun import _
from comun import SEPARATOR, RESOLUTION, MMTOPIXEL, MMTOPDF, MMTOPNG, TOP, MIDLE, BOTTOM, LEFT, CENTER, RIGHT, ROTATE_000, ROTATE_090, ROTATE_180, ROTATE_270
from comun import  EXTENSIONS_TO, EXTENSIONS_FROM, MIMETYPES_TO, MIMETYPES_FROM, MIMETYPES_PDF, MIMETYPES_PNG, MIMETYPES_IMAGE

mimetypes.init()
	
########################################################################

def create_temp_file():
	return tempfile.mkstemp(prefix = 'tmp_filemanager_pdf_tools_')[1]

def dialog_save_as_image(title, original_file):
	dialog = Gtk.FileChooserDialog(title,
									None,
								   Gtk.FileChooserAction.SAVE,
								   (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
									Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
	dialog.set_default_response(Gtk.ResponseType.OK)
	dialog.set_current_folder(os.path.dirname(original_file))
	dialog.set_filename(original_file)
	for aMimetype in MIMETYPES_IMAGE.keys():
		print(aMimetype,MIMETYPES_IMAGE[aMimetype])
		filter = Gtk.FileFilter()
		filter.set_name(aMimetype)
		for mime_type in MIMETYPES_IMAGE[aMimetype]['mimetypes']:
			filter.add_mime_type(mime_type)
		for pattern in MIMETYPES_IMAGE[aMimetype]['patterns']:
			filter.add_pattern(pattern)
		dialog.add_filter(filter)
	if dialog.run() == Gtk.ResponseType.OK:
		filename = dialog.get_filename()
	else:
		filename = None
	dialog.destroy()
	return filename


def dialog_save_as(title, original_file):
	dialog = Gtk.FileChooserDialog(title,
									None,
								   Gtk.FileChooserAction.SAVE,
								   (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
									Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
	dialog.set_default_response(Gtk.ResponseType.OK)
	dialog.set_current_folder(os.path.dirname(original_file))
	dialog.set_filename(original_file)
	for mimetype in MIMETYPES_PDF:
		filter = Gtk.FileFilter()
		filter.set_name(_('Pdf files'))
		filter.add_mime_type(mimetype)
		for pattern in mimetypes.guess_all_extensions(mimetype):
			filter.add_pattern('*'+pattern)
		dialog.add_filter(filter)
	if dialog.run() == Gtk.ResponseType.OK:
		filename = dialog.get_filename()
		if not filename.endswith('.pdf'):
			filename += '.pdf'
	else:
		filename = None
	dialog.destroy()
	return filename

def dialog_save_as_text(title, original_file):
	dialog = Gtk.FileChooserDialog(title,
									None,
								   Gtk.FileChooserAction.SAVE,
								   (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
									Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
	dialog.set_default_response(Gtk.ResponseType.OK)
	dialog.set_current_folder(os.path.dirname(original_file))
	dialog.set_filename(original_file)
	filter = Gtk.FileFilter()
	filter.set_name(_('Text file'))
	filter.add_mime_type('text/plain')
	filter.add_pattern('*.txt')
	dialog.add_filter(filter)
	if dialog.run() == Gtk.ResponseType.OK:
		filename = dialog.get_filename()
		if not filename.endswith('.txt'):
			filename += '.txt'
	else:
		filename = None
	dialog.destroy()
	return filename

		
########################################################################

def create_image_surface_from_file(filename):
	pixbuf = GdkPixbuf.Pixbuf.new_from_file(filename)
	return create_image_surface_from_pixbuf(pixbuf)

def create_image_surface_from_pixbuf(pixbuf):
	surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, pixbuf.get_width(),pixbuf.get_height())
	context = cairo.Context(surface)
	Gdk.cairo_set_source_pixbuf(context, pixbuf,0,0)
	context.paint()
	return surface


def split_pdf(file_in):
	document = Poppler.Document.new_from_file('file://' + file_in, None)
	number_of_pages = document.get_n_pages()
	if number_of_pages>1:
		file_out,ext = os.path.splitext(file_in)		
		for i in range(0,number_of_pages):
			file_out_i = '%s_%s%s'%(file_out,i+1,ext)
			pdfsurface = cairo.PDFSurface(file_out_i,200,200)
			context = cairo.Context(pdfsurface)
			current_page = document.get_page(i)
			context.save()
			pdf_width,pdf_height = current_page.get_size()
			pdfsurface.set_size(pdf_width,pdf_height)
			current_page.render(context)
			context.restore()				
			context.show_page()		
			pdfsurface.flush()
			pdfsurface.finish()

def convert_pdf_to_png(file_in):
	print(file_in)
	document = Poppler.Document.new_from_file('file://' + file_in, None)
	number_of_pages = document.get_n_pages()
	if number_of_pages>0:
		file_out,ext = os.path.splitext(file_in)		
		for i in range(0,number_of_pages):
			current_page = document.get_page(i)
			pdf_width,pdf_height = current_page.get_size()
			file_out_i = '%s_%s%s'%(file_out,i+1,'.png')
			pngsurface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(pdf_width*MMTOPNG), int(pdf_height*MMTOPNG))
			context = cairo.Context(pngsurface)
			context.save()
			context.scale(1.0*MMTOPNG,1.0*MMTOPNG)
			current_page.render(context)
			context.restore()
			pngsurface.flush()
			pngsurface.write_to_png(file_out_i)
			pngsurface.finish()
	
def create_from_images(file_out,images,width=1189,height=1682,margin=0):
	temp_pdf = create_temp_file()
	temp_png = None
	pdfsurface = cairo.PDFSurface(temp_pdf,width,height)
	context = cairo.Context(pdfsurface)
	for image in images:
		basename,extension = os.path.splitext(image)
		if mimetypes.guess_type(image)[0] in MIMETYPES_PNG:
			imagesurface = cairo.ImageSurface.create_from_png(image)	
		else:
			imagesurface = create_image_surface_from_file(image)		
		imagesurface_width = imagesurface.get_width()
		imagesurface_height = imagesurface.get_height()			
		scale_x = (imagesurface_width/MMTOPIXEL)/width
		scale_y = (imagesurface_height/MMTOPIXEL)/height
		if scale_x > scale_y:
			scale = scale_x		
		else:
			scale = scale_y
		if margin == 1:
			scale = scale * 1.05
		elif margin == 2:
			scale = scale * 1.15
		x = (width - imagesurface_width/MMTOPIXEL/scale)/2
		y = (height - imagesurface_height/MMTOPIXEL/scale)/2		
		context.save()
		context.translate(x,y)
		context.scale(1.0/MMTOPIXEL/scale,1.0/MMTOPIXEL/scale)
		context.set_source_surface(imagesurface)
		context.paint()
		context.restore()
		context.show_page()				
	pdfsurface.flush()
	pdfsurface.finish()
	shutil.copy(temp_pdf, file_out)
	os.remove(temp_pdf)

		
def reduce_pdf(file_in):
	file_out = get_output_filename(file_in,'reduced')
	rutine = 'ghostscript -q  -dNOPAUSE -dBATCH -dSAFER \
	-sDEVICE=pdfwrite \
	-dCompatibilityLevel=1.4 \
	-dPDFSETTINGS=/screen \
	-dEmbedAllFonts=true \
	-dSubsetFonts=true \
	-dDownsampleColorImages=true \
	-dColorImageResolution=100 \
	-dColorImageDownsampleType=/Bicubic \
	-dColorImageResolution=72 \
	-dGrayImageDownsampleType=/Bicubic \
	-dGrayImageResolution=72 \
	-dMonoImageDownsampleType=/Bicubic \
	-dMonoImageResolution=72 \
	-sOutputFile=%s %s'%(file_out,file_in)
	args = shlex.split(rutine)
	p = subprocess.Popen(args,stdout = subprocess.PIPE)
	out, err = p.communicate()

def resize(file_in,file_out,width=1189,height=1682):
	document = Poppler.Document.new_from_file('file://' + file_in, None)
	number_of_pages = document.get_n_pages()
	width = float(width)
	height = float(height)
	horizontal = (width > height)
	pdfsurface = cairo.PDFSurface(file_out,width,height)
	context = cairo.Context(pdfsurface)
	for i in range(0,number_of_pages):
		current_page = document.get_page(i)
		widthi,heighti = current_page.get_size()
		horizontali = (widthi > heighti)
		if horizontal != horizontali:
			sw = width/heighti
			sh = height/widthi
			if sw<sh:
				scale = sw
			else:
				scale = sh
			context.save()
			mtr = cairo.Matrix()
			mtr.rotate(ROTATE_270/180.0*math.pi)
			context.transform(mtr)
			context.scale(scale,scale)
			context.translate(-widthi,0.0)			
			current_page.render(context)			
			context.restore()				
		else:
			sw = width/widthi
			sh = height/heighti
			if sw<sh:
				scale = sw
			else:
				scale = sh
			context.save()
			context.scale(scale,scale)
			current_page.render(context)			
			context.restore()
		context.show_page()			
	pdfsurface.flush()
	pdfsurface.finish()


def combine(file_in,file_out,filas=1,columnas=2,width=297,height=210,margen=0.0,byrows=True ):
	document = Poppler.Document.new_from_file('file://' + file_in, None)
	number_of_pages = document.get_n_pages()
	filas = float(filas)
	columnas = float(columnas)
	width = float(width)
	height = float(height)
	margen = float(margen)
	pdfsurface = cairo.PDFSurface(file_out,width,height)
	context = cairo.Context(pdfsurface)
	for i in range(0,number_of_pages,int(filas*columnas)):
		page = i-1
		for fila in range(0,int(filas)):
			for columna in range(0,int(columnas)):			
				page += 1		
				if byrows:
					aux_combine(page,document,fila,columna,width,height,filas,columnas,margen,context)
				else:
					aux_combine(page,document,columna,fila,width,height,filas,columnas,margen,context)
		context.show_page()
	pdfsurface.flush()
	pdfsurface.finish()

def aux_combine(page,document,fila,columna,width,height,filas,columnas,margen,context):		
	if page < document.get_n_pages():
		current_page = document.get_page(page)
		pdf_width,pdf_height = current_page.get_size()
		sw = (width-(filas+1.0)*margen)/pdf_width/columnas
		sh = (height-(columnas+1.0)*margen)/pdf_height/filas
		if sw<sh:
			scale = sw
		else:
			scale = sh
		x = float(columna) * width /columnas + (float(columna)+1.0)*margen
		y = (filas - float(fila) - 1.0) * height /float(filas) + (float(fila)+1.0)*margen
		context.save()		
		context.translate(x,y)
		context.scale(scale,scale)
		
		current_page.render(context)
		context.restore()		
	else:
		return 

def remove_ranges(file_in,file_out,ranges):
	pages =[]
	for rang in ranges:
		if len(rang)>1:
			for i in range(rang[0],rang[1]+1):
				if not i in pages:
					pages.append(i)
		else:
			if not rang[0] in pages:
				pages.append(rang[0])	
	document = Poppler.Document.new_from_file('file://' + file_in, None)
	number_of_pages = document.get_n_pages()
	temp_pdf = create_temp_file()
	pdfsurface = cairo.PDFSurface(temp_pdf,200,200)
	context = cairo.Context(pdfsurface)
	for i in range(0,number_of_pages):
		if i+1 not in pages:
			current_page = document.get_page(i)
			context.save()
			pdf_width,pdf_height = current_page.get_size()
			pdfsurface.set_size(pdf_width,pdf_height)
			current_page.render(context)
			context.restore()				
			context.show_page()		
	pdfsurface.flush()
	pdfsurface.finish()
	shutil.copy(temp_pdf, file_out)
	os.remove(temp_pdf)
	
def rotate_ranges_in_pdf(file_in,file_out,degrees,ranges,flip_horizontal=False,flip_vertical=False):
	pages =[]
	for rang in ranges:
		if len(rang)>1:
			for i in range(rang[0],rang[1]+1):
				if not i in pages:
					pages.append(i)
		else:
			if not rang[0] in pages:
				pages.append(rang[0])
	document = Poppler.Document.new_from_file('file://' + file_in, None)
	if document.get_n_pages() > 0:
		temp_pdf = create_temp_file()
		pdfsurface = cairo.PDFSurface(temp_pdf,200,200)
		context = cairo.Context(pdfsurface)
		for i in range(0,document.get_n_pages()):
			current_page = document.get_page(i)
			if i+1 in pages:
				if degrees == ROTATE_000 or degrees == ROTATE_180:
					pdf_width,pdf_height = current_page.get_size()
				else:
					pdf_height,pdf_width = current_page.get_size()
				pdfsurface.set_size(pdf_width,pdf_height)
				context.save()
				mtr = cairo.Matrix()
				mtr.rotate(degrees/180.0*math.pi)
				context.transform(mtr)			
				if degrees == ROTATE_090:
						context.translate(0.0,-pdf_width)
						print(degrees)
				elif degrees == ROTATE_180:
						context.translate(-pdf_width,-pdf_height)
				elif degrees == ROTATE_270:
						context.translate(-pdf_height,0.0)			
				if flip_vertical:
					context.scale(1,-1)
					if degrees == ROTATE_000 or degrees == ROTATE_180:
						context.translate(0,-pdf_height)
					else:
						context.translate(0,-pdf_width)
				if flip_horizontal:
					context.scale(-1,1)
					if degrees == ROTATE_000 or degrees == ROTATE_180:
						context.translate(-pdf_width,0)
					else:
						context.translate(-pdf_height,0)
				current_page.render(context)			
				context.restore()
			else:
				context.save()
				pdf_width,pdf_height = current_page.get_size()
				pdfsurface.set_size(pdf_width,pdf_height)
				current_page.render(context)
				context.restore()				
			context.show_page()		
		pdfsurface.flush()
		pdfsurface.finish()
		shutil.copy(temp_pdf, file_out)
		os.remove(temp_pdf)

def convert2png(file_in,file_out):
	im=Image.open(file_in)
	im.save(file_out)
	
def rotate_and_flip_pages(file_pdf_in,degrees=ROTATE_090,flip_vertical=False,flip_horizontal=False,overwrite=False):
	document = Poppler.Document.new_from_file('file://' + file_pdf_in, None)
	if document.get_n_pages() > 0:
		temp_pdf = create_temp_file()
		pdfsurface = cairo.PDFSurface(temp_pdf,200,200)
		context = cairo.Context(pdfsurface)
		for i in range(0,document.get_n_pages()):
			current_page = document.get_page(i)
			if degrees == ROTATE_000 or degrees == ROTATE_180:
				pdf_width,pdf_height = current_page.get_size()
			else:
				pdf_height,pdf_width = current_page.get_size()
			pdfsurface.set_size(pdf_width,pdf_height)
			context.save()
			mtr = cairo.Matrix()
			mtr.rotate(degrees/180.0*math.pi)
			context.transform(mtr)			
			if degrees == ROTATE_090:
					context.translate(0.0,-pdf_width)
					print(degrees)
			elif degrees == ROTATE_180:
					context.translate(-pdf_width,-pdf_height)
			elif degrees == ROTATE_270:
					context.translate(-pdf_height,0.0)			
			if flip_vertical:
				context.scale(1,-1)
				if degrees == ROTATE_000 or degrees == ROTATE_180:
					context.translate(0,-pdf_height)
				else:
					context.translate(0,-pdf_width)
			if flip_horizontal:
				context.scale(-1,1)
				if degrees == ROTATE_000 or degrees == ROTATE_180:
					context.translate(-pdf_width,0)
				else:
					context.translate(-pdf_height,0)
			current_page.render(context)			
			context.restore()
			context.show_page()		
		pdfsurface.flush()
		pdfsurface.finish()
		if overwrite:
			shutil.copy(temp_pdf, file_pdf_in)
		else:			
			shutil.copy(temp_pdf, get_output_filename(file_pdf_in,'rotated_'+str(int(degrees))))
		os.remove(temp_pdf)

def add_paginate_all_pages(file_pdf_in,color,font,size,horizontal_position,vertical_position,overwrite=False):
	document = Poppler.Document.new_from_file('file://' + file_pdf_in, None)
	number_of_pages = document.get_n_pages()
	if document.get_n_pages() > 0:
		temp_pdf = create_temp_file()
		pdfsurface = cairo.PDFSurface(temp_pdf,200,200)
		context = cairo.Context(pdfsurface)
		for i in range(0,number_of_pages):
			current_page = document.get_page(i)
			text = '%s/%s'%(i+1,number_of_pages)
			pdf_width,pdf_height = current_page.get_size()
			pdfsurface.set_size(pdf_width,pdf_height)
			context.save()
			current_page.render(context)
			context.restore()			
			context.save()
			context.set_source_rgba(*color)
			context.select_font_face(font)
			context.set_font_size(size)
			xbearing, ybearing, font_width, font_height, xadvance, yadvance = context.text_extents(text)
			if vertical_position == TOP:
				y = font_height
			elif vertical_position == MIDLE:
				y = (pdf_height + font_height)/2					
			elif vertical_position == BOTTOM:
				y = pdf_height
			if horizontal_position == LEFT:
				x = 0
			elif horizontal_position == CENTER:
				x = (pdf_width - font_width)/2
			elif horizontal_position == RIGHT:
				x = pdf_width - font_width	+ xbearing
			context.move_to(x,y)
			context.translate(x,y)
			context.show_text(text)
			context.restore()
			context.show_page()		
		pdfsurface.flush()
		pdfsurface.finish()
		if overwrite:
			shutil.copy(temp_pdf, file_pdf_in)
		else:			
			shutil.copy(temp_pdf, get_output_filename(file_pdf_in,'paginated'))
		os.remove(temp_pdf)

def add_textmark_to_all_pages(file_pdf_in,text,color,font,size,horizontal_position,vertical_position,overwrite=False):
	document = Poppler.Document.new_from_file('file://' + file_pdf_in, None)
	if document.get_n_pages() > 0:
		temp_pdf = create_temp_file()
		pdfsurface = cairo.PDFSurface(temp_pdf,200,200)
		context = cairo.Context(pdfsurface)
		for i in range(0,document.get_n_pages()):
			current_page = document.get_page(i)
			pdf_width,pdf_height = current_page.get_size()
			pdfsurface.set_size(pdf_width,pdf_height)
			context.save()
			current_page.render(context)
			context.restore()			
			context.save()
			context.set_source_rgba(*color)
			context.select_font_face(font)
			context.set_font_size(size)
			xbearing, ybearing, font_width, font_height, xadvance, yadvance = context.text_extents(text)
			if vertical_position == TOP:
				y = font_height
			elif vertical_position == MIDLE:
				y = (pdf_height + font_height)/2					
			elif vertical_position == BOTTOM:
				y = pdf_height
			if horizontal_position == LEFT:
				x = 0
			elif horizontal_position == CENTER:
				x = (pdf_width - font_width)/2
			elif horizontal_position == RIGHT:
				x = pdf_width - font_width	+ xbearing
			context.move_to(x,y)
			context.translate(x,y)
			context.show_text(text)
			context.restore()
			context.show_page()		
		pdfsurface.flush()
		pdfsurface.finish()
		if overwrite:
			shutil.copy(temp_pdf, file_pdf_in)
		else:			
			shutil.copy(temp_pdf, get_output_filename(file_pdf_in,'textmarked'))
		os.remove(temp_pdf)

def add_watermark_to_all_pages(file_pdf_in,file_image_in,horizontal_position,vertical_position,overwrite=False):
	document = Poppler.Document.new_from_file('file://' + file_pdf_in, None)
	if document.get_n_pages() > 0:
		temp_pdf = create_temp_file()
		watermark_surface = create_image_surface_from_file(file_image_in)
		watermark_width = watermark_surface.get_width()
		watermark_height = watermark_surface.get_height()	
		pdfsurface = cairo.PDFSurface(temp_pdf,200,200)
		context = cairo.Context(pdfsurface)
		for i in range(0,document.get_n_pages()):
			current_page = document.get_page(i)
			pdf_width,pdf_height = current_page.get_size()
			pdfsurface.set_size(pdf_width,pdf_height)
			context.save()
			current_page.render(context)
			context.restore()
			context.save()
			if vertical_position == TOP:
				y = 0
			elif vertical_position == MIDLE:
				y = (pdf_height - watermark_height/MMTOPIXEL)/2					
			elif vertical_position == BOTTOM:
				y = pdf_height - watermark_height/MMTOPIXEL
			if horizontal_position == LEFT:
				x = 0
			elif horizontal_position == CENTER:
				x = (pdf_width - watermark_width/MMTOPIXEL)/2
			elif horizontal_position == RIGHT:
				x = pdf_width - watermark_width/MMTOPIXEL	
			context.translate(x,y)
			context.scale(1.0/MMTOPIXEL,1.0/MMTOPIXEL)
			context.set_source_surface(watermark_surface)
			context.paint()
			context.restore()
			context.show_page()		
		pdfsurface.flush()
		pdfsurface.finish()
		if overwrite:
			shutil.copy(temp_pdf, file_pdf_in)
		else:			
			shutil.copy(temp_pdf, get_output_filename(file_pdf_in,'watermarked'))
		os.remove(temp_pdf)

def extract_ranges(file_in,file_out,ranges):
	pages =[]
	for rang in ranges:
		if len(rang)>1:
			for i in range(rang[0],rang[1]+1):
				if not i in pages:
					pages.append(i)
		else:
			if not rang[0] in pages:
				pages.append(rang[0])	
	document = Poppler.Document.new_from_file('file://' + file_in, None)
	number_of_pages = document.get_n_pages()
	temp_pdf = create_temp_file()
	pdfsurface = cairo.PDFSurface(temp_pdf,200,200)
	context = cairo.Context(pdfsurface)
	for i in range(0,number_of_pages):
		if i+1 in pages:
			current_page = document.get_page(i)
			context.save()
			pdf_width,pdf_height = current_page.get_size()
			pdfsurface.set_size(pdf_width,pdf_height)
			current_page.render(context)
			context.restore()				
			context.show_page()		
	pdfsurface.flush()
	pdfsurface.finish()
	shutil.copy(temp_pdf, file_out)
	os.remove(temp_pdf)


def rotate_some_pages_in_pdf(file_in,file_out,degrees,first_page,last_page):
	document = Poppler.Document.new_from_file('file://' + file_in, None)
	if document.get_n_pages() > 0:
		temp_pdf = create_temp_file()
		pdfsurface = cairo.PDFSurface(temp_pdf,200,200)
		context = cairo.Context(pdfsurface)
		for i in range(0,document.get_n_pages()):
			current_page = document.get_page(i)
			if i>=first_page and i<=last_page:
				if degrees == ROTATE_000 or degrees == ROTATE_180:
					pdf_width,pdf_height = current_page.get_size()
				else:
					pdf_height,pdf_width = current_page.get_size()
				pdfsurface.set_size(pdf_width,pdf_height)
				context.save()
				mtr = cairo.Matrix()
				mtr.rotate(degrees/180.0*math.pi)
				context.transform(mtr)			
				if degrees == ROTATE_090:
						context.translate(0.0,-pdf_width)
						print(degrees)
				elif degrees == ROTATE_180:
						context.translate(-pdf_width,-pdf_height)
				elif degrees == ROTATE_270:
						context.translate(-pdf_height,0.0)			
				if flip_vertical:
					context.scale(1,-1)
					if degrees == ROTATE_000 or degrees == ROTATE_180:
						context.translate(0,-pdf_height)
					else:
						context.translate(0,-pdf_width)
				if flip_horizontal:
					context.scale(-1,1)
					if degrees == ROTATE_000 or degrees == ROTATE_180:
						context.translate(-pdf_width,0)
					else:
						context.translate(-pdf_height,0)
				current_page.render(context)			
				context.restore()
			else:
				context.save()
				pdf_width,pdf_height = current_page.get_size()
				pdfsurface.set_size(pdf_width,pdf_height)
				current_page.render(context)
				context.restore()				
			context.show_page()		
		pdfsurface.flush()
		pdfsurface.finish()
		shutil.copy(temp_pdf, file_out)
		os.remove(temp_pdf)

def extract_pages(file_in,file_out,first_page,last_page):
	document = Poppler.Document.new_from_file('file://' + file_in, None)
	number_of_pages = document.get_n_pages()
	if first_page > number_of_pages-1:
		first_page = number_of_pages-1
	if last_page < first_page:
		last_page = first_page
	if last_page > number_of_pages-1:
		last_page = number_of_pages-1
	temp_pdf = create_temp_file()
	pdfsurface = cairo.PDFSurface(temp_pdf,200,200)
	context = cairo.Context(pdfsurface)
	for i in range(first_page,last_page+1):
		current_page = document.get_page(i)
		context.save()
		pdf_width,pdf_height = current_page.get_size()
		pdfsurface.set_size(pdf_width,pdf_height)
		current_page.render(context)
		context.restore()				
		context.show_page()		
	pdfsurface.flush()
	pdfsurface.finish()
	shutil.copy(temp_pdf, file_out)
	os.remove(temp_pdf)

def remove_pages(file_in,file_out,first_page,last_page):
	document = Poppler.Document.new_from_file('file://' + file_in, None)
	number_of_pages = document.get_n_pages()
	if first_page > number_of_pages-1:
		first_page = number_of_pages-1
	if last_page < first_page:
		last_page = first_page
	if last_page > number_of_pages-1:
		last_page = number_of_pages-1
	temp_pdf = create_temp_file()
	pdfsurface = cairo.PDFSurface(temp_pdf,200,200)
	context = cairo.Context(pdfsurface)
	for i in range(0,number_of_pages):
		if i not in list(range(first_page,last_page+1)):
			current_page = document.get_page(i)
			context.save()
			pdf_width,pdf_height = current_page.get_size()
			pdfsurface.set_size(pdf_width,pdf_height)
			current_page.render(context)
			context.restore()				
			context.show_page()		
	pdfsurface.flush()
	pdfsurface.finish()
	shutil.copy(temp_pdf, file_out)
	os.remove(temp_pdf)


def join_files(files,file_out):
	temp_pdf = create_temp_file()
	pdfsurface = cairo.PDFSurface(temp_pdf,200,200)
	context = cairo.Context(pdfsurface)
	for file_in in files:
		document = Poppler.Document.new_from_file('file://' + file_in, None)
		number_of_pages = document.get_n_pages()		
		for i in range(0,number_of_pages):
			current_page = document.get_page(i)
			context.save()
			pdf_width,pdf_height = current_page.get_size()
			pdfsurface.set_size(pdf_width,pdf_height)
			current_page.render(context)
			context.restore()				
			context.show_page()		
	pdfsurface.flush()
	pdfsurface.finish()
	shutil.copy(temp_pdf, file_out)
	os.remove(temp_pdf)
	
def get_output_filename(file_in,modificator):
	if os.path.exists(file_in) and os.path.isfile(file_in):
		head, tail = os.path.split(file_in)
		root, ext = os.path.splitext(tail)
		file_out = os.path.join(head,root+'_'+modificator+ext)
		return file_out
	return None

def get_files(files_in):
	files = []
	for file_in in files_in:
		print(file_in)
		file_in = unquote_plus(file_in.get_uri()[7:])
		if os.path.isfile(file_in):
			files.append(file_in)
	if len(files)>0:
		return files
	return None

def get_num(chain):
	try:
		chain = chain.strip() # removing spaces
		return int(float(chain))
	except:
		return None

def get_ranges(chain):
	ranges = []
	if chain.find(',') > -1:
		for part in chain.split(','):
			if part.find('-') > -1:
				parts = part.split('-')
				if len(parts) > 1:
					f = get_num(parts[0])
					t = get_num(parts[1])
					if f != None and t !=None:
						ranges.append([f,t])
			else:
				el = get_num(part)
				if el:
					ranges.append([el])
	elif chain.find('-') > -1:
		parts = chain.split('-')
		if len(parts) > 1:
			f = get_num(parts[0])
			t = get_num(parts[1])
			if f != None and t !=None:
				ranges.append([f,t])
	else:
		el = get_num(chain)
		if el:
			ranges.append([el])
	return ranges

"""
Tools to manipulate pdf
"""	
class PdfToolsMenuProvider(GObject.GObject, FileManager.MenuProvider):
	"""Implements the 'Replace in Filenames' extension to the File Manager right-click menu"""

	def __init__(self):
		"""File Manager crashes if a plugin doesn't implement the __init__ method"""
		pass

	def all_files_are_pdf(self,items):
		for item in items:
			fileName, fileExtension = os.path.splitext(unquote_plus(item.get_uri()[7:]))
			if fileExtension != '.pdf':
				return False
		return True

	def all_files_are_images(self,items):
		for item in items:
			fileName, fileExtension = os.path.splitext(unquote_plus(item.get_uri()[7:]))
			if fileExtension.lower() in EXTENSIONS_FROM:
				return True
		return False

	def resize_pdf_pages(self,menu,selected):
		files = get_files(selected)
		if files:
			file_in = files[0]
			cd = ResizeDialog(_('Resize pages'))
			if cd.run() == Gtk.ResponseType.ACCEPT:
				size = cd.get_size()
				if cd.is_vertical():
					width = size[0]
					height = size[1]
				else:
					width = size[1]
					height = size[0]
				cd.destroy()
				file_out = dialog_save_as(_('Select file to save new file'), file_in)
				if file_out:
					resize(file_in,file_out,width,height)
			cd.destroy()

	def convert_pdf_file_to_png(self,menu,selected):
		files = get_files(selected)
		for afile in files:
			print(afile)
			convert_pdf_to_png(afile)
				
	def combine_pdf_pages(self,menu,selected):
		files = get_files(selected)
		if files:
			file_in = files[0]
			cd = CombineDialog(_('Combine pages'))
			if cd.run() == Gtk.ResponseType.ACCEPT:
				size = cd.get_size()
				if cd.is_vertical():
					width = size[0]
					height = size[1]
				else:
					width = size[1]
					height = size[0]
				filas = cd.get_rows()
				columnas = cd.get_columns()
				byrows = cd.is_sort_by_rows()
				margen = cd.get_margin()
				cd.destroy()
				file_out = dialog_save_as(_('Select file to save new file'), file_in)
				if file_out:
					combine(file_in,file_out,filas,columnas,width,height,margen,byrows )
			cd.destroy()
			
	def create_pdf_from_images(self,menu,selected):
		files = get_files(selected)
		if files:
			cpfi = CreatePDFFromImagesDialog(_('Create pdf from images'),files)
			if cpfi.run() == Gtk.ResponseType.ACCEPT:
				cpfi.hide()
				files = cpfi.get_png_files()
				if cpfi.is_vertical():
					width,height = cpfi.get_size()
				else:
					height,width = cpfi.get_size()				
				margin = cpfi.get_margin()
				cpfi.destroy()
				file0 = os.path.join(os.path.dirname(files[0]),'converted_from_images.pdf')
				file_out = dialog_save_as(_('Select file to save new file'), file0)
				if file_out:
					create_from_images(file_out,files,width,height,margin)
			cpfi.destroy()
			
	def join_pdf_files(self,menu,selected):
		files = get_files(selected)
		if files:
			jpd = JoinPdfsDialog(_('Join pdf files'),files)
			if jpd.run() == Gtk.ResponseType.ACCEPT:
				files = jpd.get_pdf_files()
				jpd.destroy()
				if len(files)>0:
					file0 = os.path.join(os.path.dirname(files[0]),'joined_files.pdf')
					file_out = dialog_save_as(_('Select file to save new file'), file0)
					if file_out:
						join_files(files,file_out)
			jpd.destroy()

	def paginate(self,*args):
		menu_item, sel_items = args
		files = get_files(sel_items)
		if len(files)>0:
			file0 = files[0]
			wd = PaginateDialog(file0)
			if wd.run() == Gtk.ResponseType.ACCEPT:
				wd.hide()
				color =wd.get_color()
				font = wd.get_font()
				size =wd.get_size()
				hoption = wd.get_horizontal_option()
				voption = wd.get_vertical_option()
				for afile in files:
					add_paginate_all_pages(afile,color,font,size,hoption,voption,wd.rbutton0.get_active())
			wd.destroy()
	def reduce(self, *args):
		menu_item, sel_items = args
		files = get_files(sel_items)
		for afile in files:			
			reduce_pdf(afile)
			
	def textmark(self,*args):
		menu_item, sel_items = args
		files = get_files(sel_items)
		if len(files)>0:
			file0 = files[0]
			wd = TextmarkDialog(file0)
			if wd.run() == Gtk.ResponseType.ACCEPT:
				wd.hide()
				text = wd.get_text()
				color =wd.get_color()
				font = wd.get_font()
				size =wd.get_size()
				hoption = wd.get_horizontal_option()
				voption = wd.get_vertical_option()
				for afile in files:
					add_textmark_to_all_pages(afile,text,color,font,size,hoption,voption,wd.rbutton0.get_active())
			wd.destroy()

	def watermark(self,*args):
		menu_item, sel_items = args
		files = get_files(sel_items)
		if len(files)>0:
			file0 = files[0]
			wd = WatermarkDialog(file0)
			if wd.run() == Gtk.ResponseType.ACCEPT:
				wd.hide()
				hoption = wd.get_horizontal_option()
				voption = wd.get_vertical_option()
				for afile in files:
					print('------------------------------------------------')
					print(afile)
					add_watermark_to_all_pages(afile,wd.get_image_filename(),hoption,voption,wd.rbutton0.get_active())
					print('------------------------------------------------')
			wd.destroy()

	def rotate_or_flip(self,*args):
		menu_item, sel_items = args
		files = get_files(sel_items)
		if len(files)>0:
			file0 = files[0]
			fd = FlipDialog(_('Rotate files'),file0)
			degrees = 0
			if fd.run() == Gtk.ResponseType.ACCEPT:
				fd.hide()
				for afile in files:
					if fd.rbutton1.get_active():
						rotate_and_flip_pages(afile,ROTATE_000, fd.switch1.get_active(),fd.switch2.get_active(),fd.rbutton0.get_active())					
					elif fd.rbutton2.get_active():
						rotate_and_flip_pages(afile,ROTATE_090, fd.switch1.get_active(),fd.switch2.get_active(),fd.rbutton0.get_active())
					elif fd.rbutton3.get_active():
						rotate_and_flip_pages(afile,ROTATE_180, fd.switch1.get_active(),fd.switch2.get_active(),fd.rbutton0.get_active())
					elif fd.rbutton4.get_active():
						rotate_and_flip_pages(afile,ROTATE_270, fd.switch1.get_active(),fd.switch2.get_active(),fd.rbutton0.get_active())
			fd.destroy()
			
	def rotate_some_pages(self,menu,selected):
		files = get_files(selected)
		if files:
			file0 = files[0]
			document = Poppler.Document.new_from_file('file://' + file0, None)
			last_page = document.get_n_pages()
			spd = SelectPagesRotateDialog(_('Rotate some pages'),last_page)
			if spd.run() == Gtk.ResponseType.ACCEPT:			
				ranges = get_ranges(spd.entry1.get_text())				
				if spd.rbutton1.get_active():
					degrees = 270
				elif spd.rbutton2.get_active():
					degrees = 90
				else:
					degrees = 180
				spd.destroy()
				if len(ranges)>0:
					file_out = dialog_save_as(_('Select file to save new file'), file0)
					if file_out:
						rotate_ranges_in_pdf(file0,file_out,degrees,ranges)
			else:
				spd.destroy()
				
	def about(self,menu,selected):
		ad=Gtk.AboutDialog()
		ad.set_name(comun.APP)
		ad.set_icon_name(comun.ICON)
		ad.set_version(comun.VERSION)
		ad.set_copyright('Copyrignt (c) 2012-2015\nLorenzo Carbonell')
		ad.set_comments(_('Tools to manage pdf files'))
		ad.set_license(''+
		'This program is free software: you can redistribute it and/or modify it\n'+
		'under the terms of the GNU General Public License as published by the\n'+
		'Free Software Foundation, either version 3 of the License, or (at your option)\n'+
		'any later version.\n\n'+
		'This program is distributed in the hope that it will be useful, but\n'+
		'WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY\n'+
		'or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for\n'+
		'more details.\n\n'+
		'You should have received a copy of the GNU General Public License along with\n'+
		'this program.  If not, see <http://www.gnu.org/licenses/>.')
		ad.set_website('http://www.atareao.es')
		ad.set_website_label('http://www.atareao.es')
		ad.set_authors(['Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>'])
		ad.set_documenters(['Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>'])
		ad.set_program_name(comun.APP)
		ad.set_logo_icon_name(comun.ICON)
		ad.run()
		ad.destroy()		
		
	def remove_some_pages(self,menu,selected):
		files = get_files(selected)
		if files:
			file0 = files[0]
			document = Poppler.Document.new_from_file('file://' + file0, None)
			last_page = document.get_n_pages()
			spd = SelectPagesDialog(_('Remove some pages'),last_page)
			if spd.run() == Gtk.ResponseType.ACCEPT:
				ranges = get_ranges(spd.entry1.get_text())
				spd.destroy()
				if len(ranges)>0:
					file_out = dialog_save_as(_('Select file to save new file'), file0)
					if file_out:
						remove_ranges(file0,file_out,ranges)
			else:
				spd.destroy()

	def split_pdf_files(self,menu,selected):
		files = get_files(selected)
		if files:
			file0 = files[0]
			split_pdf(file0)
		
	def extract_some_pages(self,menu,selected):
		files = get_files(selected)
		if files:
			file0 = files[0]
			document = Poppler.Document.new_from_file('file://' + file0, None)
			last_page = document.get_n_pages()
			spd = SelectPagesDialog(_('Extract some pages'),last_page)
			if spd.run() == Gtk.ResponseType.ACCEPT:
				ranges = get_ranges(spd.entry1.get_text())
				spd.destroy()
				if len(ranges)>0:				
					file_out = dialog_save_as(_('Select file to save extracted pages'), file0)
					if file_out:
						extract_ranges(file0,file_out,ranges)
			else:
				spd.destroy()
				
	def extract_text(self,menu,selected):
		files = get_files(selected)
		if files:
			file0 = files[0]
			file_out = dialog_save_as_text(_('Select file to save extracted text'), file0)
			if file_out:
				extract_text(file0,file_out)
		
	def get_file_items(self, window, sel_items):
		"""Adds the 'Replace in Filenames' menu item to the File Manager right-click menu,
		   connects its 'activate' signal to the 'run' method passing the selected Directory/File"""
		if self.all_files_are_pdf(sel_items):
			top_menuitem = FileManager.MenuItem(name='PdfToolsMenuProvider::Gtk-pdf-tools',
									 label=_('Pdf Tools'),
									 tip=_('Tools to manipulate pdf files'),
									 icon='Gtk-find-and-replace')
			#
			submenu = FileManager.Menu()
			top_menuitem.set_submenu(submenu)
			sub_menus = []
			items = [
			('01',_('Rotate and flip'),_('rotate_and_flip pdf files'),self.rotate_or_flip),
			('02',_('Watermark'),_('Watermark pdffiles'),self.watermark),
			('03',_('Textmark'),_('Textmark pdf files'),self.textmark),
			('04',_('Paginate'),_('Paginate pdf files'),self.paginate),
			('05',_('Rotate pages'),_('Rotate pages of the document files'),self.rotate_some_pages),
			('06',_('Remove pages'),_('Remove pages of the document files'),self.remove_some_pages),
			('07',_('Extract pages'),_('Extract pages of the document files'),self.extract_some_pages),
			('08',_('Join pdf files'),_('Join pdf files in one document'),self.join_pdf_files),
			('09',_('Split pdf files'),_('Split a pdf in several documents'),self.split_pdf_files),
			('10',_('Combine pdf pages'),_('Combine pdf pages in one page'),self.combine_pdf_pages),
			('11',_('Reduce pdf size'),_('Reduce pdf size'),self.reduce),
			('12',_('Resize pdf pages'),_('Resize pdf pages'),self.resize_pdf_pages),
			('13',_('Convert pdf to png'),_('Convert pdf file to png image'),self.convert_pdf_file_to_png),
			]
			for item in items:
				sub_menuitem = FileManager.MenuItem(name='PdfToolsMenuProvider::Gtk-pdf-tools-'+item[0],
								 label=item[1],tip=item[2])
				sub_menuitem.connect('activate', item[3], sel_items)
				submenu.append_item(sub_menuitem)		
			#		
			sub_menuitem_98 = FileManager.MenuItem(name='PdfToolsMenuProvider::Gtk-None',
									 label=SEPARATOR)
			submenu.append_item(sub_menuitem_98)
			#		
			sub_menuitem_99 = FileManager.MenuItem(name='PdfToolsMenuProvider::Gtk-pdf-tools-99',
									 label=_('About'),
									 tip=_('About'),
									 icon='Gtk-find-and-replace')
			sub_menuitem_99.connect('activate', self.about, sel_items)
			submenu.append_item(sub_menuitem_99)
			#		
			return top_menuitem,
		elif self.all_files_are_images(sel_items):
			top_menuitem = FileManager.MenuItem(name='PdfToolsMenuProvider::Gtk-pdf-tools',
									 label=_('Pdf Tools'),
									 tip=_('Tools to manipulate pdf files'),
									 icon='Gtk-find-and-replace')
			submenu = FileManager.Menu()
			top_menuitem.set_submenu(submenu)
			sub_menus = []
			items = [
			('51',_('Convert to pdf'),_('Convert images to pdf'),self.create_pdf_from_images),
			]
			for item in items:
				sub_menuitem = FileManager.MenuItem(name='PdfToolsMenuProvider::Gtk-pdf-tools-'+item[0],
								 label=item[1],tip=item[2])
				sub_menuitem.connect('activate', item[3], sel_items)
				submenu.append_item(sub_menuitem)		
			#		
			sub_menuitem_98 = FileManager.MenuItem(name='PdfToolsMenuProvider::Gtk-None',
									 label=SEPARATOR)
			submenu.append_item(sub_menuitem_98)
			#		
			sub_menuitem_99 = FileManager.MenuItem(name='PdfToolsMenuProvider::Gtk-pdf-tools-99',
									 label=_('About'),
									 tip=_('About'),
									 icon='Gtk-find-and-replace')
			sub_menuitem_99.connect('activate', self.about, sel_items)
			submenu.append_item(sub_menuitem_99)
			#		
			return top_menuitem,
		return
if __name__ == '__main__':
	'''
	cd = CreatePDFFromImagesDialog('Test')
	cd.run()
	'''
	for extension in EXTENSIONS_TO:
		print(mimetypes.types_map[extension])
	for mimetype in MIMETYPES_FROM:
		print(mimetypes.guess_all_extensions(mimetype))
	for mimetype in MIMETYPES_PDF:
		print(mimetypes.guess_all_extensions(mimetype))
	print(mimetypes.guess_all_extensions('text/plain'))
	from gi.repository import GdkPixbuf
	supported_mimetypes = []
	for aformat in GdkPixbuf.Pixbuf.get_formats():
		print(aformat.get_description(),aformat.get_extensions(), aformat.get_mime_types())
		supported_mimetypes += aformat.get_mime_types()
	print(supported_mimetypes)
	url='/home/lorenzo/Imágenes/2webp_053.png'
	print(mimetypes.guess_type(url)[0])
	print(mimetypes.guess_type(url)[0] in supported_mimetypes)
	print('******************')
	print(MIMETYPES_IMAGE)
	dialog_save_as_image("","")
