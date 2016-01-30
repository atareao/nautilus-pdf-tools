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
import comun
from comun import _

class SelectPagesDialog(Gtk.Dialog):
	def __init__(self, title, last_page):
		Gtk.Dialog.__init__(self,title,None,Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT,Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL))
		self.set_size_request(300, 120)
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
		frame1 = Gtk.Frame()
		notebook.append_page(frame1,tab_label = Gtk.Label(_('Select Pages')))
		#
		table1 = Gtk.Table(rows = 3, columns = 3, homogeneous = False)
		table1.set_border_width(5)
		table1.set_col_spacings(5)
		table1.set_row_spacings(5)
		frame1.add(table1)
		#
		label1 = Gtk.Label(_('Pages')+':')
		label1.set_tooltip_text(_('Type page number and/or page\nranges separated by commas\ncounting from start of the\ndocument ej. 1,4,6-9'))
		label1.set_alignment(0,.5)
		table1.attach(label1,0,1,0,1, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.entry1 = Gtk.Entry()
		self.entry1.set_tooltip_text(_('Type page number and/or page\nranges separated by commas\ncounting from start of the\ndocument ej. 1,4,6-9'))
		table1.attach(self.entry1,1,3,0,1, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.show_all()
	def close_application(self,widget):
		self.hide()

if __name__ == '__main__':
	dialog = SelectPagesDialog('Test',10)
	dialog.run()
