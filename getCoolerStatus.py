from camera import apogee_U2000			

if __name__  == "__main__":
  c = apogee_U2000(camera_idx=0)
  c.getCoolerStatus()
  c.disconnect()
