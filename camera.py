import datetime
import time

import numpy as np

import pylibapogee.pylibapogee as apg
import pylibapogee.pylibapogee_setup as SetupDevice

class apogee_U2000():
  def __init__(self, camera_idx):
    self.cam = self._connect(camera_idx=camera_idx)
    
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
        
  def _connect(self, camera_idx=0):
     '''
       Connect to a USB camera.
     '''
     devices = SetupDevice.GetUsbDevices()
     if(len(devices) == 0):
       raise RuntimeError("No USB devices found")
    
     cam = SetupDevice.CreateAndConnectCam(devices[camera_idx])
       
     return cam

  def disconnect(self):
    '''
      Disconnect the camera from this instance.
    '''
    if self.cam == None:
      raise RuntimeError("No camera initialised")
    self.cam.CloseConnection()

  def getCoolerStatus(self):
    '''
      Get the current cooler status.
    '''
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
    
  def init(self, ROSpeed='normal', ADCGain=0, ADCOffset=0):
    '''
      Initialise common settings for a camera.
    '''
    self.setROSpeed(ROSpeed)
    self.setADCGain(ADCGain)
    self.setADCOffset(ADCOffset)    

  def setADCGain(self, gain=0):
    ''' 
      Set the gain for current ADC. Should be between 0 and 1023 
    '''
    if self.cam == None:
      raise RuntimeError("No camera initialised")
    if gain < 0 or gain > 1023:
      raise RuntimeError("Invalid gain setting")
    self.cam.SetAdcGain(gain, self.cam.GetCcdAdcSpeed(), 0)

  def setADCOffset(self, offset=0):
    ''' 
      Set the offset for current ADC. Should be between 0 and 255 
    '''
    if self.cam == None:
      raise RuntimeError("No camera initialised")
    if offset < 0 or offset > 255:
      raise RuntimeError("Invalid offset setting")
    self.cam.SetAdcOffset(offset, self.cam.GetCcdAdcSpeed(), 0)

  def setCooler(self, mode):
    ''' 
      Set the cooler on or off.
    '''
    if self.cam == None:
      raise RuntimeError("No camera initialised")
    self.cam.SetCooler(int(mode))
  
  def setCoolerSetPoint(self, sp):
    '''
      Set the cooler setpoint.
    '''
    if self.cam == None:
      raise RuntimeError("No camera initialised")
    self.cam.SetCoolerSetPoint(float(sp))
    
  def setROSpeed(self, speed='normal'):
    '''
      Set the readout speed. Can be 'normal' (16bit) or 'fast' (12bit) 
    '''
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


