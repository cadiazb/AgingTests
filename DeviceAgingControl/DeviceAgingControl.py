#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject
import sys
import subprocess, time, serial

class PeristalticPump:
  
    def __init__(self):
	self.FlowRate = 0
	self.Period = 1
	self.TimeON = 0.5
	self.Status = 'Idle'
	
class WastePump:
  
    def __init__(self):
	self.FlowRate = 0
	self.Period = 1
	self.TimeON = 0.5
	self.Status = 'Idle'
	
class BathStatus:
  
    def __init__(self):
	self.CurrentTemperature = subprocess.check_output("sudo GetTemperature", shell=True)
	
    def GetTemperature(self):
	self.CurrentTemperature = subprocess.check_output("sudo GetTemperature", shell=True)
	
class Thermostat:
  
    def __init__(self, gtkWindow):
	self.TemperatureSetPoint = 20
	self.ActualTemperature = 25
	self.FlowRateSetPoint = 1
	self.ActualFlowRate = 1
	self.Power = False
	self.ManualPower = gtkWindow.wg.ThermostatManualPower_checkbutton.get_active()
	
	#Create timer to update system
	GObject.timeout_add_seconds(5, self.ThermostatUpdate)
	
	#Create serial port communication
	self.SerialPort = serial.Serial(port='/dev/ttyUSB0', baudrate = 19200, timeout = 2)
	self.SerialPort.isOpen()
	self.ThermostatUpdate()
	
    def __del__(self):
	self.SerialPort.close()
	print 'Serial port closed'
	
    def SetTemperature(self, newSetPoint):
	self.SerialPort.write('SS ' + str(newSetPoint) + '\r')
	time.sleep(0.1)
	print 'Set temperature function'
	self.ThermostatUpdate()
	
    def ThermostatUpdate(self):
	#Get actual temperature
	self.SerialPort.write('RT\r')
	time.sleep(0.1)
	self.ActualTemperature = self.SerialPort.readline()
	
	#Get set point from thermostat
	self.SerialPort.write('RS\r')
	time.sleep(0.1)
	self.TemperatureSetPoint = self.SerialPort.readline()
	return True
	
class DataLogger:
  
    def __init__(self):
	self.StartLogging = False
	self.SaveFolder = '/home/pi/Documents'
	self.AutoFileName = True
	self.FileName = 'AgingTest_20160425'
	
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
	
	
	#Create Peristaltic pump object
	self.pPump = PeristalticPump()
	self.wg.peristalticPeriodEntry.props.text = str(self.pPump.Period)
	self.wg.peristalticTimeOnEntry.props.text = str(self.pPump.TimeON)
	self.wg.peristalticFlowEntry.props.text = str(self.pPump.FlowRate)
	
	#Create waste pump object
	self.wPump = PeristalticPump()
	self.wg.wastePumpPeriodEntry.props.text = str(self.wPump.Period)
	self.wg.wastePumpTimeOnEntry.props.text = str(self.wPump.TimeON)
	
	#Create bath status object
	self.agingBath = BathStatus()
	
	#Create Thermostat object
	self.thermo = Thermostat(self)
	self.wg.thermostatTempEntry.props.text = str(self.thermo.TemperatureSetPoint)
	self.wg.thermostatFlowEntry.props.text = str(self.thermo.FlowRateSetPoint)
	self.wg.ThermostatManualPower_checkbutton.connect("toggled", self.ThermostatManualPower_callback)
	self.wg.thermostatTempEntry.connect("activate", self.ThermostatTempEntry_callback, self.wg.thermostatTempEntry)
	
	#Create data logger object
	self.dLogger = DataLogger()
	#print(dir(self.wg.dataLogChooseFolder.props))
	self.dLogger.AutoFileName = self.wg.dataLogAutoName_checkbutton.get_active()
	self.wg.dataLogChooseFolder.set_filename(self.dLogger.SaveFolder)
	
	  #connections
	self.wg.dataLogAutoName_checkbutton.connect("toggled", self.AutoFileNameCheckButton_callback)
	self.wg.dataLogPower_button.connect("notify::active", self.DataLogPower_button_callback)
	self.wg.dataLogChooseFolder.connect("selection-changed", self.DataLogChooseFolder_callback)
	
	#Create timer to update system
	GObject.timeout_add_seconds(0.1, self.WindowUpdate)
	
    #Define general use methods
    def is_number(self, s):
	try:
	    float(s)
	    return True
	except ValueError:
	    return False

    #Define callbacks for thermostat module
    def ThermostatManualPower_callback(self, button):
	self.thermo.ManualPower = button.get_active()
	self.wg.ThermostatManualPower_button.props.visible = button.get_active()
	
    def ThermostatTempEntry_callback(self, widget, entry):
	tmpText = entry.get_text()
	if self.is_number(tmpText):
	    if (float(tmpText) >= 20 and float(tmpText) <= 150):
		self.thermo.SetTemperature(float(tmpText))
	self.wg.thermostatTempEntry.props.text = str(self.thermo.TemperatureSetPoint)
	    
    #Define callbacks for data logging module
    def DataLogPower_button_callback(self, switch, gparam):
	if (switch.get_active()):
	  self.dLogger.FileName = 'AgingTest_' + time.strftime("%Y%m%d_%H%M%S")
	  print self.dLogger.FileName
	self.dLogger.StartLogging = switch.get_active()
	
    def AutoFileNameCheckButton_callback(self, button):
	self.dLogger.AutoFileName = button.get_active()
	self.wg.dataLogFileNameEntry.props.visible = not button.get_active()
	
    def DataLogChooseFolder_callback(self, button):
	self.dLogger.SaveFolder =  self.wg.dataLogChooseFolder.get_filename()
	    
	  
    #Function to periodically update window
    def WindowUpdate(self):
	self.agingBath.GetTemperature()
	self.wg.BathTemperatureLabel.props.label = self.agingBath.CurrentTemperature[0:4] + ' C'
	#self.wg.thermostatTempEntry.props.text = str(self.thermo.TemperatureSetPoint)
	self.wg.thermostatTempLabel.props.label = str(self.thermo.ActualTemperature)
	self.wg.thermostatFlowLabel.props.label = str(self.thermo.ActualFlowRate) + ' L/min'
	self.wg.ThermostatManualPower_button.props.visible = self.thermo.ManualPower
	self.wg.peristalticStateLabel.props.label = self.pPump.Status
	self.wg.wastePumpStateLabel.props.label = self.wPump.Status
	self.wg.dataLogPower_button.set_active(self.dLogger.StartLogging)
	self.wg.dataLogFileNameEntry.props.visible = not self.dLogger.AutoFileName
	return True

if __name__ == "__main__":
    try:
        win = AgingSystemControl()
	Gtk.main()
    except KeyboardInterrupt:
        pass

