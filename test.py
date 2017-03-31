import pyfits

from camera import apogee_U2000	

if __name__ == "__main__":
  c = apogee_U2000()
  c.connect()
  data, attr = c.capture(1)
  pyfits.writeto("test.fits", data)
  c.close()
