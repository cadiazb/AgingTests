#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class HellowWorldGTK:

    def __init__(self):
        self.gladefile = "DeviceAgingControl.glade" 
        self.glade = Gtk.Builder()
        self.glade.add_from_file(self.gladefile)
        self.glade.connect_signals(self)
        self.glade.get_object("ControlPanel").show_all()

    def on_MainWindow_delete_event(self, widget, event):
        Gtk.main_quit()

if __name__ == "__main__":
    try:
        a = HellowWorldGTK()
        Gtk.main()
    except KeyboardInterrupt:
        pass