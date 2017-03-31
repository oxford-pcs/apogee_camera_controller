import optparse

import numpy as np
import pyfits

from camera import apogee_U2000				

if __name__  == "__main__":
  parser = optparse.OptionParser()
  group1 = optparse.OptionGroup(parser, "General")  
  group1.add_option('--mi', action='store', default=0.002, dest='minExp', help='min exposure (s)')
  group1.add_option('--ma', action='store', default=100, dest='maxExp', help='min exposure (s)')

  args = parser.parse_args()
  options, args = parser.parse_args()
 
  try:
    minExp = float(options.minExp)
    maxExp = float(options.maxExp)
  except TypeError:
    print "Need to specify numeric minimum and maximum exposure time."

  c = apogee_U2000()
  c.connect(init=True)

  # get approximate bias level, rate and corresponding ADUs for the minimum and maximum 
  # exposure times inputted
  # 
  data, attr = c.capture(0.0, override=True)
  bias = np.percentile(data, 99.5)
  data, attr = c.capture(1.0)
  one_second = np.mean(data)

  rate = one_second-bias

  print "At minimum exposure time of " + str(minExp) + "s, number of ADUs will " \
        "be ~" + str(rate*minExp) + "."

  print "At maximum exposure time of " + str(maxExp) + "s, number of ADUs will " \
        "be ~" + str(rate*maxExp) + "."

  print "If full well is determined by the ADC (" + str(attr['ADCBITS'][0]) + "bit), there" + \
        "are " + str(2**float(round(int(attr['ADCBITS'][0])))) + " bits available for digitisation."

  for r in [0.002, 0.004, 0.008, 0.016, 0.032, 0.064, 0.128, 0.256, 0.512, 1.024]:
    for i in [0, 1]:
      data, attr = c.capture(r)

      h = pyfits.Header()
      for k, v in attr.iteritems():
        h.append((k, v[0], v[1]))

      pyfits.writeto("f_" + str(r) + "_" + str(i) + ".fits", data, header=h)

  for r in [2, 4, 6, 8, 10, 20, 30, 40, 50]:
    for i in [0, 1]:
      data, attr = c.capture(r)

      h = pyfits.Header()
      for k, v in attr.iteritems():
        h.append((k, v[0], v[1]))

      pyfits.writeto("f_" + str(r) + "_" + str(i) + ".fits", data, header=h)


  for r in [55, 58, 61, 64, 67]:
    for i in [0, 1]:
      data, attr = c.capture(r)

      h = pyfits.Header()
      for k, v in attr.iteritems():
        h.append((k, v[0], v[1]))

      pyfits.writeto("f_" + str(r) + "_" + str(i) + ".fits", data, header=h)

  c.close()

