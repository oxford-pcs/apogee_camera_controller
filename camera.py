import datetime
import time

import numpy as np

import pylibapogee.pylibapogee as apg
import pylibapogee.pylibapogee_setup as SetupDevice

class apogee_U2000():
  def __init__(self):
    self.cam = None

  def capture(self, exposureTime, reshape=True, override=False):
    if self.cam == None:
      raise RuntimeError("No camera initialised")
    if (not override and (exposureTime > self.cam.GetMaxExposureTime() or 
       exposureTime < self.cam.GetMinExposureTime())):
      raise RuntimeError("Exposure time selected violates camera's min/max " + 
                         "recommended exposure times.")


    expDatetime = datetime.datetime.now()
    self.cam.StartExposure(exposureTime, True)              
    status = None
    while status != apg.Status_ImageReady:
      status = self.cam.GetImagingStatus()	
      if(status == apg.Status_ConnectionError or
         status == apg.Status_DataError or
         status == apg.Status_PatternError):

        msg = "Capture failed. Error in camera status = %d" % (status)
        raise RuntimeError(msg)

    start = time.time()
    data = self.cam.GetImage()
    pixel_readout_rate = 1/((time.time() - start)/len(data))

    if reshape:
      data = np.reshape(data, (self.cam.GetMaxImgCols(), self.cam.GetMaxImgRows()))

    attr = {}
    attr['CCDTEMP0'] = (float(self.cam.GetTempCcd()), "CCD temperature (deg)")
    attr['CCDTEMP1'] = (float(self.cam.GetTempHeatsink()), "heatsink temperature (deg)")
    if self.cam.GetCcdAdcResolution() == apg.Resolution_TwelveBit:
      attr['ADCBITS'] = (12, "resolution of ADC (bits)")
    elif self.cam.GetCcdAdcResolution() == apg.Resolution_SixteenBit:
      attr['ADCBITS'] = (16, "resolution of ADC (bits)")
    attr['SETPOINT'] = (float(self.cam.GetCoolerSetPoint()), "cooler setpoint (deg)")
    attr['COOLPOW'] = (float(self.cam.GetCoolerDrive()), "cooler power (%)")
    if self.cam.GetCoolerStatus() == apg.CoolerStatus_Off:
      attr['COOLSTAT'] = ("OFF", "cooler status flag")
    elif self.cam.GetCoolerStatus() == apg.CoolerStatus_RampingToSetPoint:
      attr['COOLSTAT'] = ("RAMPING", "cooler status flag")
    elif self.cam.GetCoolerStatus() == apg.CoolerStatus_AtSetPoint:
      attr['COOLSTAT'] = ("AT_SETPOINT", "cooler status flag")
    elif self.cam.GetCoolerStatus() == apg.CoolerStatus_Revision:
      attr['COOLSTAT'] = ("WAITING", "cooler status flag")
    if self.cam.GetFanMode() == apg.FanMode_Off:
      attr['FANMODE'] = ("OFF", "fan status flag")
    elif self.cam.GetFanMode() == apg.FanMode_Low:
      attr['FANMODE'] = ("LOW", "fan status flag")
    elif self.cam.GetFanMode() == apg.FanMode_Medium:
      attr['FANMODE'] = ("MEDIUM", "fan status flag")
    elif self.cam.GetFanMode() == apg.FanMode_High:
      attr['FANMODE'] = ("HIGH", "fan status flag")
    attr['ADGAIN'] = (float(self.cam.GetAdcGain(self.cam.GetCcdAdcSpeed(), 0)), 
                      "ADC gain")
    attr['ADOFFSET'] = (float(self.cam.GetAdcOffset(self.cam.GetCcdAdcSpeed(), 0)),
                      "ADC offset")
    attr['DATETIME'] = (str(expDatetime), "frame datetime")
    attr['READOUTS'] = (float(int(round(pixel_readout_rate))), "pixel readout rate (Hz)")
    attr['EXPTIME'] = (float(exposureTime), "exposure time (s)")

    return data, attr

  def close(self):
    if self.cam == None:
      raise RuntimeError("No camera initialised")
    self.cam.CloseConnection()
        
  def connect(self, camera_idx=0, init=False):
     devices = SetupDevice.GetUsbDevices()
     if(len(devices) == 0):
       raise RuntimeError("No USB devices found")
    
     self.cam = SetupDevice.CreateAndConnectCam(devices[camera_idx])

     if init:
       self.setROSpeed('normal')
       self.setADCGain(0)
       self.setADCOffset(0)

  def getCoolerStatus(self):
    if self.cam.GetCoolerStatus() == apg.CoolerStatus_Off:
      status = "OFF"
    elif self.cam.GetCoolerStatus() == apg.CoolerStatus_RampingToSetPoint:
      status = "RAMPING"
    elif self.cam.GetCoolerStatus() == apg.CoolerStatus_AtSetPoint:
      status = "AT_SETPOINT"
    elif self.cam.GetCoolerStatus() == apg.CoolerStatus_Revision:
      status = "WAITING"

    print "CCD temp:\t" + str(self.cam.GetTempCcd())
    print "setpoint:\t" + str(self.cam.GetCoolerSetPoint())
    print "status:\t\t" + status

  def setADCGain(self, gain=0):
    ''' Sets gain for current ADC. Should be between 0 and 1023 '''
    if self.cam == None:
      raise RuntimeError("No camera initialised")
    if gain < 0 or gain > 1023:
      raise RuntimeError("Invalid gain setting")
    self.cam.SetAdcGain(gain, self.cam.GetCcdAdcSpeed(), 0)

  def setADCOffset(self, offset=0):
    ''' Sets offset for current ADC. Should be between 0 and 255 '''
    if self.cam == None:
      raise RuntimeError("No camera initialised")
    if offset < 0 or offset > 255:
      raise RuntimeError("Invalid offset setting")
    self.cam.SetAdcOffset(offset, self.cam.GetCcdAdcSpeed(), 0)

  def setROSpeed(self, speed='normal'):
    ''' Set the readout speed, can be 'normal' (16bit) or 'fast' (12bit) '''
    if self.cam == None:
      raise RuntimeError("No camera initialised")
    if speed == 'normal':
      self.cam.SetCcdAdcSpeed(apg.AdcSpeed_Normal)
      print "Set readout speed to normal"
    elif speed == 'fast':
      self.cam.SetCcdAdcSpeed(apg.AdcSpeed_Fast)
      print "Set readout speed to fast"
    else:
      raise RuntimeError("Readout speed value not recognised")

  def setCoolerSetPoint(self, setpoint):
    if self.cam == None:
      raise RuntimeError("No camera initialised")
    self.cam.SetCoolerSetPoint(float(setpoint))
  




