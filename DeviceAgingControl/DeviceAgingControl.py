#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import sys

class PeristalticPump:
  
    def _initt__(self):
	self.FlowRate = 0
	self.Period = 1
	self.TimeON = 0.5
  
class AgingSystemControl:

    def __init__(self):
        self.gladefile = "DeviceAgingControl.glade" 
        self.glade = Gtk.Builder()
        self.glade.add_from_file(self.gladefile)
        self.glade.connect_signals(self)
        self.glade.get_object("ControlPanel").show_all()
	self.glade.get_object("ControlPanel").connect("delete-event", Gtk.main_quit)
	
	#Create Peristaltic pump
	pPump = PeristalticPump()

if __name__ == "__main__":
    try:
        win = AgingSystemControl()
	Gtk.main()
    except KeyboardInterrupt:
        pass

