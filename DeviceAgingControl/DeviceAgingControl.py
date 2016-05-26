#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gdk
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
	self.Power = False
	self.ManualPower = gtkWindow.wg.ThermostatManualPower_checkbutton.get_active()
	self.StatusCode = 0
	self.StatusMessage = 'System OK'
	
	#Create timer to update system
	GObject.timeout_add_seconds(10, self.ThermostatUpdate)
	
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
	print self.SerialPort.readline()
	self.ThermostatUpdate()
	
    def PowerON(self):
	if (self.Power):
	    self.SerialPort.write('SO 1\r')
	else:
	    self.SerialPort.write('SO 0\r')
	    
	self.SerialPort.readline()
	
    def ThermostatUpdate(self):
	#Get Unit On status
	self.SerialPort.write('RO\r')
	time.sleep(0.04)
	tmpRes = self.SerialPort.read(2)
	self.Power = bool(tmpRes == '1\r')
	
	#Get actual temperature
	self.SerialPort.write('RT\r')
	time.sleep(0.04)
	self.ActualTemperature = self.SerialPort.readline()
	
	#Get set point from thermostat
	self.SerialPort.write('RS\r')
	time.sleep(0.04)
	self.TemperatureSetPoint = self.SerialPort.readline()

	#Get fault status
	self.SerialPort.write('RUFS\r')
	time.sleep(0.04)
	self.StatusCode = self.SerialPort.readline()
	self.FaultStatusMessageUpdate()
	return True
      
    def FaultStatusMessageUpdate(self):
	tmpCodes = [int(i) for i in self.StatusCode.split()]
	tmpBinaryV3 = list(bin(tmpCodes[2]))
	tmpBinaryV3 = [0] * (8-len(tmpBinaryV3)+2) + map(int,tmpBinaryV3[2:])
	if (tmpBinaryV3[7]):
	    self.StatusMessage = 'Code ' + ''.join(str(e) for e in tmpBinaryV3) + ' - Low Level Warning'
	   
	if (tmpBinaryV3[4]):
	    self.StatusMessage = 'Code ' + ''.join(str(e) for e in tmpBinaryV3) + ' - Low Level Fault'
	    
	if (not(tmpBinaryV3[7]) and not(tmpBinaryV3[4])):
	    self.StatusMessage = 'Code ' + ''.join(str(e) for e in tmpBinaryV3) + ' - OK'
	
	
class DataLogger:
  
    def __init__(self):
	self.StartLogging = False
	self.SaveFolder = '/home/pi/Github/AgingTests/Data'
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
	self.ThermostatManualPower_checkbutton = gtkWindow.glade.get_object("ThermostatManualPower_checkbutton")
	self.ThermostatManualPower_button = gtkWindow.glade.get_object("ThermostatManualPower_button")
	self.thermostatPowerStatus_label = gtkWindow.glade.get_object("thermostatPowerStatus_label")
	self.thermostatFaultStatus_label = gtkWindow.glade.get_object("thermostatFaultStatus_label")
	
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
	self.wg.ThermostatManualPower_checkbutton.connect("toggled", self.ThermostatManualPower_callback)
	self.wg.thermostatTempEntry.connect("activate", self.ThermostatTempEntry_callback, self.wg.thermostatTempEntry)
	self.wg.ThermostatManualPower_button.connect("notify::active", self.ThermostatManualPower_button_callback)
	
	#Create data logger object
	self.dLogger = DataLogger()
	#print(dir(self.wg.dataLogChooseFolder.props))
	self.dLogger.AutoFileName = self.wg.dataLogAutoName_checkbutton.get_active()
	self.wg.dataLogChooseFolder.set_filename(self.dLogger.SaveFolder)
	#Create timer to log every minute
	GObject.timeout_add_seconds(60, self.LogData)
	
	  #connections
	self.wg.dataLogAutoName_checkbutton.connect("toggled", self.AutoFileNameCheckButton_callback)
	self.wg.dataLogPower_button.connect("notify::active", self.DataLogPower_button_callback)
	self.wg.dataLogChooseFolder.connect("selection-changed", self.DataLogChooseFolder_callback)
	
	#Create timer to update system
	GObject.timeout_add_seconds(0.5, self.WindowUpdate)
	
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
	self.wg.ThermostatManualPower_button.set_active(self.thermo.Power)
	self.wg.ThermostatManualPower_button.props.visible = button.get_active()

    def ThermostatManualPower_button_callback(self, switch, gparam):
	self.thermo.Power = switch.get_active()
	self.thermo.PowerON()
	self.WindowUpdate()
	
    def ThermostatTempEntry_callback(self, widget, entry):
	tmpText = entry.get_text()
	if self.is_number(tmpText):
	    if (float(tmpText) >= 20 and float(tmpText) <= 150):
		self.thermo.SetTemperature(float(tmpText))
		
	self.wg.thermostatTempEntry.props.text = str(self.thermo.TemperatureSetPoint)
	self.WindowUpdate()
	    
    #Define callbacks for data logging module
    def DataLogPower_button_callback(self, switch, gparam):
	if (switch.get_active()):
	  self.dLogger.FileName = 'AgingTest_' + time.strftime("%Y%m%d_%H%M%S") + '.txt'
	  print self.dLogger.FileName
	self.dLogger.StartLogging = switch.get_active()
	
    def AutoFileNameCheckButton_callback(self, button):
	self.dLogger.AutoFileName = button.get_active()
	self.wg.dataLogFileNameEntry.props.visible = not button.get_active()
	
    def DataLogChooseFolder_callback(self, button):
	self.dLogger.SaveFolder =  self.wg.dataLogChooseFolder.get_filename()
	    
	  
    #Function to periodically update window
    def WindowUpdate(self):
	#Bath status
	self.agingBath.GetTemperature()
	self.wg.BathTemperatureLabel.props.label = self.agingBath.CurrentTemperature[0:4] + ' C'
	
	#Thermostat
	self.wg.thermostatTempLabel.props.label = str(self.thermo.ActualTemperature)
	self.wg.ThermostatManualPower_button.props.visible = self.thermo.ManualPower
	self.wg.ThermostatManualPower_button.props.state = self.thermo.Power
	if (self.thermo.Power):
	    self.wg.thermostatPowerStatus_label.props.label = 'ON'
	    self.wg.thermostatPowerStatus_label.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.0, 1.0, 0.0, 1.0))
	else:
	    self.wg.thermostatPowerStatus_label.props.label = 'OFF'
	    self.wg.thermostatPowerStatus_label.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(1.0, 0.0, 0.0, 1.0))
	self.wg.thermostatFaultStatus_label.props.label = self.thermo.StatusMessage    
	
	
	#Peristaltic pump
	self.wg.peristalticStateLabel.props.label = self.pPump.Status
	
	#Waste pump
	self.wg.wastePumpStateLabel.props.label = self.wPump.Status
	
	#Data logging
	self.wg.dataLogPower_button.set_active(self.dLogger.StartLogging)
	self.wg.dataLogFileNameEntry.props.visible = not self.dLogger.AutoFileName
	return True
    
    #Function to log data
    def LogData(self):
	if (self.dLogger.StartLogging):
	  tmpFileName = self.dLogger.SaveFolder + '/' + self.dLogger.FileName
	  tmpLogFile = open(tmpFileName, 'a+')
	  tmpLogFile.write(time.strftime("%Y%m%d_%H%M%S") + ' \t' + str(self.thermo.ActualTemperature[0:4]) + '\t' + str(self.agingBath.CurrentTemperature[0:4]) + '\n')
	  tmpLogFile.close()
	  
	return True

if __name__ == "__main__":
    try:
        win = AgingSystemControl()
	Gtk.main()
    except KeyboardInterrupt:
        pass

