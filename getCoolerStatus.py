from camera import apogee_U2000			

if __name__  == "__main__":
  c = apogee_U2000()
  c.connect()
  c.getCoolerStatus()
  c.close()
