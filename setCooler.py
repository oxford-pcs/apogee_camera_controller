import optparse

from camera import apogee_U2000			

if __name__  == "__main__":
  parser = optparse.OptionParser()
  group1 = optparse.OptionGroup(parser, "General")  
  group1.add_option('--s', action='store', default=1, dest='mode', help='set cooler on/off')

  args = parser.parse_args()
  options, args = parser.parse_args()

  try:
    mode = bool(options.mode)
  except TypeError:
    print "Set must be boolean"

  c = apogee_U2000(camera_idx=0)
  c.setCooler(mode)
  c.disconnect()
