# Setup the library ready for use
import Libraries.Thunderborg as ThunderBorg
import time


# Board #1, address 10
TB1 = ThunderBorg.ThunderBorg()
TB1.i2cAddress = 10
TB1.Init()
# TB1.ResetEpo()

# Board #2, address 11
TB2 = ThunderBorg.ThunderBorg()
TB2.i2cAddress = 0x15 
TB2.Init()
# TB2.ResetEpo()

TB1.SetMotor1(1)
time.sleep(1)
TB1.MotorsOff()
