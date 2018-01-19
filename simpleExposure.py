import optparse

import pyfits

from camera import apogee_U2000			

if __name__  == "__main__":
  parser = optparse.OptionParser()
  group1 = optparse.OptionGroup(parser, "General")  
  group1.add_option('--t', action='store', default=0.001, dest='expT', help='exposure time (s)')

  args = parser.parse_args()
  options, args = parser.parse_args()

  try:
    expT = float(options.expT)
  except TypeError:
    print "Set point must be a number."
    
  print options.expT

  c = apogee_U2000(camera_idx=0)
  c.init()
  data, attr = c.capture(expT)
  pyfits.writeto("test.fits", data)
  c.disconnect()
