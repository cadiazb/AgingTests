#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject
import sys
import subprocess

class PeristalticPump:
  
    def __init__(self):
	self.FlowRate = 0
	self.Period = 1
	self.TimeON = 0.5
	
class BathStatus:
  
    def __init__(self):
	self.CurrentTemperature = subprocess.check_output("sudo GetTemperature", shell=True)
	
    def GetTemperature(self):
	self.CurrentTemperature = subprocess.check_output("sudo GetTemperature", shell=True)
	
class Thermostat:
  
    def __init__(self, gtkWindow):
	self.TemperatureSetPoint = 25
	self.ActualTemperature = 25
	self.FlowRateSetPoint = 1
	self.ActualFlowRate = 1
	self.Power = False
	self.ManualPower = gtkWindow.wg.ThermostatManualPower_checkbutton.get_active()
	
class widgetIDs(object):
  
    def __init__(self, gtkWindow):
	self.ControlPanel = gtkWindow.glade.get_object("ControlPanel")
	
	self.peristalticPeriodEntry = gtkWindow.glade.get_object("peristalticPeriodEntry")
	self.peristalticTimeOnEntry = gtkWindow.glade.get_object("peristalticTimeOnEntry")
	self.peristalticFlowEntry = gtkWindow.glade.get_object("peristalticFlowEntry")
	self.peristalticStateLabel = gtkWindow.glade.get_object("peristalticStateLabel")
	self.peristalticStepTimeLabel = gtkWindow.glade.get_object("peristalticStepTimeLabel")
	
	self.thermostatTempEntry = gtkWindow.glade.get_object("thermostatTempEntry")
	self.thermostatTempLabel = gtkWindow.glade.get_object("thermostatTempLabel")
	self.thermostatFlowEntry = gtkWindow.glade.get_object("thermostatFlowEntry")
	self.thermostatFlowLabel = gtkWindow.glade.get_object("thermostatFlowLabel")
	self.ThermostatManualPower_checkbutton = gtkWindow.glade.get_object("ThermostatManualPower_checkbutton")
	self.ThermostatManualPower_button = gtkWindow.glade.get_object("ThermostatManualPower_button")
	
	self.wastePumpPeriodEntry = gtkWindow.glade.get_object("wastePumpPeriodEntry")
	self.wastePumpTimeOnEntry = gtkWindow.glade.get_object("wastePumpTimeOnEntry")
	self.wastePumpStateLabel = gtkWindow.glade.get_object("wastePumpStateLabel")
	self.wastePumpStepTimeRead = gtkWindow.glade.get_object("wastePumpStepTimeRead")
	
	self.dataLogPower_button = gtkWindow.glade.get_object("dataLogPower_button")
	self.dataLogChooseFolder = gtkWindow.glade.get_object("dataLogChooseFolder")
	self.dataLogAutoName_checkbutton = gtkWindow.glade.get_object("dataLogAutoName_checkbutton")
	self.dataLogFileNameEntry = gtkWindow.glade.get_object("dataLogFileNameEntry")
	
	self.messageLine = gtkWindow.glade.get_object("messageLine")
	self.BathTemperatureLabel = gtkWindow.glade.get_object("BathTemperatureLabel")
	self.MasterPower_button = gtkWindow.glade.get_object("MasterPower_button")
	#self. = gtkWindow.glade.get_object("")
  
class AgingSystemControl:

    def __init__(self):
        self.gladefile = "DeviceAgingControl.glade" 
        self.glade = Gtk.Builder()
        self.glade.add_from_file(self.gladefile)
        self.glade.connect_signals(self)
        
        #Create widget wtrusture
        self.wg = widgetIDs(self)
        self.wg.ControlPanel = self.glade.get_object("ControlPanel")
        self.wg.ControlPanel.show_all()
	self.wg.ControlPanel.connect("delete-event", Gtk.main_quit)
	#print(dir(self.glade.get_object("ThermostatManualPower_button").props))
	
	
	#Create Peristaltic pump object and widgets
	self.pPump = PeristalticPump()
	
	#Create bath status object
	self.agingBath = BathStatus()
	
	#Create Thermostat object
	self.thermo = Thermostat(self)
	self.wg.ThermostatManualPower_button.props.visible = self.thermo.ManualPower
	self.wg.ThermostatManualPower_checkbutton.connect("toggled", self.ThermostatManualPower_callback)
	
	#Create timer to update system
	GObject.timeout_add_seconds(0.1, self.WindowUpdate)

    def ThermostatManualPower_callback(self, button):
	if button.get_active():
	    self.thermo.ManualPower = True
	    self.wg.ThermostatManualPower_button.props.visible = True
	else:
	    self.thermo.ManualPower = False
	    self.wg.ThermostatManualPower_button.props.visible = False
	    
	  
    def WindowUpdate(self):
	self.agingBath.GetTemperature()
	self.wg.BathTemperatureLabel.props.label = self.agingBath.CurrentTemperature[0:4] + ' C'
	return True

if __name__ == "__main__":
    try:
        win = AgingSystemControl()
	Gtk.main()
    except KeyboardInterrupt:
        pass

