import optparse

from camera import apogee_U2000			

if __name__  == "__main__":
  parser = optparse.OptionParser()
  group1 = optparse.OptionGroup(parser, "General")  
  group1.add_option('--sp', action='store', default='', dest='setPoint', help='set point (deg)')

  args = parser.parse_args()
  options, args = parser.parse_args()

  try:
    float(options.setPoint)
  except TypeError:
    print "Set point must be a number."

  c = apogee_U2000()
  c.connect()
  c.setCoolerSetPoint(options.setPoint)
  c.close()
